import json
import whisper
import aiofiles
import requests
import os
from aiogram import F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, FSInputFile, ChatJoinRequest
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
import google.generativeai as genai
from config import GEMINI_API_KEY, ELEVENLABS_API_KEY, TOKEN, CHANNEL_ID, CHANNEL_LINK
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from noor.instructions import INSTRUCTIONS_OF_AI, greeting, voices_text
bot = Bot(token=TOKEN)
import noor.keyboards as kb
# File to store chat history
CHAT_HISTORY_FILE = "chat_history.json"
USER_PROFILE_FILE = "user_profile.json"
VOICE_SETTINGS_FILE = "voice_settings.json"
ALL_USERS_DB = "all_users.json"

class Reg(StatesGroup):
    user_id = State()
    ai_name = State()
    name = State()
    Experience = State()
    Approach = State()
    Mission = State()
    Commitment = State()
    CallToAction = State() 


# --- Load and Save Voice Settings ---
async def load_voice_settings():
    try:
        if os.path.exists(VOICE_SETTINGS_FILE):
            async with aiofiles.open(VOICE_SETTINGS_FILE, "r") as f:
                return json.loads(await f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"default_voice_id": "21m00Tcm4TlvDq8ikWAM"}  # Default value

async def save_voice_settings(voice_id):
    try:
        async with aiofiles.open(VOICE_SETTINGS_FILE, "w") as f:
            await f.write(json.dumps({"default_voice_id": voice_id}, indent=4))
    except Exception as e:
        print(f"Error saving voice settings: {e}")


# Load existing chat history from the file
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}
#loading existing user_profile
def load_user_profile():
    if os.path.exists(USER_PROFILE_FILE):
        with open(USER_PROFILE_FILE, "r") as f:
            return json.load(f)
    return {}
def load_all_user():
    if os.path.exists(ALL_USERS_DB):
        with open(ALL_USERS_DB, "r") as f:
            return json.load(f)
    return {}
# Save chat history to the file
def save_chat_history():
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(user_chat_histories, f, indent=4)
async def sub_chek(user_id):
    if user_id in pending_requests or await is_subscribed(user_id=user_id):
        return True
    else:
        return False

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False
    
async def generate_the_content(text: str, userid: int):
    # Ensure user history exists
    if userid not in user_chat_histories:
        user_chat_histories[userid] = []

    # Add user message to history
    user_chat_histories[userid].append({
        "role": "user",
        "parts": [{"text": text}]
    })
    save_chat_history()
    chat_session = model.start_chat(history=user_chat_histories[userid])
    response = await chat_session.send_message_async(text)
    response_text = response.text

    # Save AI response to history
    user_chat_histories[userid].append({
        "role": "model",
        "parts": [{"text": response_text}]
    })
    save_chat_history()
    return response_text
    
# Initialize user chat history
user_chat_histories = load_chat_history()
user_profile = load_user_profile()
# Ensure dictionary format
if not isinstance(user_chat_histories, dict):
    user_chat_histories = {}

class UserLimitManager:
    def __init__(self, max_daily_limit=5, audio_max_limits=0):
        self.max_daily_limit = max_daily_limit
        self.max_daily_limit_audio = audio_max_limits
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
                        'last_reset': datetime.fromisoformat(info['last_reset']),
                        'audio_count': info['audio_count']
                    }
        except FileNotFoundError:
            pass

    def save_limits(self):
        data = {
            user_id: {
                'count': info['count'],
                'last_reset': info['last_reset'].isoformat(),
                'audio_count': info['audio_count']
            }
            for user_id, info in self.user_limits.items()
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def check_and_reset_daily(self, user_id):
        user_id = str(user_id)
        if user_id not in self.user_limits:
            self.user_limits[user_id] = {'count': 0, 'last_reset': datetime.now(), 'audio_count': 0}
        
        last_reset = self.user_limits[user_id]['last_reset']
        if datetime.now() - last_reset > timedelta(days=1):
            self.user_limits[user_id] = {'count': 0, 'last_reset': datetime.now(), 'audio_count': 0}
    def funded_limites(self, user_id):
        user_id = str(user_id)
        x = int(self.user_limits[user_id]['count'])
        y = self.user_limits[user_id]['last_reset']
        j = int(self.user_limits[user_id]['audio_count'])
        self.user_limits[user_id] = {'count': x-10, 'last_reset': y, 'audio_count': j}
    def funded_limites_auido(self, user_id):
        user_id = str(user_id)
        x = int(self.user_limits[user_id]['count'])
        y = self.user_limits[user_id]['last_reset']
        j = int(self.user_limits[user_id]['audio_count'])
        self.user_limits[user_id] = {'count': x, 'last_reset': y, 'audio_count': j-10}

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
    async def use_limit_audio(self, user_id):
        user_id = str(user_id)
        self.check_and_reset_daily(user_id)

        if self.user_limits[user_id]['audio_count'] >= self.max_daily_limit_audio:
            return False, 0

        self.user_limits[user_id]['audio_count'] += 1
        remaining = self.max_daily_limit_audio - self.user_limits[user_id]['audio_count']
        self.save_limits()
        return True, remaining
class Gen(StatesGroup):
    wait = State()
# Configure the AI model
os.environ["GENAI_API_ENDPOINT"] = "us-central1-genai.googleapis.com"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=INSTRUCTIONS_OF_AI
)



router = Router()
limit_manager = UserLimitManager(max_daily_limit=20, audio_max_limits=1)
hi_message = greeting
pending_requests = set()

import aiosqlite

DATABASE = "all_users.db"

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
        await db.commit()

@router.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    pending_requests.add(update.from_user.id)
    # Optionally notify admins or log the request

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()

    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await message.answer(f"Hi\Привет {message.from_user.full_name}\n {hi_message}", reply_markup=kb.settings)



async def send_to_all(text: str, bot):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            async for row in cursor:
                await bot.send_message(chat_id=row[0], text=text)

@router.message(Command("narrator"))
async def narrator(message: Message, command: CommandObject):
    await send_to_all(command.args, message.bot)



@router.callback_query(F.data == "subchek")
async def subchek(callback: CallbackQuery):
    if not await sub_chek(callback.from_user.id):
        await callback.answer("Your not subscribed yet",)
        return
    await callback.answer("Your are okay to go")
    

@router.callback_query(F.data == 'history_callback')
async def history_callback(callback: CallbackQuery):
    try:
        await callback.answer("History: show")
        user_id = str(callback.from_user.id)
        
        if user_id not in user_chat_histories or not user_chat_histories[user_id]:
            await callback.message.edit_text("📜 No chat history found. \n История чата не найдена", reply_markup=kb.back_to_main)
            return

        history_text = "\n\n".join(
            f"{entry['role'].capitalize()}: {entry['parts'][0]['text']}"
            for entry in user_chat_histories[user_id]
        )

        await callback.message.edit_text(f"📜 Chat History/История чата:\n\n{history_text}", reply_markup=kb.back_to_main)
    except TelegramBadRequest as e:
        if 'MESSAGE_TOO_LONG' in str(e):
            await callback.message.edit_text(f"Error: {e}. Message is too long, Should i converit it to txt file?.", reply_markup=kb.history_text)
        else:
            await callback.message.edit_text(f"An error occurred: {e}")

@router.callback_query(F.data == "send_as_file_history")
async def send_as_file_history(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    user_id = str(callback.from_user.id)
    history_text = "\n\n".join(
            f"{entry['role'].capitalize()}: {entry['parts'][0]['text']}"
            for entry in user_chat_histories[user_id]
        )
    file_hist_name = f"history{user_id}.txt"
    with open(file_hist_name, 'w', encoding="utf-8") as history_file:
        history_file.write(history_text)
    hist_doc = FSInputFile(file_hist_name, filename=f"output_{file_hist_name}_{callback.from_user.id}.txt")
    await callback.message.answer_document(hist_doc, caption="Here is your history in txt file ⬆️")
    os.remove(file_hist_name)

    
@router.callback_query(F.data == "fundup")
async def fundup(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    await callback.message.answer_invoice(
        title="Extend limits/Расширить дневные лимиты",
        description="Your going to extend you limit by 10 additional tries/Вы собираетесь продлить свой лимит на 10 дополнительных попыток.",
        payload='fundup_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )
@router.callback_query(F.data == "voice_change")
async def audio_voice_change(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    await callback.message.edit_text(voices_text, reply_markup=kb.aviable_voices)


@router.callback_query(F.data == "Joseph_change_voice")
async def Joseph_change_voice(callback: CallbackQuery):
    VOICE_ID = "Zlb1dXrM653N07WRdFW3"
    await save_voice_settings(VOICE_ID)
    await callback.answer("The voice has been changed... ✌️")    
@router.callback_query(F.data == "Liam_change_voice")
async def Liam_change_voice(callback: CallbackQuery):
    VOICE_ID = "TX3LPaxmHKxFdv7VOQHJ"
    await save_voice_settings(VOICE_ID)
    await callback.answer("The voice has been changed...✌️")

@router.callback_query(F.data == "Domi_change_voice")
async def Domi_change_voice(callback: CallbackQuery):
    VOICE_ID = "AZnzlk1XvdvUeBnXmlld"
    await save_voice_settings(VOICE_ID)
    await callback.answer("The voice has been changed...✌️")

@router.callback_query(F.data == "Rachel_change_voice")
async def Joseph_change_voice(callback: CallbackQuery):
    VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
    await save_voice_settings(VOICE_ID)
    await callback.answer("The voice has been changed...✌️")



@router.callback_query(F.data == 'fund_up_audio')
async def fund_the_audio(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    await callback.message.answer_invoice(
        title="Extending limits for audio/Расширить лимиты для аудио",
        description="Your going to extend your audio limit by 10 additional tries/Вы собираетесь продлить свой аудио лимит на 10 дополнительных попыток.",
        payload='fundup_audio_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )
@router.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(hi_message, reply_markup=kb.settings)

@router.callback_query(F.data == "profile")
async def profileus(callback: CallbackQuery, state: FSMContext):
    await callback.answer("😍")
    await callback.message.edit_text("Here you can create or see your profile💼", reply_markup=kb.profile_settings)
    
@router.callback_query(F.data == "show_users_profliee")
async def show_users_profliee(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    try:
        await callback.message.edit_text(f"Here is your profile: \n👤 Your_name: {user_profile[user_id]['name']} \n💼 Your_exp_job: {user_profile[user_id]['Experience']} \n💡 My_Approach: {user_profile[user_id]['Approach']} \n🚀 My_Mission: {user_profile[user_id]['Mission']} \n🔒 My_Commitment: {user_profile[user_id]['Commitment']} \n📞 Your_CallToAction: {user_profile[user_id]['CallToAction']} \n🤖 My_ai_name: {user_profile[user_id]['ai_name']}", reply_markup=kb.profile_settings)
    except KeyError:
        await callback.message.edit_text("You dont have a profile yet so you should create one", reply_markup=kb.profile_creating)


@router.callback_query(F.data == "create_update_profile")
async def create_update_profile(callback: CallbackQuery, state: FSMContext):
    await callback.answer("💼")
    await state.set_state(Reg.name)
    await callback.message.answer("How should I call you? Write just your name (e.g. Noor, Licensed Therapist) \n Как мне к вам обращаться? Напишите только имя (например, Нур, лицензированный терапевт)")


@router.message(Gen.wait)
async def stop_flood(message: Message):
    await message.answer("Wait one requests at a time \nПодождите ваш запрос генерируется.")




@router.message(Command("reg"))
async def reg_name(message: Message, state: FSMContext):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await state.set_state(Reg.name)
    await message.answer("How should i call you?(e.g. Noor, Licensed Therapist) \n Как мне к вам обращаться? Напишите только имя (например, Нур, лицензированный терапевт)")

@router.message(Reg.name)
async def reg_exp(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.Experience)
    await message.answer('What do you do(e.g. junior designer, pro programmer, actor. If private leave "private") \n Чем вы занимаетесь (например, младший дизайнер, профессиональный программист, актер. Если вы частный, оставьте «частный»)')

@router.message(Reg.Experience)
async def reg_approach(message: Message, state: FSMContext):
    await state.update_data(Experience=message.text)
    await state.set_state(Reg.Approach)
    await message.answer("How should i approach you? e.g.: \n(Direct, data-driven, and pragmatic—no fluff, just solutions)\n Как мне к вам обращаться? (Прямо, основано на данных и прагматично — без лишних слов, только решения)\n(Слыш, просто на чилях, не веди себя как чушпан, пиши только годные вещи)")

@router.message(Reg.Approach)
async def reg_Mission(message: Message, state: FSMContext):
    await state.update_data(Approach=message.text)
    await state.set_state(Reg.Mission)
    await message.answer('What is my mission?(e.g. Helping you overcome obstacles and optimize mental performance, Help me to overcome procrastination) \n Какова моя миссия? (Например: Помогать вам преодолевать препятствия и оптимизировать умственную продуктивность, Помоги мне справиться с прокрастинацией)')


@router.message(Reg.Mission)
async def reg_Commitment(message: Message, state: FSMContext):
    await state.update_data(Mission=message.text)
    await state.set_state(Reg.Commitment)
    await message.answer("How should i be commited?(e.g. Absolute confidentiality and clear guidance)\n Как я должен быть предан делу? (Например: Абсолютная конфиденциальность и четкие инструкции) \n (Сделай шутки про мои проблемы и в конце добавь какой фильм соответствует моей проблеме)")

@router.message(Reg.Commitment)
async def reg_CallToAction(message: Message, state: FSMContext):
    await state.update_data(Commitment=message.text)
    await state.set_state(Reg.CallToAction)
    await message.answer("Write your typical Call-To-Action(e.g. Ready to tackle challenges? Let's get to work) \n Какой у тебя типичный призыв к действию? (Например: Готов разобраться с проблемами? Давай работать) \n (Слыш ты как телка небудь, давай ради родителей и детей пахай, ты через 5 лет собой будешь гордится)")

@router.message(Reg.CallToAction)
async def reg_ainame(message: Message, state: FSMContext):
    await state.update_data(CallToAction=message.text)
    await state.set_state(Reg.ai_name)
    await message.answer("What name you prefer to me(e.g. Alex, Noor, Optimus, Elon, Temur, SquidPuppy) \n Какое имя ты предпочитаешь для меня? (Например: Алекс, Нур, Оптимус, Илон, Темур, SquidPuppy)")

@router.message(Reg.ai_name)
async def reg_finish(message: Message, state:FSMContext):
    userid = str(message.from_user.id)
    await state.update_data(ai_name=message.text)
    await state.update_data(user_id=userid)
    data = await state.get_data()
    data = {
            userid: {
                'ai_name': data["ai_name"],
                'name': data["name"],
                'Experience': data["Experience"],
                'Approach': data["Approach"],
                'Mission': data["Mission"],
                'Commitment': data["Commitment"],
                'CallToAction': data["CallToAction"]
            }
            
    }
    userid_data = data[userid]
    one_row_data = '"' + "userid: " + ", ".join(f"{key}={value}" for key, value in userid_data.items()) + '"'
    if userid not in user_chat_histories:
            user_chat_histories[userid] = []

        # Add user message to history
    user_chat_histories[userid].append({
        "role": "user",
        "parts": [{"text": one_row_data}]
    })
    save_chat_history()
    with open(USER_PROFILE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    global user_profile  # Important: Access the global variable
    user_profile.update(data) # Update in-memory data
    # user_profile = load_user_profile() # <--- OLD CODE
    await message.answer(f"You fineshed up you registration.....🎊 \n Вы завершили регистрацию... \n {data}")
    await state.clear()


@router.message(Command("audio_plan"))
async def audio_plan(message: Message):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await message.answer_invoice(
        title="Extending limits for audio/Расширить лимиты для аудио",
        description="Your going to extend you limit by 10 additional tries/Вы собираетесь продлить свой лимит на 10 дополнительных попыток.",
        payload='fundup_audio_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )

### testing / for developers and those who understand only
# @router.message(Command("jasur"))
# async def jasur(message: Message):
#     result = await bot.get_star_transactions(offset=0, limit=100)
#     with open("txt.txt", 'w', encoding="utf-8") as files:
#         files.write(str(result.transactions))# you should use the last star_transaction since the time zone may not match, or you can calculate the time zone and find the transaction you want
#     await bot.refund_star_payment(user_id=message.from_user.id, telegram_payment_charge_id='stxzmNSmhzhfmd9CMdU7qvRCXhWIcZCrLBsptM7nPY1cLd1PL_xJ71V0m6fJfp0B4qNvI4civuX44nh89MrltZGA-P5tugfYe8gUvhk8rHkd6o')
### testing / for developers and those who understand only


@router.message(Command('fund'))
async def start_fund(message: Message):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await message.answer_invoice(
        title="Extend limits/Расширить дневные лимиты",
        description="Your going to extend you limit by 10 additional tries/Вы собираетесь продлить свой лимит на 10 дополнительных попыток.",
        payload='fundup_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )

@router.pre_checkout_query()
async def pre_checkout_handler(event: PreCheckoutQuery):
    await event.answer(True)





@router.message(F.successful_payment.invoice_payload == "fundup_limits")
async def successful_payment(message: Message):
    user_id = str(message.from_user.id)
    await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id) # for testing purposes \ it will refund the stars a.k.a it will give your stars(money) back, use it for test purposes
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    limit_manager.funded_limites(user_id=user_id)
    await message.reply(f"✅ LIMIT check! {remaining_limits} uses remaining today.\n ✅ ПРОВЕРка ЛИМИТА! {remaining_limits} Попыток на сегодня.")

    await message.answer("Your stuff has been updated😍\n Ваши материалы обновлены😍", reply_markup=kb.back_to_main)
###
@router.message(F.successful_payment.invoice_payload == "fundup_audio_limits")
async def successful_payment_audio(message: Message):
    user_id = str(message.from_user.id)
    await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id) # for testing purposes \ it will refund the stars a.k.a it will give your stars(money) back, use it for test purposes
    limit_manager.funded_limites_auido(user_id=user_id)
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    await message.answer("Your stuff has been updated😍\n Ваши материалы обновлены😍", reply_markup=kb.back_to_main)
    await message.reply(f"✅ LIMIT check! {remaining_limits} uses remaining today.\n ✅ ПРОВЕРка ЛИМИТА! {remaining_limits} Попыток на сегодня.")
###


@router.message(Command('history'))
async def user_history(message: Message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_chat_histories or not user_chat_histories[user_id]:
        await message.answer("📜 No chat history found. \n История чата не найдена")
        return

    history_text = "\n\n".join(
        f"{entry['role'].capitalize()}: {entry['parts'][0]['text']}"
        for entry in user_chat_histories[user_id]
    )

    await message.answer(f"📜 Chat History/История чата:\n\n{history_text}")

@router.message(Command('end'))
async def end_current(message: Message):
    user_id = str(message.from_user.id)
    user_chat_histories[user_id] = []  # Clear history for new conversation
    save_chat_history()
    await message.answer("🚮 History has been cleared \n 🚮История была очищена.")

@router.message(Command('new'))
async def end_current_start_new(message: Message):
    user_id = str(message.from_user.id)
    user_chat_histories[user_id] = []  # Clear history for new conversation
    save_chat_history()
    await message.answer("🔄 New chat session started. \n 🔄 Начался новый сеанс чата")

@router.message(F.voice)
async def handle_audio(message: Message):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    user_id = str(message.from_user.id)  # Convert to string for JSON compatibility
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    can_auido_proceed, remaining_audio_limits = await limit_manager.use_limit_audio(user_id)
    if not can_proceed:
        reset_time_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"⛔️ You've reached your daily limit. Limits reset at: {reset_time_str} \n ⛔️ Вы использовали все сегодняшние попытки. Лимит перезагрузится в: {reset_time_str} \nyou can buy additional limits by running '/fund'")
        return
    elif not can_auido_proceed:
        await message.reply(f"🛑Sorry you haven't bought audio usage or you reached your limit, you can buy audio limits by running '/audio_plan'")
        return
    x = await load_voice_settings()
    if x == None:
        await message.answer("Pealse chose a voice and try again", reply_markup=kb.aviable_voices)
        return
    the_x = await message.answer("active listening...")

    split_tup = os.path.splitext(message.voice.file_id)
    file_name = f"{split_tup[0]}_{message.from_user.id}{split_tup[1]}.ogg"
    await bot.download(message.voice.file_id, file_name)

    # # Load the model (choose "tiny", "base", "small", "medium", or "large" as needed)
    whisper_model = whisper.load_model("small")

    # # Transcribe the OGG audio file
    result = whisper_model.transcribe(file_name)
    final_result = result["text"]
    user_id = str(message.from_user.id)  # Convert to string for JSON compatibility

    sent_message = await the_x.edit_text("Recording something important, probably...\n Веду глубокую беседу со своим микрофоном... ")
    
    respone_txt = await generate_the_content(message.text,user_id)

    await sent_message.edit_text(respone_txt, parse_mode="HTMl")

    API_KEY = ELEVENLABS_API_KEY
    TEXT = str(respone_txt)
    VOICE_ID = x["default_voice_id"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    data = {
        "text": TEXT,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    response_audio = requests.post(url, json=data, headers=headers)
    file_name_voice = f"output_{message.from_user.id}.ogg"
    if response_audio.status_code == 200:
        with open(file_name_voice, "wb") as f:
            f.write(response_audio.content)
        cat = FSInputFile(file_name_voice, filename=f"output_{file_name_voice}_{message.from_user.id}.ogg")
        await message.answer_voice(voice=cat, caption="Dont listen ⬆️")
    else:
        message.answer("Error:", response_audio.text)
    await sent_message.delete()

    os.remove(file_name)
    try:
        os.remove(file_name_voice)
        await message.reply(f"✅ Command processed! {remaining_limits} uses remaining today.\n ✅ Запрос успешен! {remaining_limits} Попыток на сегодня.")
        await message.reply(f"🎊 Command processed! {remaining_audio_limits} audio uses remaining.\n ✅ Запрос успешен! {remaining_audio_limits} Аудио попыток.")
    except FileNotFoundError:
        await message.answer("Error: audio api has reached it's limits \n come back next month or donate")

@router.message(Command(commands=["au", "audio"])) #/au how to fix my pose
async def audio_respone(message: Message, command: CommandObject):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    user_id = str(message.from_user.id)  # Convert to string for JSON compatibility
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    can_auido_proceed, remaining_audio_limits = await limit_manager.use_limit_audio(user_id)
    if not can_proceed:
        reset_time_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"⛔️ You've reached your daily limit. Limits reset at: {reset_time_str} \n ⛔️ Вы использовали все сегодняшние попытки. Лимит перезагрузится в: {reset_time_str} \nyou can buy additional limits by running '/fund'")
        return
    elif not can_auido_proceed:
        await message.reply(f"🛑Sorry you haven't bought audio usage or you reached your limit, you can buy audio limits by running '/audio_plan'")
        return
    x = await load_voice_settings()
    if x == None:
        await message.answer("Pealse chose a voice and try again", reply_markup=kb.aviable_voices)
        return
    sent_message = await message.answer("Recording something important, probably...\n Веду глубокую беседу со своим микрофоном... ")

    
    respone_txt = await generate_the_content(message.text,user_id)

    await sent_message.edit_text(respone_txt, parse_mode="HTMl")

    API_KEY = ELEVENLABS_API_KEY
    x = await load_voice_settings()
    VOICE_ID = x["default_voice_id"]
    TEXT = str(respone_txt)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    data = {
        "text": TEXT,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    response = requests.post(url, json=data, headers=headers)
    file_name = f"output_{message.from_user.id}.ogg"
    if response.status_code == 200:
        with open(file_name, "wb") as f:
            f.write(response.content)
        cat = FSInputFile(file_name, filename=f"output_{file_name}_{message.from_user.id}.ogg")
        await message.answer_voice(voice=cat)
    else:
        message.answer("Error:", response.text)

    await sent_message.delete()
    try:
        os.remove(file_name)
        await message.reply(f"✅ Command processed! {remaining_limits} uses remaining today.\n ✅ Запрос успешен! {remaining_limits} Попыток на сегодня.")
        await message.reply(f"🎊 Command processed! {remaining_audio_limits} audio uses remaining.\n ✅ Запрос успешен! {remaining_audio_limits} Аудио попыток.")
    except FileNotFoundError:
        await message.answer("Error: audio api has reached it's limits \n come back next month or donate")

@router.message(F.text)
async def the_text(message: Message, state: FSMContext):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    if message.text == None:
        return
    await state.set_state(Gen.wait)
    user_id = str(message.from_user.id)  # Convert to string for JSON compatibility
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)

    if not can_proceed:
        reset_time_str = reset_time.strftime("%Y-%m-%d %H:%M:%S")
        await message.reply(f"⛔️ You've reached your daily limit. Limits reset at: {reset_time_str} \n ⛔️ Вы использовали все сегодняшние попытки. Лимит перезагрузится в: {reset_time_str} \nyou can buy additional limits by running '/fund'")
        return

    sent_message = await message.answer("Doing something important, probably...\n Веду глубокую беседу со своими мозгами ", parse_mode="HTMl")

    x = await generate_the_content(message.text,user_id)

    await sent_message.edit_text(x, parse_mode="HTMl")


    await message.reply(f"✅ Command processed! {remaining_limits} uses remaining today.\n ✅ Запрос успешен! {remaining_limits} Попыток на сегодня.")
    await state.clear()
