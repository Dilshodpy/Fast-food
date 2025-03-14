from aiogram import executor

if __name__ == "__main__":
    from handlers import *
    print("Бот запущен: @fffooooddd_bot")
    executor.start_polling(dp, skip_updates=True)
