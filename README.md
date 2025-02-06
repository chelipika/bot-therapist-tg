```md
# Noor AI Chatbot

![Python 3.11.9](https://img.shields.io/badge/Python-3.11.9-blue?logo=python&logoColor=white)
![aiogram 3.17.0](https://img.shields.io/badge/aiogram-3.17.0-brightgreen)
![Google Generative AI](https://img.shields.io/badge/Google%20Generative%20AI-active?logo=google&logoColor=white)

A feature-rich Telegram bot that simulates a personal AI therapist. It leverages aiogram for bot management and Google’s Gemini API to generate AI responses. The bot supports interactive user registration, chat history management, daily usage limits, and payment-based limit extensions.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Running the Bot](#running-the-bot)
- [File Structure](#file-structure)
- [Usage](#usage)

---

## Features

- **Interactive Greeting & Settings:** Welcomes users with multilingual greetings and provides easy access to settings.
- **User Registration:** Gathers personalized details using a multi-step conversation.
- **Chat History Management:** Saves and displays complete conversation logs.
- **Daily Usage Limits:** Implements a daily usage limit per user with automatic resets.
- **Payment Integration:** Allows users to extend their daily limits via payment processing.
- **AI Response Generation:** Streams AI responses using Google’s Gemini API with real-time updates.

---

## Requirements

- **Python:** 3.11.9  
- **aiogram:** 3.17.0  
- **google-generativeai:** Latest version available on PyPI

---

## Setup

1. **Clone the repository** and navigate to the project directory.
2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Credentials:**

   Create a `config.py` file in the project root with your API keys:

   ```python
   TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   ```

5. **File Permissions:**

   Ensure the bot has write permissions for `chat_history.json` and `user_limits.json`.

---

## Running the Bot

Start the bot with the following command:

```bash
python your_script_name.py
```

Replace `your_script_name.py` with the actual filename of your bot script.

---

## File Structure

```
├── config.py             # Contains API tokens and configuration keys.
├── chat_history.json     # Stores conversation logs for users.
├── user_limits.json      # Tracks daily usage limits for each user.
├── user_profile.json     # Saves user registration details.
├── requirements.txt      # Lists all project dependencies.
└── your_script_name.py   # Main bot script containing all handlers and logic.
```

---

## Usage

- **Start Command:**  
  `/start` greets the user and displays the main menu with settings options.

- **Registration:**  
  Initiate registration via `/reg` or the profile button to set up your personalized AI interaction.

- **Chat History:**  
  View your conversation history using `/history` or the dedicated history button.

- **Clearing History:**  
  Use `/end` or `/new` to clear the current chat session.

- **Extend Daily Limits:**  
  Trigger limit extension via the "fundup" button or `/fund`, which processes an invoice and updates your limits.

- **General Interaction:**  
  Send any text to start a conversation with the AI. The bot tracks each interaction, enforces usage limits, and responds using Google’s Gemini API.

---

## requirements.txt

```
aiogram==3.17.0
google-generativeai
```

---

Enjoy your personal AI therapist experience.
```
