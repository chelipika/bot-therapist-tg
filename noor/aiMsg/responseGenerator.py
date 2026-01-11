import os
import google.generativeai as genai
import asyncio

from aiogram import F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from noor.botClasses import Gen
from noor.botTools.subscription import sub_chek
from config import limit_manager
import noor.keyboards as kb
from noor.aiMsg.chat_history import user_chat_histories, save_chat_history
from config import GEMINI_API_KEY, CHANNEL_LINK, TOKEN
from noor.instructions import INSTRUCTIONS_OF_AI
from aiogram import Router

AimsgRouter = Router()
bot = Bot(token=TOKEN)



os.environ["GENAI_API_ENDPOINT"] = "us-central1-genai.googleapis.com"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=INSTRUCTIONS_OF_AI
)

async def generate_the_content(text: str, userid: int,message: Message):
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
    response = await chat_session.send_message_async(text, stream=True)
    full_text = ""
    async for chunk in response:
        if chunk.text:
            full_text += chunk.text
            try:
                await message.bot.send_message_draft(
                    chat_id=message.chat.id,
                    draft_id=message.message_id,
                    text=full_text,
                    message_thread_id=message.message_thread_id
                )
                await asyncio.sleep(0.2)  # Slight delay to avoid hitting rate limits
            except Exception as e:
                await message.answer(f"ERROR: {e}")

    # Final message without blinking cursor
    await message.answer(full_text, parse_mode="HTML")
    response_text = full_text

    # Save AI response to history
    user_chat_histories[userid].append({
        "role": "model",
        "parts": [{"text": response_text}]
    })
    save_chat_history()
    return response_text

@AimsgRouter.message(Command('end'))
async def end_current(message: Message):
    user_id = str(message.from_user.id)
    user_chat_histories[user_id] = []  # Clear history for new conversation
    save_chat_history()
    await message.answer("🚮 History has been cleared \n 🚮История была очищена.")

@AimsgRouter.message(Command('new'))
async def end_current_start_new(message: Message):
    user_id = str(message.from_user.id)
    user_chat_histories[user_id] = []  # Clear history for new conversation
    save_chat_history()
    await message.answer("🔄 New chat session started. \n 🔄 Начался новый сеанс чата")


@AimsgRouter.message(F.text)
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

    # sent_message = await message.answer("Doing something important, probably...\n Веду глубокую беседу со своими мозгами ", parse_mode="HTMl")

    await generate_the_content(message.text,user_id,message)

    # await sent_message.edit_text(x, parse_mode="HTMl")
    await state.clear()
