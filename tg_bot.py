import asyncio
from aiogram import Bot, Dispatcher
from handlers import hd_main

TOKEN = "6421226180:AAHAVEuqJYQt_DSe_Oqi5XyxuhOw6ODD1w8"

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(hd_main.router)
    await bot.delete_webhook(drop_pending_updates=True)
    tasks = [
        asyncio.create_task(dp.start_polling(bot))
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
