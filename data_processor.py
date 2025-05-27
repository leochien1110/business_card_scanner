import base64
import json
import uuid
import tempfile
import pathlib
import time
import pandas as pd
import gradio as gr

from config import PROMPT, SERVERS, POST_PROCESSING_PROMPT
from image_utils import resize_image
from api_client import call_ai_api, test_connection, call_post_processing_api
import config


def extract_from_image(file_path, use_raw_images=False):
    """Extract data from a single business card image (without post-processing)"""
    try:
        # Process image
        image_data = resize_image(file_path, use_raw=use_raw_images)
        b64 = base64.b64encode(image_data).decode()
        
        # Call AI API
        raw_response, token_usage = call_ai_api(PROMPT, b64)
        
        # Clean response
        response = raw_response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        # Extract JSON
        if '{' in response and '}' in response:
            start = response.find('{')
            end = response.rfind('}') + 1
            response = response[start:end]
        
        # Parse JSON
        data = json.loads(response)
        
        # Ensure all required fields exist
        result = {
            "name": data.get("name", ""),
            "company": data.get("company", ""),
            "title": data.get("title", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "address": data.get("address", ""),
            "handwriting_notes": data.get("handwriting_notes", ""),
            "other": data.get("other", "")
        }
        
        return result, token_usage
        
    except Exception as e:
        error_result = {
            "name": f"Error processing {pathlib.Path(file_path).name}",
            "company": "",
            "title": "",
            "phone": "",
            "email": "",
            "address": "",
            "handwriting_notes": "",
            "other": str(e)
        }
        return error_result, None


def post_process_batch(results):
    """Post-process entire batch of extracted data with smart chunking"""
    try:
        # Smart chunking based on API limits
        # Gemini 2.5 Flash Preview limits: 250K TPM, 65K output tokens
        max_cards_per_chunk = 15  # Conservative: ~20K output tokens per chunk
        
        if len(results) > max_cards_per_chunk:
            print(f"📦 Large batch detected ({len(results)} cards) - processing in chunks of {max_cards_per_chunk} with contextual learning")
            processed_results = []
            total_tokens = {"input": 0, "output": 0}
            
            for i in range(0, len(results), max_cards_per_chunk):
                chunk = results[i:i+max_cards_per_chunk]
                chunk_start = i + 1
                chunk_end = min(i + max_cards_per_chunk, len(results))
                print(f"🔄 Processing chunk {chunk_start}-{chunk_end} ({len(chunk)} cards) with context from {len(processed_results)} previous cards...")
                
                # Pass previous results as context for consistency
                chunk_result, chunk_tokens = post_process_single_batch_with_context(chunk, processed_results)
                processed_results.extend(chunk_result)
                
                # Show token usage for this chunk
                if chunk_tokens:
                    total_tokens["input"] += chunk_tokens["input"]
                    total_tokens["output"] += chunk_tokens["output"]
                    if "thinking" in chunk_tokens:
                        if "thinking" not in total_tokens:
                            total_tokens["thinking"] = 0
                        total_tokens["thinking"] += chunk_tokens["thinking"]
                    
                    # Display thinking tokens if available (Gemini 2.5 Flash with thinking)
                    thinking_tokens = chunk_tokens.get("thinking", 0)
                    if thinking_tokens > 0:
                        print(f"   🧠 Chunk {chunk_start}-{chunk_end} tokens: {chunk_tokens['input']:,} input + {thinking_tokens:,} thinking + {chunk_tokens['output']:,} output = {chunk_tokens['input'] + thinking_tokens + chunk_tokens['output']:,} total")
                    else:
                        print(f"   🎯 Chunk {chunk_start}-{chunk_end} tokens: {chunk_tokens['input']:,} input + {chunk_tokens['output']:,} output = {chunk_tokens['input'] + chunk_tokens['output']:,} total")
                    
                    # Running total
                    running_total = total_tokens['input'] + total_tokens['output'] + total_tokens.get('thinking', 0)
                    print(f"   📊 Running total: {running_total:,} tokens")
                else:
                    print(f"   ⚠️ Chunk {chunk_start}-{chunk_end}: token usage not available")
                
                # Small delay between chunks to respect rate limits
                time.sleep(1)
            
            print(f"✅ All chunks completed - processed {len(processed_results)} cards total with full context learning")
            return processed_results, total_tokens
        else:
            # Single batch processing
            return post_process_single_batch(results)
        
    except Exception as e:
        print(f"❌ Batch processing failed: {str(e)}")
        return results, None


def post_process_single_batch(results):
    """Post-process a single batch of extracted data (without context)"""
    return post_process_single_batch_with_context(results, [])


def post_process_single_batch_with_context(results, previous_results):
    """Post-process a single batch of extracted data with context from previous chunks"""
    try:
        # Build context section if we have previous results
        context_section = ""
        if previous_results:
            # Limit context to avoid token overflow - show recent examples
            context_sample = previous_results[-30:] if len(previous_results) > 30 else previous_results
            context_section = f"""

CONTEXT FROM PREVIOUS CARDS (for consistency):
Previously standardized {len(previous_results)} cards. Recent examples:
{json.dumps(context_sample, indent=2)}

IMPORTANT: Maintain consistency with the patterns established above:
- Use the same phone number format style (e.g. +1-555-123-4567)
- Use the same company name variations (e.g., if "ABC Corp" was used before, don't use "ABC Corporation")
- Use the same address formatting style
- Use the same job title standardizations
"""

        batch_prompt = f"""
You are a data quality expert. Please standardize and validate the following batch of business card data to ensure consistency and proper formatting.
{context_section}

CURRENT BATCH TO STANDARDIZE:
Total cards in this batch: {len(results)}
Data: {json.dumps(results, indent=2)}

Please return a JSON array with the same number of objects, each with standardized formatting:

Rules for standardization:
1. Phone numbers: Format as international standard (e.g., +1-555-123-4567) or local standard if country unclear
2. Email: Ensure proper email format (lowercase domain)
3. Address: Clean and standardize address format (but preserve multilingual text like "123 Main St / 主要街道123号")
4. Name: Proper capitalization, remove extra spaces BUT PRESERVE multilingual format (e.g., "John Smith / 約翰・スミス")
5. Company: Proper business name formatting BUT PRESERVE multilingual format (e.g., "ABC Corp / ABC株式会社") (maintain consistency with previous cards)
6. Title: Standardize job titles (e.g., "CEO" not "C.E.O.") BUT PRESERVE multilingual format (e.g., "CEO / 最高経営責任者")
7. Keep handwriting_notes as extracted
8. Other: Clean URLs, social media handles, etc. BUT PRESERVE multilingual text

Return only a valid JSON array with the same structure, no comments or markdown.
"""
        
        print(f"🔄 Starting batch post-processing for {len(results)} cards...")
        post_processed_response, token_usage = call_post_processing_api(batch_prompt)
        
        # Clean response
        response = post_processed_response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        # Parse JSON array
        post_processed_data = json.loads(response)
        
        # Ensure it's a list and has the same length
        if isinstance(post_processed_data, list) and len(post_processed_data) == len(results):
            print(f"✅ Post-processing completed successfully - standardized {len(post_processed_data)} cards")
            print("📊 Post-processing applied: phone formatting, email validation, name capitalization, address formatting")
            return post_processed_data, token_usage
        else:
            print(f"⚠️ Post-processing returned {len(post_processed_data)} items instead of {len(results)} - using original data")
            return results, token_usage
        
    except Exception as e:
        print(f"❌ Post-processing failed: {str(e)}")
        print("📝 Using original extracted data without post-processing")
        return results, None


def extract(files, custom_filename, use_raw_images, vision_model, progress=gr.Progress()):
    """Extract data from all uploaded files"""
    config.processing_stopped = False
    start_time = time.time()
    
    if not files:
        return pd.DataFrame(), None, gr.update(interactive=True), gr.update(interactive=False), ""
    
    # Update current config based on selected model
    if vision_model in SERVERS:
        config.current_config = SERVERS[vision_model]
    
    # Process all files - extraction only
    model_info = f"{config.current_config['model']} ({config.current_config['type']})"
    print(f"🔍 Phase 1: Extracting data from {len(files)} business cards...")
    print(f"📱 Using model: {model_info}")
    
    results = []
    total_extraction_tokens = {"input": 0, "output": 0}
    
    for i, file_path in enumerate(files):
        if config.processing_stopped:
            break
            
        progress((i, len(files)), desc=f"Extracting {i+1}/{len(files)}")
        result, token_usage = extract_from_image(file_path, use_raw_images)
        results.append(result)
        
        # Accumulate token usage if available
        if token_usage:
            total_extraction_tokens["input"] += token_usage.get("input", 0)
            total_extraction_tokens["output"] += token_usage.get("output", 0)
    
    if not config.processing_stopped:
        print(f"✅ Extraction completed - processed {len(results)} cards")
        if total_extraction_tokens["input"] > 0 or total_extraction_tokens["output"] > 0:
            print(f"🎯 Extraction tokens: {total_extraction_tokens['input']:,} input + {total_extraction_tokens['output']:,} output = {total_extraction_tokens['input'] + total_extraction_tokens['output']:,} total")
        else:
            print("🎯 Token usage not available for this model type")
    
    # Run batch post-processing if not stopped
    if not config.processing_stopped and results:
        post_model_info = f"{config.POST_PROCESSING_CONFIG['model']} ({config.POST_PROCESSING_CONFIG['type']})"
        print(f"\n🔬 Phase 2: Post-processing batch of {len(results)} cards for data standardization...")
        print(f"📱 Using model: {post_model_info}")
        progress((1, 1), desc="Post-processing batch data...")
        results, post_processing_tokens = post_process_batch(results)
        print("✨ Post-processing phase completed")
        
        # Show post-processing token usage
        if post_processing_tokens:
            thinking_total = post_processing_tokens.get('thinking', 0)
            if thinking_total > 0:
                print(f"🎯 Post-processing tokens: {post_processing_tokens['input']:,} input + {thinking_total:,} thinking + {post_processing_tokens['output']:,} output = {post_processing_tokens['input'] + thinking_total + post_processing_tokens['output']:,} total")
            else:
                print(f"🎯 Post-processing tokens: {post_processing_tokens['input']:,} input + {post_processing_tokens['output']:,} output = {post_processing_tokens['input'] + post_processing_tokens['output']:,} total")
        else:
            print("🎯 Post-processing token usage not available")
            
        # Show total token usage including thinking tokens
        extraction_total = total_extraction_tokens['input'] + total_extraction_tokens['output']
        if post_processing_tokens:
            post_total = post_processing_tokens['input'] + post_processing_tokens['output'] + post_processing_tokens.get('thinking', 0)
        else:
            post_total = 0
        
        total_tokens = extraction_total + post_total
        if total_tokens > 0:
            print(f"💰 Total session tokens: {total_tokens:,}")
            if post_processing_tokens and post_processing_tokens.get('thinking', 0) > 0:
                print(f"🧠 Including thinking tokens: {post_processing_tokens.get('thinking', 0):,}")
        print()
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save to CSV
    filename = custom_filename.strip() if custom_filename and custom_filename.strip() else f"cards_{uuid.uuid4().hex}"
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    tmp = pathlib.Path(tempfile.gettempdir()) / filename
    df.to_csv(tmp, index=False, encoding='utf-8-sig')
    
    # Calculate processing time
    processing_time = time.time() - start_time
    if processing_time < 60:
        time_str = f"⏱️ Completed in {processing_time:.1f} seconds"
    else:
        minutes = int(processing_time // 60)
        seconds = processing_time % 60
        time_str = f"⏱️ Completed in {minutes}m {seconds:.1f}s"
    
    if config.processing_stopped:
        time_str = f"⏹️ Stopped after {processing_time:.1f} seconds"
    
    return df, str(tmp), gr.update(interactive=True), gr.update(interactive=False), time_str


def update_model(selected_model):
    """Update the current model configuration"""
    if selected_model in SERVERS:
        config.current_config = SERVERS[selected_model]
        return test_connection()
    return "🔴 Model not found"


def stop_processing():
    """Stop the current processing"""
    config.processing_stopped = True
    return gr.update(interactive=False), gr.update(interactive=True) 