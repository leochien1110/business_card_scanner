import requests
import json
import config


def call_ai_api(prompt, image_b64=None):
    """Call AI API with image and prompt"""
    api_type = config.current_config.get("type", "ollama")
    
    if api_type == "openai":
        return call_openai_api(prompt, image_b64)
    elif api_type == "gemini":
        return call_gemini_native_api(prompt, image_b64)
    else:
        return call_ollama_api(prompt, image_b64)


def call_ollama_api(prompt, image_b64=None):
    """Call Ollama API"""
    payload = {
        "model": config.current_config["model"],
        "prompt": prompt,
        "stream": False,
    }
    
    if image_b64:
        payload["images"] = [image_b64]
    
    try:
        resp = requests.post(config.current_config["url"], json=payload, timeout=300)
        if resp.status_code == 200:
            response_data = resp.json()
            
            # Extract token usage if available
            token_usage = None
            if "prompt_eval_count" in response_data and "eval_count" in response_data:
                token_usage = {
                    "input": response_data.get("prompt_eval_count", 0),
                    "output": response_data.get("eval_count", 0)
                }
            
            return response_data["response"], token_usage
        else:
            raise Exception(f"Ollama API error: {resp.status_code}")
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")


def call_openai_api(prompt, image_b64=None, max_retries=3):
    """Call OpenAI-compatible API (like Gemini) with retry logic"""
    headers = {
        "Authorization": f"Bearer {config.current_config.get('api_key', '')}",
        "Content-Type": "application/json"
    }
    
    content = prompt
    if image_b64:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    
    payload = {
        "model": config.current_config["model"],
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 1000
    }
    
    # Special handling for Gemini 2.5 Flash Preview models
    if "2.5" in config.current_config["model"] and "preview" in config.current_config["model"]:
        # Gemini 2.5 Flash Preview might need specific parameters
        payload["max_tokens"] = 2048  # Increase token limit
        # Some preview models might benefit from explicit temperature setting
        payload["temperature"] = 0.1
    
    import time
    
    for attempt in range(max_retries):
        try:
            resp = requests.post(config.current_config["url"], headers=headers, json=payload, timeout=300)
            if resp.status_code == 200:
                response_data = resp.json()
                
                # Debug logging for Gemini 2.5 Flash Preview issues (can be removed after confirmation)
                # if "2.5" in config.current_config["model"] and "preview" in config.current_config["model"]:
                #     print(f"🔍 Debug - Full response for {config.current_config['model']}: {response_data}")
                
                # Better error handling for response structure
                if "choices" not in response_data:
                    raise Exception(f"No 'choices' in response: {response_data}")
                
                if len(response_data["choices"]) == 0:
                    raise Exception(f"Empty choices array: {response_data}")
                
                choice = response_data["choices"][0]
                if "message" not in choice:
                    raise Exception(f"No 'message' in choice: {choice}")
                
                message = choice["message"]
                
                # Check if message only has role but no content (completely empty response)
                if len(message) == 1 and "role" in message and message["role"] == "assistant":
                    empty_response_error = "API returned empty assistant message with no content - this may indicate rate limiting, API issues, or content filtering"
                    if attempt < max_retries - 1:
                        print(f"⚠️ {empty_response_error}. Retrying in {2 ** attempt} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise Exception(empty_response_error)
                
                if "content" not in message:
                    # Some APIs might return content in different format
                    if "text" in message:
                        content_text = message["text"]
                    elif "parts" in message and len(message["parts"]) > 0:
                        content_text = message["parts"][0].get("text", "")
                    else:
                        content_error = f"No 'content' or alternative in message: {message}"
                        if attempt < max_retries - 1:
                            print(f"⚠️ {content_error}. Retrying in {2 ** attempt} seconds... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            raise Exception(content_error)
                else:
                    content_text = message["content"]
                
                # Handle empty or None content
                if content_text is None or content_text == "":
                    empty_content_error = "API returned null or empty content - this may indicate rate limiting, API issues, or content filtering"
                    if attempt < max_retries - 1:
                        print(f"⚠️ {empty_content_error}. Retrying in {2 ** attempt} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise Exception(empty_content_error)
                
                # Extract token usage if available
                token_usage = None
                if "usage" in response_data:
                    usage = response_data["usage"]
                    token_usage = {
                        "input": usage.get("prompt_tokens", 0),
                        "output": usage.get("completion_tokens", 0)
                    }
                
                return content_text, token_usage
            elif resp.status_code == 429:  # Rate limiting
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️ Rate limited (429). Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Rate limited (429) - max retries exceeded")
            else:
                raise Exception(f"OpenAI API error: {resp.status_code} - {resp.text}")
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ JSON decode error: {str(e)}. Retrying in {2 ** attempt} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"JSON decode error in OpenAI API: {str(e)}")
        except Exception as e:
            if "rate limiting" in str(e).lower() or "empty assistant message" in str(e) or "429" in str(e):
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️ API issue: {str(e)}. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
            raise Exception(f"OpenAI API error: {str(e)}")


def call_gemini_native_api(prompt, image_b64=None):
    """Call native Gemini API (not OpenAI compatibility)"""
    url = f"{config.current_config['url']}?key={config.current_config.get('api_key', '')}"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Build the content parts
    parts = [{"text": prompt}]
    if image_b64:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_b64
            }
        })
    
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 2048,
            "temperature": 0.1
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=300)
        if resp.status_code == 200:
            response_data = resp.json()
            
            # Debug logging
            print(f"🔍 Native Gemini API response: {response_data}")
            
            # Handle Gemini API response structure
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                
                # Check for truncation due to max tokens
                if candidate.get("finishReason") == "MAX_TOKENS":
                    raise Exception("Response truncated due to token limit")
                
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        # Extract token usage if available
                        token_usage = None
                        if "usageMetadata" in response_data:
                            usage = response_data["usageMetadata"]
                            token_usage = {
                                "input": usage.get("promptTokenCount", 0),
                                "output": usage.get("candidatesTokenCount", 0)
                            }
                        
                        return parts[0]["text"], token_usage
                    else:
                        raise Exception(f"No text in parts: {parts}")
                else:
                    raise Exception(f"Unexpected candidate structure: {candidate}")
            else:
                raise Exception(f"Unexpected response structure: {response_data}")
        else:
            raise Exception(f"Native Gemini API error: {resp.status_code} - {resp.text}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decode error in native Gemini API: {str(e)}")
    except Exception as e:
        raise Exception(f"Native Gemini API error: {str(e)}")


def call_post_processing_api(prompt):
    """Call Gemini 2.5 Flash Preview for post-processing using native Gemini API"""
    # Use the native Gemini API format
    url = f"{config.POST_PROCESSING_CONFIG['url']}?key={config.POST_PROCESSING_CONFIG.get('api_key', '')}"
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.1,
            "thinkingConfig": {
                "thinkingBudget": 2048
            }
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=300)
        if resp.status_code == 200:
            response_data = resp.json()
            
            # Handle Gemini API response structure
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                
                # Check for truncation due to max tokens
                if candidate.get("finishReason") == "MAX_TOKENS":
                    raise Exception("Response truncated due to token limit - try processing fewer cards at once")
                
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        # Extract token usage if available
                        token_usage = None
                        if "usageMetadata" in response_data:
                            usage = response_data["usageMetadata"]
                            token_usage = {
                                "input": usage.get("promptTokenCount", 0),
                                "output": usage.get("candidatesTokenCount", 0),
                                "thinking": usage.get("thoughtsTokenCount", 0)
                            }
                        
                        return parts[0]["text"], token_usage
                    else:
                        raise Exception(f"No text in parts: {parts}")
                else:
                    raise Exception(f"Unexpected candidate structure: {candidate}")
            else:
                raise Exception(f"Unexpected response structure: {response_data}")
        else:
            raise Exception(f"Post-processing API error: {resp.status_code} - {resp.text}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decode error in post-processing: {str(e)}")
    except Exception as e:
        raise Exception(f"Post-processing API error: {str(e)}")


def test_connection():
    """Test connection to current AI server"""
    try:
        api_type = config.current_config.get("type", "ollama")
        
        if api_type == "openai":
            headers = {
                "Authorization": f"Bearer {config.current_config.get('api_key', '')}",
                "Content-Type": "application/json"
            }
            # Use more tokens for preview models that need more space to generate responses
            max_tokens = 50
            if "preview" in config.current_config["model"] or "2.5" in config.current_config["model"]:
                max_tokens = 100
                
            payload = {
                "model": config.current_config["model"],
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": max_tokens
            }
            resp = requests.post(config.current_config["url"], headers=headers, json=payload, timeout=10)
            
            # Enhanced debugging for Gemini 2.5 Flash Preview
            if resp.status_code == 200:
                try:
                    response_data = resp.json()
                    # if "2.5" in config.current_config["model"] and "preview" in config.current_config["model"]:
                    #     print(f"🔍 Test connection response for {config.current_config['model']}: {response_data}")
                    
                    # Check if we get a valid response structure
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        choice = response_data["choices"][0]
                        if "message" in choice:
                            message = choice["message"]
                            if len(message) == 1 and "role" in message and message["role"] == "assistant":
                                return f"🟡 Connected but getting empty responses from {config.current_config['model']}"
                            elif "content" in message and message["content"]:
                                return "🟢 Connected"
                            else:
                                return f"🟡 Connected but content format unexpected: {message}"
                        else:
                            return f"🟡 Connected but no message in choice: {choice}"
                    else:
                        return f"🟡 Connected but unexpected response structure: {response_data}"
                except Exception as e:
                    return f"🟡 Connected but response parsing failed: {str(e)}"
            else:
                return f"🔴 Failed ({resp.status_code}) - {resp.text[:100]}"
        else:
            test_url = config.current_config["url"].replace('/api/generate', '/api/tags')
            resp = requests.get(test_url, timeout=5)
            
            if resp.status_code == 200:
                return "🟢 Connected"
            else:
                return f"🔴 Failed ({resp.status_code})"
            
    except Exception as e:
        return f"🔴 Error: {str(e)[:50]}..."





 