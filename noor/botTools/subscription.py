from config import MANDOTARY_SUBSCRIPTION, CHANNEL_ID, TOKEN
from aiogram import F, Bot
from aiogram.types import ChatJoinRequest, CallbackQuery
from aiogram import Router

bot = Bot(token=TOKEN)
subscribtion_router = Router() 


pending_requests = set()


@subscribtion_router.chat_join_request()
async def handle_join_request(update: ChatJoinRequest):
    pending_requests.add(update.from_user.id)
    # Optionally notify admins or log the request


async def sub_chek(user_id):
    if MANDOTARY_SUBSCRIPTION:
        if user_id in pending_requests or await is_subscribed(user_id=user_id):
            return True
        else:
            return False
    else:
        return True


async def is_subscribed(user_id: int) -> bool:
    if MANDOTARY_SUBSCRIPTION:
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            return member.status in ("member", "administrator", "creator")
        except Exception:
            return False
    else:
        return True
    

@subscribtion_router.callback_query(F.data == "subchek")
async def subchek(callback: CallbackQuery):
    if not await sub_chek(callback.from_user.id):
        await callback.answer("Your not subscribed yet",)
        return
    await callback.answer("Your are okay to go")