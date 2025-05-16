import json
import logging
from typing import Any

import requests

# Set up logger
logger = logging.getLogger(__name__)

# Configuration for Ollama API
OLLAMA_API_HOST = "host.docker.internal"  # Use localhost for local development, host.docker.internal for Docker
OLLAMA_API_PORT = 11434
OLLAMA_API_URL_GENERATE = f"http://{OLLAMA_API_HOST}:{OLLAMA_API_PORT}/api/generate"
OLLAMA_API_URL_CHAT = f"http://{OLLAMA_API_HOST}:{OLLAMA_API_PORT}/api/chat"
DEFAULT_MODEL = "llama3.2:latest"


def parse_profile_from_text(text: str) -> dict[str, Any]:
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
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL_GENERATE, json=payload)
        response.raise_for_status()

        # Log the raw response for debugging
        logger.info(f"API response status: {response.status_code}")
        logger.info(f"Raw API response content: {response.content[:1000]}")  # First 1000 chars

        # Parse the response
        try:
            result = response.json()
            logger.info(f"Successfully parsed API response: {result}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response as JSON: {str(e)}")
            logger.error(f"Response content: {response.content.decode('utf-8', errors='replace')}")
            raise Exception(f"Invalid JSON response from Ollama API: {str(e)}")

        response_text = result.get("response", "{}")

        # Log the extracted text
        logger.info(f"Extracted response text: {response_text[:1000]}")  # First 1000 chars

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
        logger.error(f"API request error: {str(e)}", exc_info=True)
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
        raise Exception(f"Error processing LLM response: {str(e)}")


def chat_with_memory(
    user_message: str,
    summary: str,
    conversation_history: list[dict[str, str]]
) -> tuple[str, str]:
    """
    Sends a chat request to the Ollama API with memory (summary + recent messages).

    Args:
        user_message: The new message from the user
        summary: The current summary of the conversation
        conversation_history: List of previous messages as {"role": "user|assistant", "content": "..."}

    Returns:
        Tuple of (assistant_reply, updated_summary)

    Raises:
        Exception: If the API call fails or the response cannot be parsed
    """
    # Prepare message history
    messages = []

    # Add system message with user summary and strict JSON format instructions
    system_message = {
        "role": "system",
        "content": f"""You are Yenta. Here is what you remember about this user:

{summary}

IMPORTANT FORMATTING INSTRUCTIONS:
YOU MUST RESPOND IN THE FOLLOWING JSON FORMAT WITH NO EXCEPTIONS:
{{
  "reply": "Your response to the user goes here",
  "updated_summary": "Updated summary of the conversation including any new information"
}}

DO NOT add any explanatory text outside of the JSON structure.
DO NOT add any markdown formatting or code blocks.
DO NOT include the word 'json' or any other text before or after your JSON object.
JUST RETURN THE JSON OBJECT DIRECTLY.
"""
    }
    messages.append(system_message)

    # Add recent conversation history (up to the last 10 messages)
    recent_messages = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    messages.extend(recent_messages)

    # Add new user message
    new_message = {"role": "user", "content": user_message}
    messages.append(new_message)

    # Prepare payload for Ollama API
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": False,  # Explicitly disable streaming
        "temperature": 0.2  # Lower temperature for more consistent outputs
    }

    try:
        # Call Ollama API
        response = requests.post(OLLAMA_API_URL_CHAT, json=payload)
        response.raise_for_status()

        # Log the raw response content for debugging
        logger.info(f"Raw API response status: {response.status_code}")
        logger.info(f"Raw API response content: {response.content[:1000]}")  # Log first 1000 chars in case it's large

        # Parse the response
        try:
            result = response.json()
            logger.info(f"Successfully parsed API response: {result}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response as JSON: {str(e)}")
            logger.error(f"Response content: {response.content.decode('utf-8', errors='replace')}")
            raise Exception(f"Invalid JSON response from Ollama API: {str(e)}")

        response_text = result.get("message", {}).get("content", "{}")

        # Log the extracted text before JSON parsing
        logger.info(f"Extracted response text: {response_text[:1000]}")  # First 1000 chars

        # Extract JSON from the response
        try:
            # Find JSON in the response text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')

            logger.info(f"JSON start index: {start_idx}, end index: {end_idx}")

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx+1]
                logger.info(f"Extracted JSON string: {json_str[:1000]}")  # Log the extracted JSON

                try:
                    parsed_response = json.loads(json_str)
                    logger.info(f"Successfully parsed JSON: {parsed_response}")

                    reply = parsed_response.get("reply", "Sorry, I couldn't generate a proper response.")
                    updated_summary = parsed_response.get("updated_summary", summary)

                    return reply, updated_summary
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {str(e)}", exc_info=True)
                    raise Exception(f"LLM returned malformed JSON: {str(e)}")
            else:
                logger.error("No JSON object found in response text")
                raise Exception("LLM failed to return JSON. Please respond with a proper JSON format.")
        except (json.JSONDecodeError, ValueError) as e:
            # If can't parse as JSON, use the whole response as reply and keep old summary
            logger.error(f"JSON processing error: {str(e)}", exc_info=True)
            raise Exception("LLM failed to return valid JSON. Please reformat your response.")

    except requests.RequestException as e:
        # Handle API request errors
        logger.error(f"API request error in chat_with_memory: {str(e)}", exc_info=True)
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing LLM chat response: {str(e)}", exc_info=True)
        raise Exception(f"Error processing LLM response: {str(e)}")

