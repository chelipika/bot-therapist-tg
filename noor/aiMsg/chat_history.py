import os
import json
from aiogram import Router
from aiogram.types import Query, CallbackQuery, FSInputFile, Message
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram import F, Bot
from aiogram.exceptions import TelegramBadRequest


from config import CHAT_HISTORY_FILE, USER_PROFILE_FILE, ALL_USERS_DB
import noor.keyboards as kb


router = Router()


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

user_profile = load_user_profile()

def load_all_user():
    if os.path.exists(ALL_USERS_DB):
        with open(ALL_USERS_DB, "r") as f:
            return json.load(f)
    return {}
# Save chat history to the file
user_chat_histories = load_chat_history()

def save_chat_history():
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(user_chat_histories, f, indent=4)


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
