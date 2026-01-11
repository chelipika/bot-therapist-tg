# 🤖 Noor AI Chatbot


A sophisticated Telegram bot that serves as your personal AI therapist, powered by Google's Gemini API. With features like voice interactions, multi-language support, and customizable personalities, Noor creates a unique and engaging therapeutic experience.

## TODO
- remove chat history json method, use gemini built in function instead
- move all json files to db[user profile, voice settings, user limit]


## ✨ Features

### Core Capabilities
- 🎯 **Smart Chat System**
  - Contextual conversations with memory
  - Daily usage tracking and limits
  - Multi-language support (English/Russian)

### Voice & Audio
- 🎤 **Voice Message Processing**
  - Voice-to-text conversion using Whisper
  - Text-to-speech responses with ElevenLabs
  - Multiple voice personalities

### User Experience
- 👤 **Personalized Profiles**
  - Customizable AI personality
  - User preference storage
  - Conversation history management

### Payment Integration
- 💳 **Premium Features**
  - Extended daily message limits
  - Additional voice message credits
  - Seamless payment processing

## 🛠️ Technical Requirements

### Core Dependencies
- ![Python](https://img.shields.io/badge/Python-3.11.9-blue)
- ![aiogram](https://img.shields.io/badge/aiogram-3.17.0-green) 
- ![Gemini](https://img.shields.io/badge/google--generativeai-0.8.4-red) 
- ![Whisper](https://img.shields.io/badge/openai--whisper-20240930-orange)

### Additional Requirements
- ElevenLabs API access
- Telegram Bot Token
- Google Gemini API key

## 🚀 Getting Started

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
```

### 2. Installation
```bash
# Install all dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `config.py` file with your credentials:
```python
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
```

### 4. Launch
```bash
python bot.py
```

## 🎮 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and display options |
| `/reg` | Start user profile registration |
| `/history` | View conversation history |
| `/new` | Start new conversation |
| `/end` | Clear current chat history |
| `/fund` | Purchase additional message credits |
| `/audio_plan` | Purchase voice message credits |
| `/au` | Generate audio response |

## 💾 Data Storage
The bot utilizes several JSON files for data persistence:
- `chat_history.json`: Stores conversation logs
- `user_profile.json`: Maintains user preferences
- `voice_settings.json`: Voice configuration data
- `user_limits.json`: Usage tracking

## 🔒 Privacy & Security
- All conversations are stored securely
- User data is handled with strict confidentiality
- Payment processing through secure Telegram payments

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
