This script implements a Telegram bot using the `aiogram` library, which interacts with Google’s Gemini API for generative AI responses. It manages user interaction with daily limits on usage, tracking these limits via a JSON file. The bot provides various commands such as `/start`, `/end`, `/new`, and `/history` to engage users, while ensuring users don't exceed their daily usage limits. The bot's primary functionality includes responding to text messages with personalized generative content, while tracking daily interactions and enforcing usage constraints. 🤖💬

#### Features:
- **User Limit Management** 🔒: Tracks and enforces daily interaction limits for each user. Resets daily usage after 24 hours. ⏰
- **Generative AI Responses** 💡: Leverages Google’s Gemini model to generate personalized therapeutic responses based on user input. 🧠💬
- **Bot Commands** 🎮: Includes basic commands such as `/start`, `/end`, `/new`, and `/history` to interact with the bot. ⚙️
- **File Persistence** 💾: Saves user limits and resets them on a daily basis using a local JSON file. 📂

#### Requirements:
- **aiogram** 📲: For Telegram bot API handling.
- **google-generativeai** 🤖: To interact with Google’s generative AI for processing user input and generating responses.
