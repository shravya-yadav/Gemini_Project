from django.shortcuts import render
from django.conf import settings
import google.generativeai as genai
import json
from datetime import datetime
import os
import logging
from django.core.cache import cache

# Set up logging
logger = logging.getLogger(__name__)

HISTORY_FILE = os.path.join(settings.BASE_DIR, 'chat_history.jsonl')
HISTORY_CACHE_KEY = 'chat_history'
HISTORY_LIMIT = 10  # Number of history entries to display
CONTEXT_LIMIT = 5   # Number of history entries for context

def load_history():
    """Load chat history from file and cache it."""
    history = cache.get(HISTORY_CACHE_KEY)
    if history is None:
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history = [json.loads(line) for line in f if line.strip()]
                cache.set(HISTORY_CACHE_KEY, history, timeout=300)  # Cache for 5 minutes
            except Exception as e:
                logger.error(f"Error reading history file: {str(e)}")
    return history

def save_to_history(query, response):
    """Save a query and response to the history file."""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'query': query[:1000],  # Limit query length
        'response': response[:5000]  # Limit response length
    }
    try:
        with open(HISTORY_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        cache.delete(HISTORY_CACHE_KEY)  # Invalidate cache
    except Exception as e:
        logger.error(f"Error writing to history file: {str(e)}")

def get_gemini_response(prompt):
    """Get a response from the Gemini AI model."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        # Build context from recent history
        history = load_history()
        context_lines = [
            f"User: {entry['query']}\nAI: {entry['response']}"
            for entry in history[-CONTEXT_LIMIT:]
        ]
        context_str = "\n".join(context_lines)

        logger.info("Sending request to Gemini API")
        response = model.generate_content(
            f"{context_str}\nNew query: {prompt}" if context_str else prompt,
            generation_config={"temperature": 0.7},
            request_options={'timeout': 60}  # Increased timeout to 60 seconds
        )
        logger.info("Received response from Gemini API")
        return response.text

    except genai.GenerationError as e:
        logger.error(f"Gemini API generation error: {str(e)}")
        return f"Error: API generation failed - {str(e)}"
    except TimeoutError as e:
        logger.error(f"Timeout error: {str(e)}")
        return f"Error: Request timed out after 60 seconds - {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Error: {str(e)}"

def chat_view(request):
    """Handle chat requests and render the chat interface."""
    response = None
    history = load_history()

    if request.method == 'POST':
        user_query = request.POST.get('query', '').strip()
        if user_query:
            if len(user_query) > 1000:
                response = "Error: Query is too long (max 1000 characters)"
            else:
                response = get_gemini_response(user_query)
                print(response)
                save_to_history(user_query, response)

    return render(request, 'chat.html', {
        'response': response,
        'history': reversed(history[-HISTORY_LIMIT:])
    })