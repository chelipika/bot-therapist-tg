from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Main mune")]
],
        resize_keyboard=True,
        input_field_placeholder="Write smth...")

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="History", callback_data="history_callback"), InlineKeyboardButton(text="Fund up", callback_data="fundup")],
    [InlineKeyboardButton(text="Profile", url="https://t.me/notesworth/50")]
])

back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Back🔙", callback_data="back")]
])
