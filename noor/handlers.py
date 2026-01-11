from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ChatMemberUpdated
from aiogram import Router
from config import TOKEN, CHANNEL_LINK
import database.requests as rq


from noor.instructions import greeting
import noor.keyboards as kb
from noor.botTools.subscription import sub_chek, subscribtion_router
from noor.aiMsg.responseGenerator import AimsgRouter
from noor.aiMsg.chat_history import ChatHistoryRouter
from noor.voicemsg.voice_responses import VoiceRouter
from noor.voicemsg.voice_handler import VoiceHandlerRouter
from noor.botTools.user_profile_handler import UserProfileRouter
from noor.botTools.funding_handler import FundingRouter
from noor.botTools.msg_to_all_users import MsgAllUsersRouter

bot = Bot(token=TOKEN)
router = Router()
router.include_router(subscribtion_router)
router.include_router(AimsgRouter)
router.include_router(ChatHistoryRouter)
router.include_router(VoiceRouter)
router.include_router(VoiceHandlerRouter)
router.include_router(UserProfileRouter)
router.include_router(FundingRouter)
router.include_router(MsgAllUsersRouter)

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


