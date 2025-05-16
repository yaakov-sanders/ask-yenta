import json
from typing import Dict, Any

import requests

# Configuration for Ollama API
OLLAMA_API_HOST = "host.docker.internal"  # Use localhost for local development, host.docker.internal for Docker
OLLAMA_API_PORT = 11434
OLLAMA_API_URL = f"http://{OLLAMA_API_HOST}:{OLLAMA_API_PORT}/api/generate"


def parse_profile_from_text(text: str) -> Dict[str, Any]:
    """
    Sends a POST request to the Ollama API to parse free-form user text into structured JSON.
    Uses model: llama3:latest, stream: false
    
    Args:
        text: The free-form text from the user
        
    Returns:
        Parsed JSON object with relevant user profile fields
        
    Raises:
        Exception: If the API call fails or the response cannot be parsed as JSON
    """
    prompt = f"""
    You are AskYenta, an assistant that extracts a structured JSON user profile from free-form text. 
    Return only a JSON object with relevant fields the user mentioned (like interests, personality, goals, work, values, etc.). 
    Do not add any keys the user did not mention. Do not include commentary.
    
    Text: {text}
    """
    
    payload = {
        "model": "llama3.2:latest",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        response_text = result.get("response", "{}")
        
        # Extract JSON from response
        # We need to handle the case where the LLM outputs additional text before/after the JSON
        try:
            # Try to parse directly first
            parsed_json = json.loads(response_text)
            return parsed_json
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from the string
            # Look for the first '{' and the last '}'
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # If still can't parse, return empty dict
                    return {}
            return {}
    except requests.RequestException as e:
        # Handle API request errors
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        # Handle general errors
        raise Exception(f"Error processing LLM response: {str(e)}")


def send_direct_prompt(prompt: str, model: str = "llama3.2:latest") -> str:
    """
    Sends a direct prompt to the LLM and returns the raw response.
    
    Args:
        prompt: The prompt to send to the LLM
        model: The model to use, defaults to llama3:latest
        
    Returns:
        The raw text response from the LLM
        
    Raises:
        Exception: If the API call fails
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        return result.get("response", "")
    except requests.RequestException as e:
        # Handle API request errors
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        # Handle general errors
        raise Exception(f"Error processing LLM response: {str(e)}")

    