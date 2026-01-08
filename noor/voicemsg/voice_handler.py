import os
import aiofiles
import json

from aiogram import Router
from aiogram.types import Message, LabeledPrice, PreCheckout, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram import F


from config import VOICE_SETTINGS_FILE
from instructions import voices_text
import noor.keyboards as kb

router = Router()



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


@router.message(Command("audio_plan"))
async def audio_plan(message: Message):
    await message.answer_invoice(
        title="Extending limits for audio/Расширить лимиты для аудио",
        description="Your going to extend you limit by 10 additional tries/Вы собираетесь продлить свой лимит на 10 дополнительных попыток.",
        payload='fundup_audio_limits',
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

