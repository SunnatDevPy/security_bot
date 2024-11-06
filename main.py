import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand, BotCommandScopeChatAdministrators, ChatMemberAdministrator, BotCommandScopeChat

from bot.group import group_router
from config import conf
from db import database


async def on_start(bot: Bot):
    await database.create_all()
    commands_admin = [
        BotCommand(command='start', description="Bo'tni ishga tushirish"),
        BotCommand(command='ban', description="1 kunga ban berish"),
        BotCommand(command='kick', description="Guruxdan chiqarish"),
        BotCommand(command='words', description="So'zlar")
    ]
    await bot.set_my_commands(commands=commands_admin)


async def main():
    dp = Dispatcher()
    dp.startup.register(on_start)
    dp.include_router(group_router)
    bot = Bot(token=conf.bot.BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

# 1065  docker login
# 1068  docker build -t nickname/name .
# 1071  docker push nickname/name

# docker run --name db_mysql -e MYSQL_ROOT_PASSWORD=1 -d mysql
