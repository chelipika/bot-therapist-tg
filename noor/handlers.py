import json
import os
from aiogram import F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery
from aiogram import Router
import google.generativeai as genai
from config import GEMINI_API_KEY
from datetime import datetime, timedelta
from collections import defaultdict
from noor.instructions import INSTRUCTIONS_OF_AI
from config import TOKEN
bot = Bot(token=TOKEN)
import noor.keyboards as kb


# File to store chat history
CHAT_HISTORY_FILE = "chat_history.json"

# Load existing chat history from the file
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

# Save chat history to the file
def save_chat_history():
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(user_chat_histories, f, indent=4)

# Initialize user chat history
user_chat_histories = load_chat_history()

# Ensure dictionary format
if not isinstance(user_chat_histories, dict):
    user_chat_histories = {}

class UserLimitManager:
    def __init__(self, max_daily_limit=5):
        self.max_daily_limit = max_daily_limit
        self.user_limits = defaultdict(dict)
        self.filename = "user_limits.json"
        self.load_limits()

    def load_limits(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for user_id, info in data.items():
                    self.user_limits[user_id] = {
                        'count': info['count'],
                        'last_reset': datetime.fromisoformat(info['last_reset'])
                    }
        except FileNotFoundError:
            pass

    def save_limits(self):
        data = {
            user_id: {
                'count': info['count'],
                'last_reset': info['last_reset'].isoformat()
            }
            for user_id, info in self.user_limits.items()
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def check_and_reset_daily(self, user_id):
        user_id = str(user_id)
        if user_id not in self.user_limits:
            self.user_limits[user_id] = {'count': 0, 'last_reset': datetime.now()}
        
        last_reset = self.user_limits[user_id]['last_reset']
        if datetime.now() - last_reset > timedelta(days=1):
            self.user_limits[user_id] = {'count': 0, 'last_reset': datetime.now()}
    def funded_limites(self, user_id):
        user_id = str(user_id)
        x = int(self.user_limits[user_id]['count'])
        y = self.user_limits[user_id]['last_reset']
        self.user_limits[user_id] = {'count': x-10, 'last_reset': y}


    async def use_limit(self, user_id):
        user_id = str(user_id)
        self.check_and_reset_daily(user_id)

        if self.user_limits[user_id]['count'] >= self.max_daily_limit:
            reset_time = self.user_limits[user_id]['last_reset'] + timedelta(days=1)
            return False, 0, reset_time

        self.user_limits[user_id]['count'] += 1
        remaining = self.max_daily_limit - self.user_limits[user_id]['count']
        self.save_limits()
        return True, remaining, None

# Configure the AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=INSTRUCTIONS_OF_AI
)

router = Router()
limit_manager = UserLimitManager(max_daily_limit=20)
hi_message = '''🧠 EN: Welcome to your personal AI psychologist! I provide confidential, empathetic support to help you navigate emotions, challenges, and personal growth. Together, we'll explore your inner world safely and constructively. Ready to begin? 💆‍♀️

🌿 RU: Привет! Я твой личный психолог-ИИ! Предоставляю конфиденциальную поддержку, помогаю разобраться в эмоциях и личностном развитии. Вместе мы безопасно исследуем твой внутренний мир. Готов начать? 🤝'''
@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Hi\Привет {message.from_user.full_name}\n {hi_message}", reply_markup=kb.settings)


@router.callback_query(F.data == 'history_callback')
async def history_callback(callback: CallbackQuery):
    await callback.answer("History: show")
    user_id = str(callback.from_user.id)
    
    if user_id not in user_chat_histories or not user_chat_histories[user_id]:
        await callback.message.answer("📜 No chat history found.", reply_markup=kb.back_to_main)
        return

    history_text = "\n\n".join(
        f"{entry['role'].capitalize()}: {entry['parts'][0]['text']}"
        for entry in user_chat_histories[user_id]
    )

    await callback.message.edit_text(f"📜 Chat History:\n\n{history_text}", reply_markup=kb.back_to_main)
    
@router.callback_query(F.data == "fundup")
async def fundup(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    await callback.message.answer_invoice(
        title="Extend limits",
        description="Your going to extend you limit by 10 additional tries",
        payload='fundup_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )

@router.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(hi_message, reply_markup=kb.settings)
@router.message(Command('setupprofile'))
async def set_up_profile(message: Message):
    await message.answer("How should you call me?")
    user_id = message.from_user.id
    data = {
            user_id: {
                'nameOfAi': message.text,
                'usersName': None
            }
        }
    with open('userProfiles.json', 'w') as f:
        json.dump(data, f)
    
###
@router.message(Command('fund'))
async def start(message: Message):
    await message.answer_invoice(
        title="Extend limits",
        description="Your going to extend you limit by 10 additional tries",
        payload='fundup_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )

@router.pre_checkout_query()
async def pre_checkout_handler(event: PreCheckoutQuery):
    await event.answer(True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = str(message.from_user.id)
    await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id)

    limit_manager.funded_limites(user_id=user_id)
    await message.answer("Your stuff has been updated😍", reply_markup=kb.back_to_main)
###



@router.message(Command('history'))
async def user_history(message: Message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_chat_histories or not user_chat_histories[user_id]:
        await message.answer("📜 No chat history found.")
        return

    history_text = "\n\n".join(
        f"{entry['role'].capitalize()}: {entry['parts'][0]['text']}"
        for entry in user_chat_histories[user_id]
    )

    await message.answer(f"📜 Chat History:\n\n{history_text}")

@router.message(Command('end'))
async def end_current(message: Message):
    user_id = str(message.from_user.id)
    user_chat_histories[user_id] = []  # Clear history for new conversation
    save_chat_history()
    await message.answer("🚮 History has been cleared")

@router.message(Command('new'))
async def end_current_start_new(message: Message):
    user_id = str(message.from_user.id)
    user_chat_histories[user_id] = []  # Clear history for new conversation
    save_chat_history()
    await message.answer("🔄 New chat session started.")

@router.message()
async def the_text(message: Message):
    if message.text is not None:

        user_id = str(message.from_user.id)  # Convert to string for JSON compatibility
        can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)

        if not can_proceed:
            reset_time_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")
            await message.reply(f"⛔️ You've reached your daily limit. Limits reset at: {reset_time_str} \n ⛔️ Вы использовали все сегодняшние попытки. Лимит перезагрузится в: {reset_time_str}")
            return

        sent_message = await message.answer("Processing...")

        # Ensure user history exists
        if user_id not in user_chat_histories:
            user_chat_histories[user_id] = []

        # Add user message to history
        user_chat_histories[user_id].append({
            "role": "user",
            "parts": [{"text": message.text}]
        })
        save_chat_history()

        # Generate AI response
        chat_session = model.start_chat(history=user_chat_histories[user_id])
        response = chat_session.send_message(message.text)

        response_text = response.text

        # Save AI response to history
        user_chat_histories[user_id].append({
            "role": "model",
            "parts": [{"text": response_text}]
        })
        save_chat_history()

        # Send response to user
        text = ""
        for chunk in response:  # Normal for-loop
            text += chunk.text
            await sent_message.edit_text(text)


        await message.reply(f"✅ Command processed! {remaining_limits} uses remaining today.\n ✅ Запрос успешен! {remaining_limits} Попыток на сегодня.")
