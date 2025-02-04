import asyncio
from config import TOKEN
from aiogram import Bot, Dispatcher
from noor.handlers import router


bot = Bot(token=TOKEN)
dp = Dispatcher()




async def main():
    print("BOT start polling.....")
    dp.include_router(router=router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")

