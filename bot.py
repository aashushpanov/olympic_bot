import asyncio

from loader import dp, bot
from handlers.users.admin import register_admin
from handlers.users.user import register_student
from states.user import register_user_handlers
from commands.user import set_user_commands


async def main():
    register_admin(dp)
    register_student(dp)
    register_user_handlers(dp)
    await set_user_commands(bot)

    await dp.start_polling(dp)


if __name__ == '__main__':
    asyncio.run(main())
