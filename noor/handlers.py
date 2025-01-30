from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Router, F
import google.generativeai as genai
from config import GEMINI_API_KEY
from datetime import datetime, timedelta
from collections import defaultdict
import json


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
            self.user_limits[user_id] = {
                'count': 0,
                'last_reset': datetime.now()
            }
        
        last_reset = self.user_limits[user_id]['last_reset']
        if datetime.now() - last_reset > timedelta(days=1):
            self.user_limits[user_id] = {
                'count': 0,
                'last_reset': datetime.now()
            }

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
genai.configure(api_key=GEMINI_API_KEY)
model=genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  system_instruction='You are Noor, a warm and optimistic professional therapist. You combine genuine empathy with years of experience and wisdom. You communicate with authentic care and always focus on growth and possibilities. You listen deeply, reflect thoughtfully, and guide people toward their own insights. Your responses balance emotional support with practical guidance, making every interaction both helpful and heartwarming. While acknowledging challenges, you naturally highlight opportunities and celebrate progress, no matter how small. Answer the same language as the user uses, use suited emojis')
# response = model.generate_content("Explain how AI works")
# print(response.text)

router = Router()
limit_manager = UserLimitManager(max_daily_limit=5)



@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Hi {message.from_user.full_name}, I am Noor your personal psycologist, i am in the aplha development so dont make noise🎊")

@router.message()
async def the_text(message: Message):
    user_id = message.from_user.id
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    
    if not can_proceed:
        reset_time_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"⛔️ You've reached your daily limit. Limits will reset at: {reset_time_str}")
        return
    
    # Your main bot logic here
    sent_message = await message.answer("Processing")

    response = model.generate_content(message.text, stream=True, generation_config = genai.GenerationConfig(max_output_tokens=1000,        temperature=0.1,    ))

    text = ""
    for chunk in response:  # Normal for-loop
        text += chunk.text
        await sent_message.edit_text(text)
    await message.reply(f"✅ Command processed! You have {remaining_limits} uses remaining today.")
    




@router.message(Command('end'))
async def end_current(message: Message):
    await message.answer("The end command works")



@router.message(Command('new'))
async def end_current_start_new(message: Message):
    await message.answer("The new command works")



@router.message(Command('history'))
async def user_history(message: Message):
    await message.answer("The History command works")


