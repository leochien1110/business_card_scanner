import requests
import json
import config


def call_ai_api(prompt, image_b64=None):
    """Call AI API with image and prompt"""
    api_type = config.current_config.get("type", "ollama")
    
    if api_type == "openai":
        return call_openai_api(prompt, image_b64)
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


def call_openai_api(prompt, image_b64=None):
    """Call OpenAI-compatible API (like Gemini)"""
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
    
    try:
        resp = requests.post(config.current_config["url"], headers=headers, json=payload, timeout=300)
        if resp.status_code == 200:
            response_data = resp.json()
            
            # Extract token usage if available
            token_usage = None
            if "usage" in response_data:
                usage = response_data["usage"]
                token_usage = {
                    "input": usage.get("prompt_tokens", 0),
                    "output": usage.get("completion_tokens", 0)
                }
            
            return response_data["choices"][0]["message"]["content"], token_usage
        else:
            raise Exception(f"OpenAI API error: {resp.status_code}")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


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
            payload = {
                "model": config.current_config["model"],
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            resp = requests.post(config.current_config["url"], headers=headers, json=payload, timeout=10)
        else:
            test_url = config.current_config["url"].replace('/api/generate', '/api/tags')
            resp = requests.get(test_url, timeout=5)
        
        if resp.status_code == 200:
            return "🟢 Connected"
        else:
            return "🔴 Failed"
            
    except Exception:
        return "🔴 Error"





 