from noor.botTools.userLitmitMNG import UserLimitManager

TOKEN = ""
GEMINI_API_KEY= ""
ELEVENLABS_API_KEY = ""
CHANNEL_ID = -100  # добавьте ID вашего канала оставьте -100 \ replace with your channels id after -100 e.g. -100123456789
CHANNEL_LINK = ""  # ссылка на канал или пришлашение /  link for cahnnel or invite e.g. https://t.me/...........


MANDOTARY_SUBSCRIPTION = False 
# True = user will have to subscrive to chanel to use the bot
# False = users are free to use the bot without subscription
# True = пользователь должен подписаться на канал, чтобы использовать бота
# False = пользователи могут использовать бота без подписки


CHAT_HISTORY_FILE = "chat_history.json" 
USER_PROFILE_FILE = "user_profile.json"
VOICE_SETTINGS_FILE = "voice_settings.json"
ALL_USERS_DB = "all_users.json"


limit_manager = UserLimitManager(max_daily_limit=20, audio_max_limits=1)

#max daily litmit is limit for messages for user for a day, e.g. 20, user can send only 20 messages per day
#audio max limit is limit for audio/voice messages, e.g. 1, users can only send 1 voice message or 1 audio message per day

#максимальный дневной лимит - это лимит сообщений для пользователя в день, например, 20, пользователь может отправлять только 20 сообщений в день
#максимальный лимит аудио - это лимит для аудио/голосовых сообщений, например, 1, пользователи могут отправлять только 1 голосовое сообщение или 1 аудиосообщение в день

