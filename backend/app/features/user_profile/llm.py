import json
import logging
from typing import Any

import aiohttp

# Set up logger
logger = logging.getLogger(__name__)

# Configuration for Ollama API
OLLAMA_API_HOST = "host.docker.internal"  # Use localhost for local development, host.docker.internal for Docker
OLLAMA_API_PORT = 11434
OLLAMA_API_URL_GENERATE = f"http://{OLLAMA_API_HOST}:{OLLAMA_API_PORT}/api/generate"
OLLAMA_API_URL_CHAT = f"http://{OLLAMA_API_HOST}:{OLLAMA_API_PORT}/api/chat"
DEFAULT_MODEL = "llama3.2:latest"
MAX_RETRIES = 2  # Maximum number of retries for malformed JSON


async def parse_profile_from_text(text: str) -> dict[str, Any]:
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
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL_GENERATE, json=payload) as response:
                response.raise_for_status()

                # Log the raw response for debugging
                logger.info(f"API response status: {response.status}")
                
                # Parse the response
                try:
                    result = await response.json()
                    logger.info(f"Successfully parsed API response: {result}")
                except json.JSONDecodeError as e:
                    response_text = await response.text()
                    logger.error(f"Failed to parse API response as JSON: {str(e)}")
                    logger.error(f"Response content: {response_text}")
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
    except aiohttp.ClientError as e:
        # Handle API request errors
        logger.error(f"API request error: {str(e)}", exc_info=True)
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
        raise Exception(f"Error processing LLM response: {str(e)}")


async def chat_with_memory(
    user_message: str,
    summary: str,
    conversation_history: list[dict[str, str]],
    user_profile: dict[str, Any] = None
) -> tuple[str, str]:
    """
    Sends a chat request to the Ollama API with memory (summary + recent messages).

    Args:
        user_message: The new message from the user
        summary: The current summary of the conversation
        conversation_history: List of previous messages as {"role": "user|assistant", "content": "..."}
        user_profile: The user's LLM profile data (optional)

    Returns:
        Tuple of (assistant_reply, updated_summary)

    Raises:
        Exception: If the API call fails or the response cannot be parsed
    """
    retries = 0
    last_error = None

    while retries <= MAX_RETRIES:
        try:
            # Prepare message history
            messages = []

            # Format user profile data if available
            profile_info = ""
            if user_profile:
                profile_info = "\nUser Profile Information:\n"
                profile_info += json.dumps(user_profile, indent=2)

            # Add system message with user summary and strict JSON format instructions
            system_message_content = f"""You are Yenta. Here is what you remember about this user:

{summary}{profile_info}

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

            # If we're retrying, add error information to the system message
            if retries > 0:
                system_message_content += f"""

IMPORTANT: Your previous response contained invalid JSON.
Error details: {last_error}
DO NOT make the same mistake again.
MAKE SURE you properly close all JSON brackets and quotes.
DOUBLE CHECK your response format before submitting.
"""

            system_message = {
                "role": "system",
                "content": system_message_content
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

            # Call Ollama API
            async with aiohttp.ClientSession() as session:
                async with session.post(OLLAMA_API_URL_CHAT, json=payload) as response:
                    response.raise_for_status()

                    # Log the raw response content for debugging
                    logger.info(f"Raw API response status: {response.status}")
                    response_content = await response.text()
                    logger.info(f"Raw API response content: {response_content[:1000]}")  # Log first 1000 chars in case it's large

                    # Parse the response
                    try:
                        result = await response.json()
                        logger.info(f"Successfully parsed API response: {result}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse API response as JSON: {str(e)}")
                        logger.error(f"Response content: {response_content}")
                        raise Exception(f"Invalid JSON response from Ollama API: {str(e)}")

                    response_text = result.get("message", {}).get("content", "{}")

                    # Log the extracted text before JSON parsing
                    logger.info(f"Extracted response text: {response_text[:1000]}")

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
                                last_error = f"JSON parsing error: {str(e)}"
                                logger.error(last_error, exc_info=True)
                                raise Exception(last_error)
                        else:
                            last_error = "No JSON object found in response text"
                            logger.error(last_error)
                            raise Exception(last_error)
                    except (json.JSONDecodeError, ValueError) as e:
                        # If can't parse as JSON, use the whole response as reply and keep old summary
                        last_error = f"JSON processing error: {str(e)}"
                        logger.error(last_error, exc_info=True)
                        raise Exception(last_error)

        except aiohttp.ClientError as e:
            # Handle API request errors - these are not retryable
            logger.error(f"API request error in chat_with_memory: {str(e)}", exc_info=True)
            raise Exception(f"Error calling Ollama API: {str(e)}")
        except Exception as e:
            # Retry on JSON parsing errors
            logger.warning(f"Attempt {retries + 1}/{MAX_RETRIES + 1} failed: {str(e)}")
            last_error = str(e)
            retries += 1
            continue  # Try again

    # If we've exhausted retries, raise the last error
    logger.error(f"Error processing LLM chat response after {MAX_RETRIES + 1} attempts: {last_error}")
    raise Exception(f"Failed to get valid JSON after {MAX_RETRIES + 1} attempts. Last error: {last_error}")


async def summarize_profile_data(profile_data: dict[str, Any]) -> str:
    """
    Sends a request to the Ollama API to summarize profile data into a readable form.

    Args:
        profile_data: The structured profile data from the database

    Returns:
        A human-readable summary of the profile

    Raises:
        Exception: If the API call fails or the response cannot be parsed
    """
    # Convert profile data to a formatted string
    profile_str = json.dumps(profile_data, indent=2)

    prompt = f"""
You are AskYenta, a witty but kind assistant. You're helping a user review their profile.
Take the following structured data and turn it into a short, engaging description they can see and edit.
Use natural language, not labels or lists.

Be warm, expressive, and concise. If a section is missing, don't mention it.

Here is the profile data:

{profile_str}

Write the user's profile summary in a way that feels personal and human, like something they'd be proud to show someone new.
"""

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL_GENERATE, json=payload) as response:
                response.raise_for_status()

                result = await response.json()
                summary = result.get("response", "")

                return summary
    except aiohttp.ClientError as e:
        logger.error(f"API request error in summarize_profile_data: {str(e)}", exc_info=True)
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
        raise Exception(f"Error processing LLM response: {str(e)}")


async def update_profile_from_text(existing_profile: dict[str, Any], text: str) -> dict[str, Any]:
    """
    Sends a request to the Ollama API to update an existing profile based on new text.
    The LLM will intelligently merge the new information with the existing profile.

    Args:
        existing_profile: The existing profile data
        text: The new text information to incorporate

    Returns:
        The updated profile data

    Raises:
        Exception: If the API call fails or the response cannot be parsed as JSON
    """
    # Convert existing profile to a formatted string
    profile_str = json.dumps(existing_profile, indent=2)

    prompt = f"""
    You are AskYenta, an assistant that updates user profile data based on new information.

    EXISTING PROFILE:
    {profile_str}

    NEW INFORMATION:
    {text}

    INSTRUCTIONS:
    1. Analyze the new information and determine what should be updated in the existing profile.
    2. Return an updated JSON object that intelligently merges the existing profile with the new information.
    3. Keep existing fields that aren't mentioned in the new information.
    4. Update or add fields based on the new information.
    5. Return ONLY the updated JSON object, with no additional text or explanation.
    """

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL_GENERATE, json=payload) as response:
                response.raise_for_status()

                # Log the raw response for debugging
                logger.info(f"API response status: {response.status}")
                response_content = await response.text()
                logger.info(f"Raw API response content: {response_content[:1000]}")

                # Parse the response
                result = await response.json()
                response_text = result.get("response", "{}")

                # Log the extracted text
                logger.info(f"Extracted response text: {response_text[:1000]}")

                # Extract JSON from response
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
                            # If still can't parse, return the existing profile to avoid data loss
                            logger.error("Failed to parse LLM response as JSON, returning original profile")
                            return existing_profile
                    logger.error("Failed to extract JSON from LLM response, returning original profile")
                    return existing_profile
    except aiohttp.ClientError as e:
        # Handle API request errors
        logger.error(f"API request error: {str(e)}", exc_info=True)
        raise Exception(f"Error calling Ollama API: {str(e)}")
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
        raise Exception(f"Error processing LLM response: {str(e)}")


async def analyze_message_for_profile_updates(existing_profile: dict[str, Any], user_message: str) -> tuple[dict[str, Any], bool]:
    """
    Analyzes a user message to determine if the user profile should be updated.
    
    Args:
        existing_profile: The existing profile data
        user_message: The user's message to analyze
        
    Returns:
        A tuple containing (updated_profile_data, was_profile_updated)
        
    Raises:
        Exception: If the API call fails or the response cannot be parsed as JSON
    """
    # Convert existing profile to a formatted string
    profile_str = json.dumps(existing_profile, indent=2)

    prompt = f"""
    You are AskYenta, an assistant that analyzes user messages to determine if profile data should be updated.

    EXISTING PROFILE:
    {profile_str}

    USER MESSAGE:
    {user_message}

    INSTRUCTIONS:
    1. Analyze the user message to determine if it contains any information that should be added to or updated in the user profile.
    2. Look for personal preferences, biographical info, requests to remember something, or requests to forget/remove something.
    3. If updates are needed, return a JSON object with two fields:
       - "profile_data": The full updated profile JSON with changes applied
       - "was_updated": true
    4. If no updates are needed, return a JSON object with:
       - "profile_data": The unchanged existing profile
       - "was_updated": false
    5. Return ONLY the JSON object, with no additional text or explanation.
    
    IMPORTANT: Only update the profile if the user explicitly shares information they want remembered, or asks to modify their profile.
    """

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL_GENERATE, json=payload) as response:
                response.raise_for_status()

                # Parse the response
                result = await response.json()
                response_text = result.get("response", "{}")

                # Extract JSON from response
                try:
                    # Try to parse directly first
                    parsed_json = json.loads(response_text)
                    return parsed_json.get("profile_data", existing_profile), parsed_json.get("was_updated", False)
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON from the string
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')

                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx+1]
                        try:
                            parsed_json = json.loads(json_str)
                            return parsed_json.get("profile_data", existing_profile), parsed_json.get("was_updated", False)
                        except json.JSONDecodeError:
                            # If still can't parse, return the existing profile to avoid data loss
                            logger.error("Failed to parse LLM response as JSON, returning original profile")
                            return existing_profile, False
                    logger.error("Failed to extract JSON from LLM response, returning original profile")
                    return existing_profile, False
    except aiohttp.ClientError as e:
        # Handle API request errors
        logger.error(f"API request error: {str(e)}", exc_info=True)
        return existing_profile, False
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
        return existing_profile, False


async def analyze_message_for_initial_profile(user_message: str) -> tuple[dict[str, Any], bool]:
    """
    Analyzes a user message to determine if it contains information that warrants creating 
    an initial user profile when none exists.
    
    Args:
        user_message: The user's message to analyze
        
    Returns:
        A tuple containing (profile_data, should_create_profile)
        
    Raises:
        Exception: If the API call fails or the response cannot be parsed as JSON
    """
    prompt = f"""
    You are AskYenta, an assistant that analyzes user messages to determine if a profile should be created.

    USER MESSAGE:
    {user_message}

    INSTRUCTIONS:
    1. Analyze the user message to determine if it contains personal information worth saving in a profile.
    2. Look for personal preferences, biographical info, interests, goals, etc.
    3. If the message contains enough information to create a useful profile:
       - Return a JSON object with two fields:
       - "profile_data": JSON object with extracted profile information
       - "should_create_profile": true
    4. If the message doesn't contain profile-worthy information:
       - Return a JSON object with:
       - "profile_data": empty object {{}}
       - "should_create_profile": false
    5. Return ONLY the JSON object, with no additional text or explanation.
    
    IMPORTANT: Only suggest creating a profile if the user explicitly shares significant personal information.
    Be conservative - only create profiles for substantial information sharing.
    """

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_API_URL_GENERATE, json=payload) as response:
                response.raise_for_status()

                # Parse the response
                result = await response.json()
                response_text = result.get("response", "{}")

                # Extract JSON from response
                try:
                    # Try to parse directly first
                    parsed_json = json.loads(response_text)
                    return parsed_json.get("profile_data", {}), parsed_json.get("should_create_profile", False)
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract JSON from the string
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')

                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx+1]
                        try:
                            parsed_json = json.loads(json_str)
                            return parsed_json.get("profile_data", {}), parsed_json.get("should_create_profile", False)
                        except json.JSONDecodeError:
                            logger.error("Failed to parse LLM response as JSON")
                            return {}, False
                    logger.error("Failed to extract JSON from LLM response")
                    return {}, False
    except aiohttp.ClientError as e:
        # Handle API request errors
        logger.error(f"API request error: {str(e)}", exc_info=True)
        return {}, False
    except Exception as e:
        # Handle general errors
        logger.error(f"Error processing LLM response: {str(e)}", exc_info=True)
        return {}, False

