# Noor AI Chatbot

This bot uses aiogram and Google’s Gemini API to simulate a personal AI therapist. It handles user registration, chat history, daily usage limits, and payment processing for extended limits.

## Requirements
- Python 3.11.9
- aiogram==3.17.0
- google-generativeai==0.8.4
- openai-whisper==20240930
## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit a `config.py` file with your credentials:
   ```python
   TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   ```
## Running

Start the bot by running:
```
python bot.py
```
Replace `bot.py` with the actual filename only if it has been changed.

## Features

- **Start Command**: Greets users and presents options.
- **Chat History**: Saves and displays conversation logs.
- **User Registration**: Collects profile details via interactive prompts.
- **Daily Limits**: Tracks daily usage. Payment processing extends limits.
- **AI Chat**: Sends user messages to the Gemini API and streams responses.

---

# requirements.txt

```
aiogram==3.17.0
google-generativeai==0.8.4
openai-whisper==20240930
```
