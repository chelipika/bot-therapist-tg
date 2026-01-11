import os
import whisper
import requests

from aiogram import Bot
from aiogram import Router
from aiogram import F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, ChatJoinRequest

from noor.botClasses import Gen
from noor.botTools.subscription import sub_chek
from noor.voicemsg.voice_handler import load_voice_settings
from noor.aiMsg.responseGenerator import generate_the_content
from config import ELEVENLABS_API_KEY, limit_manager, TOKEN, CHANNEL_LINK
import noor.keyboards as kb



bot = Bot(token=TOKEN)
VoiceRouter = Router()




@VoiceRouter.message(F.voice)
async def handle_audio(message: Message, state: FSMContext):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await state.set_state(Gen.wait)
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
        await message.reply(f"🎊 Command processed! {remaining_audio_limits} audio uses remaining.\n ✅ Запрос успешен! {remaining_audio_limits} Аудио попыток.")
    except FileNotFoundError:
        await message.answer("Error: audio api has reached it's limits \n come back next month or donate")
    await state.clear()

@VoiceRouter.message(Command(commands=["au", "audio"])) #/au how to fix my pose
async def audio_respone(message: Message, command: CommandObject,  state: FSMContext):
    if not await sub_chek(message.from_user.id):
        await message.answer(f"Subscribe first, Подпишитесь: \n{CHANNEL_LINK}", reply_markup=kb.subscribe_channel)
        return
    await state.set_state(Gen.wait)
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
        await message.reply(f"🎊 Command processed! {remaining_audio_limits} audio uses remaining.\n ✅ Запрос успешен! {remaining_audio_limits} Аудио попыток.")
    except FileNotFoundError:
        await message.answer("Error: audio api has reached it's limits \n come back next month or donate")
    await state.clear()
