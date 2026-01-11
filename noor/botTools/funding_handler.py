from aiogram import Bot
from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.types import Message, LabeledPrice
from aiogram.filters import Command
from aiogram.types import PreCheckoutQuery


from noor.botClasses import Gen
from noor.botTools.subscription import sub_chek
from config import limit_manager, TOKEN, CHANNEL_LINK
import noor.keyboards as kb
from noor.instructions import greeting

bot = Bot(token=TOKEN)
FundingRouter = Router()

@FundingRouter.callback_query(F.data == "fundup")
async def fundup(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    await callback.message.answer_invoice(
        title="Extend limits/Расширить дневные лимиты",
        description="Your going to extend you limit by 10 additional tries/Вы собираетесь продлить свой лимит на 10 дополнительных попыток.",
        payload='fundup_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )



@FundingRouter.callback_query(F.data == 'fund_up_audio')
async def fund_the_audio(callback: CallbackQuery):
    await callback.answer("Proccesing...")
    await callback.message.answer_invoice(
        title="Extending limits for audio/Расширить лимиты для аудио",
        description="Your going to extend your audio limit by 10 additional tries/Вы собираетесь продлить свой аудио лимит на 10 дополнительных попыток.",
        payload='fundup_audio_limits',
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=1)]
    )
@FundingRouter.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(greeting, reply_markup=kb.settings)



@FundingRouter.message(Gen.wait)
async def stop_flood(message: Message):
    await message.answer("Wait one requests at a time \nПодождите ваш запрос генерируется.")



@FundingRouter.message(Command('fund'))
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

@FundingRouter.pre_checkout_query()
async def pre_checkout_handler(event: PreCheckoutQuery):
    await event.answer(True)





@FundingRouter.message(F.successful_payment.invoice_payload == "fundup_limits")
async def successful_payment(message: Message):
    user_id = str(message.from_user.id)
    await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id) # for testing purposes \ it will refund the stars a.k.a it will give your stars(money) back, use it for test purposes
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    limit_manager.funded_limites(user_id=user_id)
    await message.reply(f"✅ LIMIT check! {remaining_limits} uses remaining today.\n ✅ ПРОВЕРка ЛИМИТА! {remaining_limits} Попыток на сегодня.")

    await message.answer("Your stuff has been updated😍\n Ваши материалы обновлены😍", reply_markup=kb.back_to_main)
###
@FundingRouter.message(F.successful_payment.invoice_payload == "fundup_audio_limits")
async def successful_payment_audio(message: Message):
    user_id = str(message.from_user.id)
    await bot.refund_star_payment(message.from_user.id, message.successful_payment.telegram_payment_charge_id) # for testing purposes \ it will refund the stars a.k.a it will give your stars(money) back, use it for test purposes
    limit_manager.funded_limites_auido(user_id=user_id)
    can_proceed, remaining_limits, reset_time = await limit_manager.use_limit(user_id)
    await message.answer("Your stuff has been updated😍\n Ваши материалы обновлены😍", reply_markup=kb.back_to_main)
    await message.reply(f"✅ LIMIT check! {remaining_limits} uses remaining today.\n ✅ ПРОВЕРка ЛИМИТА! {remaining_limits} Попыток на сегодня.")
###
