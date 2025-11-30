# import os
# import json
# import requests
# from typing import Optional
# from dotenv import load_dotenv

# load_dotenv()


# def get_gemini_api_key() -> Optional[str]:
#     return os.environ.get('GEMINI_API_KEY')


# def generate_text(prompt: str, model: str = 'text-bison-001', api_key: Optional[str] = None) -> str:
#     """
#     Simple wrapper to call Google Generative Language REST API.

#     Note: Ensure the env var `GEMINI_API_KEY` is set. This function keeps calls minimal
#     and returns the model text if available. If key is absent, returns a message.
#     """
#     # prefer explicit api_key argument, otherwise fall back to environment
#     key = api_key or get_gemini_api_key()
#     if not key:
#         return 'GEMINI_API_KEY not set; provide a key via environment or pass it to the function.'

#     # Basic REST call - user may need to adapt endpoint/model for their account
#     url = f'https://generativelanguage.googleapis.com/v1beta2/models/{model}:generate?key={key}'
#     headers = {'Content-Type': 'application/json'}
#     body = {
#         'prompt': {'text': prompt},
#         'temperature': 0.2,
#         'maxOutputTokens': 512,
#     }
#     try:
#         resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
#         resp.raise_for_status()
#         data = resp.json()
#         # The real response shape may vary; attempt several locations
#         if 'candidates' in data and isinstance(data['candidates'], list):
#             return data['candidates'][0].get('content', '')
#         if 'output' in data and isinstance(data['output'], dict):
#             return data['output'].get('text', '')
#         return json.dumps(data)
#     except Exception as exc:
#         return f'Failed to call Gemini API: {exc}'

"""
windsurf/gemini_client.py

Improved Gemini client with:
- .env loading via python-dotenv
- flexible auth (API key via GEMINI_API_KEY or bearer token via GEMINI_BEARER_TOKEN)
- clear error messages returned as strings (easy to show in Streamlit)
- small helpers for testing

Usage:
- Put GEMINI_API_KEY=your_key or GEMINI_BEARER_TOKEN=ya29... in your .env
- pip install python-dotenv requests
- import generate_text from this module and call generate_text(prompt, model='...)'
"""
from __future__ import annotations
import os
import json
import requests
from typing import Optional, Union

# Load .env automatically when this module is imported
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If python-dotenv isn't installed, we won't crash here. But recommend installing it.
    pass


def _get_auth() -> dict:
    """Return a dict with auth information.

    Priority:
      1. GEMINI_BEARER_TOKEN -> use Authorization: Bearer <token>
      2. GEMINI_API_KEY -> use ?key=<api_key> on URL
      3. GOOGLE_API_KEY -> fallback name

    Returns: dict with either {'bearer': token} or {'api_key': key} or {}
    """
    bearer = os.environ.get('GEMINI_BEARER_TOKEN') or os.environ.get('BEARER_TOKEN')
    if bearer:
        return {'bearer': bearer}
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if api_key:
        return {'api_key': api_key}
    return {}


def generate_text(prompt: str, model: str = 'gemini-2.5-flash', max_output_tokens: int = 8192, timeout: int = 60, api_key: Optional[str] = None) -> str:
    """Generate text using the Google Generative AI API (Gemini).

    Returns a string. On errors, returns a helpful error message string (so Streamlit can show it).
    """
    if not prompt:
        return "Error: prompt is empty. Provide a non-empty prompt to generate_text()."

    # allow caller to pass an explicit API key for this call
    if api_key:
        auth = {'api_key': api_key}
    else:
        auth = _get_auth()

    if not auth:
        return (
            "GEMINI API credentials not found.\n"
            "Set GEMINI_API_KEY=<your_api_key> or GEMINI_BEARER_TOKEN=<oauth_token> in your environment or .env file, or pass an API key to this function."
        )

    # Use the v1 API endpoint with supported models like 'gemini-pro', 'gemini-1.5-pro', etc.
    # The older v1beta2 models are deprecated. If you need a different base URL, set GEMINI_BASE_URL.
    base_url = os.environ.get('GEMINI_BASE_URL') or 'https://generativelanguage.googleapis.com/v1'
    endpoint = f"{base_url}/models/{model}:generateContent"

    headers = {"Content-Type": "application/json"}
    params = {}

    # choose auth style
    if 'bearer' in auth:
        headers['Authorization'] = f"Bearer {auth['bearer']}"
    elif 'api_key' in auth:
        # prefer putting api key in params (safer than in headers for some setups)
        params['key'] = auth['api_key']

    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": max_output_tokens,
            "temperature": 0.7,
        }
    }

    try:
        resp = requests.post(endpoint, headers=headers, params=params, json=body, timeout=timeout)
        # raise_for_status will raise for 4xx/5xx and include status code
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"HTTP error calling Gemini API: {e}"

    try:
        data = resp.json()
    except ValueError:
        # Not JSON — return raw text for debugging
        return f"Non-JSON response from Gemini API: {resp.text[:1000]}"

    # Parse response from Google Generative AI v1 API
    # Response shape: {'candidates': [{'content': {'parts': [{'text': '...'}]}}]}
    if isinstance(data, dict):
        if 'candidates' in data and isinstance(data['candidates'], list) and data['candidates']:
            first_candidate = data['candidates'][0]
            if isinstance(first_candidate, dict):
                # Modern v1 API: content -> parts -> text
                if 'content' in first_candidate:
                    content = first_candidate['content']
                    if isinstance(content, dict) and 'parts' in content:
                        parts = content['parts']
                        if isinstance(parts, list) and parts:
                            for part in parts:
                                if isinstance(part, dict) and 'text' in part:
                                    text_content = part['text']
                                    if text_content and text_content.strip():
                                        return text_content
                        # Empty parts but valid structure
                        finish_reason = first_candidate.get('finishReason', '')
                        if finish_reason == 'MAX_TOKENS':
                            return "⚠️ Response was truncated. The analysis is too long. Try asking a more specific question."
                        return "API returned empty response. Try rephrasing your question or providing more specific details."
                # Fallback: try nested text fields
                for k in ('text', 'message'):
                    if k in first_candidate:
                        text_val = str(first_candidate.get(k, ''))
                        if text_val and text_val.strip():
                            return text_val
        
        # Legacy/alternative response formats
        if 'output' in data:
            out = data['output']
            if isinstance(out, str):
                return out
            if isinstance(out, dict) and 'text' in out:
                return out['text']
        
        # Check for error responses
        if 'error' in data:
            error_info = data['error']
            if isinstance(error_info, dict):
                msg = error_info.get('message', str(error_info))
                return f"API error: {msg}"
            return f"API error: {error_info}"

    # If nothing matched, return error message instead of JSON dump
    return "Unable to extract text from API response. The API may have returned an unexpected format."


# Small convenience/test runner when executed as a script
if __name__ == '__main__':
    sample = (
        "You are a helpful data analyst. Given that a dataset has 100 rows and two numeric columns, "
        "age with mean 34.5 and income with median 42000, summarize potential insights compactly."
    )
    print("Calling generate_text with a short test prompt...\n")
    out = generate_text(sample)
    print(out)
