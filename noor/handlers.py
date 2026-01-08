import json
import whisper
import aiofiles
import requests
import os
from aiogram import F, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckout

from aiogram.types import Query, CallbackQuery, FSInputFile, ChatJoinRequest
from aiogram.types import ChatMemberUpdated
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
import google.generativeai as genai
from config import GEMINI_API_KEY, ELEVENLABS_API_KEY, TOKEN, CHANNEL_ID, CHANNEL_LINK, MANDOTARY_SUBSCRIPTION,CHAT_HISTORY_FILE,USER_PROFILE_FILE, VOICE_SETTINGS_FILE,ALL_USERS_DB, limit_manager
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import database.requests as rq
from noor.instructions import INSTRUCTIONS_OF_AI, greeting, voices_text
bot = Bot(token=TOKEN)
import noor.keyboards as kb

from voicemsg.voice_handler import load_voice_settings, save_voice_settings
from botClasses import Reg, AdvMsg, GroupMsg,Gen
from aiMsg.chat_history import load_chat_history, load_user_profile, load_all_user,save_chat_history, user_chat_histories, user_profile
from botTools.subscription import sub_chek, is_subscribed, pending_requests
from aiMsg.responseGenerator import generate_the_content
from botTools.userLitmitMNG import UserLimitManager


# Ensure dictionary format
if not isinstance(user_chat_histories, dict):
    user_chat_histories = {}





router = Router()

@router.my_chat_member()
async def handle_new_chat(update: ChatMemberUpdated):
    chat_id = update.chat.id
    await rq.set_group(chat_id)
    # Save chat_id to your database or list

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    await rq.set_user(tg_id=user_id)

    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await message.answer(f"Hi\Привет {message.from_user.full_name}\n {greeting}", reply_markup=kb.settings)


