from aiogram import Bot, Dispatcher, executor, types
from db_utils import last_hour_cars
import time
from datetime import datetime
import sys
sys.stdout.flush()


TOKEN = "5875792720:AAGhbhgbEu4sD4qPjr9dIN19WdcMnFcK9pA"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


@dp.message_handler()
async def start_handler(message: types.Message):
    while (True):
        try:
            cars_number = last_hour_cars()
            print(f"[{str(datetime.utcnow())}]", cars_number)
            await bot.send_message(709029307, f'Hi. There is {cars_number} on last hour')
            time.sleep(3600)
        except Exception as e:
            print(f"[{str(datetime.utcnow())}]", e)

if __name__ == '__main__':
    print(f"[{str(datetime.utcnow())}]",
          "bot has started successfully", flush=True)
    while (True):
        try:
            executor.start_polling(dp)
        except Exception as e:
            print(f"[{str(datetime.utcnow())}]", e)
