from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models.model import Words


async def words():
    kb = InlineKeyboardBuilder()
    for i in await Words.get_all():
        kb.add(*[InlineKeyboardButton(text=i.text, callback_data='words_'),
                 InlineKeyboardButton(text="❌", callback_data=f'words_delete_{i.id}')])
    kb.row(InlineKeyboardButton(text="So'z qo'shish", callback_data='words_add'))
    kb.adjust(2)
    return kb.as_markup()


async def start():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="Guruxga qo'shish", url='https://t.me/stock_security_bot?startgroup=true'))
    kb.adjust(2)
    return kb.as_markup()
