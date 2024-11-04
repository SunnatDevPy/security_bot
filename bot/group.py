import re
from datetime import timedelta, datetime

from aiogram import Router, Bot, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ChatPermissions

from bot.buttuns.simple import start, words
from db.models.model import Words, User

user_warnings = {}

group_router = Router()


def contains_link(message: Message):
    return bool(re.search(r'http[s]?://', message.text))


async def contains_bad_word(message: Message):
    for word in await Words.get_all():
        if word.text.lower() in message.text.lower():
            return True
    return False


text = """
Salom👋
Man reklamalarni, 🔞18+ Rasm videolar va har xil behayo so'zlarni guruxlarda o'chirib beraman👨🏻‍✈️"""


@group_router.message(CommandStart(), F.chat.type == 'private')
async def send_welcome(message: Message, bot: Bot):
    await message.answer(text, reply_markup=await start())


@group_router.message(F.new_chat_member)
async def on_bot_added_to_group(message: Message, bot: Bot):
    if int(message.new_chat_member['id']) == int(bot.id):
        await bot.send_message(
            message.chat.id,
            f"Bot guruxga qo'shildi: {message.chat.title} (Gurux ID: {message.chat.id})"
        )


@group_router.message(F.chat.type.in_(['group', 'supergroup']))
async def filter_message(message: Message, bot: Bot):
    user = await User.get(message.from_user.id)
    if user == None:
        from_user = message.from_user
        user = await User.create(id=message.from_user.id, username=from_user.username,
                                 full_name=from_user.first_name)
    else:
        pass
    if contains_link(message):
        await message.delete()
        await message.answer(f"{message.from_user.first_name}, link tashlamang!")
        await User.update(user.id, count=user.count + 1)

    elif await contains_bad_word(message):
        await message.delete()
        await message.answer(f"{message.from_user.first_name}, haqoratli so'zlar yozmang!")
        await User.update(user.id, count=user.count + 1)

    if message.sticker:
        await message.delete()
        await message.answer(f"{message.from_user.first_name}, sticker tashlamang!")

    user: User = await User.get(message.from_user.id)
    if user.count == 3:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=True),
            until_date=message.date + timedelta(seconds=15),
            request_timeout=15
        )
        await User.update(message.from_user.id, count=0)


class AddAdmin(StatesGroup):
    user_id = State()


@group_router.message(Command("words"))
async def add_bad_word(message: Message, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ['administrator', 'creator']:
        await message.reply("Sizda xuquq yo'q.")
        return

    await message.answer("So'zlar to'plami", reply_markup=await words())


@group_router.callback_query(F.data.startswith('words_'))
async def delete_admins(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    await call.answer()
    if data[1] == 'add':
        await call.message.delete()
        await state.set_state(AddAdmin.user_id)
        await call.message.answer("Yangi so'z qo'shing")
    elif data[1] == 'delete':
        try:
            await Words.delete(int(data[-1]))
            await call.message.edit_text("So'zlar to'plami", reply_markup=await words())
        except:
            await call.message.answer('Xatolik yuz berdi')


@group_router.message(AddAdmin.user_id)
async def add_admin(call: Message, state: FSMContext):
    await Words.create(text=call.text)
    await call.answer("Yangi so'z qo'shildi")
    await call.answer("So'zlar to'plami", reply_markup=await words())
    await state.clear()


@group_router.message(Command("ban"))
async def ban_user(message: Message, bot: Bot):
    if message.reply_to_message:
        user_to_ban = message.reply_to_message.from_user.id

        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await message.reply("Sizda xuquq yo'q.")
            return

        try:
            await bot.restrict_chat_member(
                message.chat.id,
                user_to_ban,
                ChatPermissions(can_send_messages=False),
                until_date=datetime.now() + timedelta(days=7)
            )
            await message.reply(f"Foydalanuvchi 7 kunga bloklandi.")
        except Exception as e:
            pass
    else:
        await message.reply("Komanda ishga tushishi uchun xabarga yo'naltiring.")


@group_router.message(Command("kick"))
async def kick_user(message: Message, bot: Bot):
    if message.reply_to_message:
        user_to_kick = message.reply_to_message.from_user.id

        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ['administrator', 'creator']:
            await message.reply("Sizda xuquq yo'q.")
            return
        try:
            await bot.ban_chat_member(message.chat.id, user_to_kick)
            await bot.unban_chat_member(message.chat.id, user_to_kick)

            await message.reply("Foydalanuvchi guruxda chiqarildi")
        except Exception as e:
            pass
    else:
        await message.reply("Komanda ishga tushishi uchun xabarga yo'naltiring.")


UNWANTED_KEYWORDS = ['18+', 'xxx', 'adult', 'porn']


@group_router.message(ContentType.VIDEO)
async def check_video_content(message: Message, bot: Bot):
    # Video caption yoki fayl nomini tekshirish
    if message.caption:
        caption = message.caption.lower()
        if any(keyword in caption for keyword in UNWANTED_KEYWORDS):
            await message.reply("⚠️ Ushbu video nomaqbul kontentni o'z ichiga olishi mumkin!")
            await bot.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
            await bot.unban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
            return

    video = await message.video.get_file()
    if any(keyword in video.file_path.lower() for keyword in UNWANTED_KEYWORDS):
        await message.reply("⚠️ Ushbu video nomaqbul kontentni o'z ichiga olishi mumkin!")
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
