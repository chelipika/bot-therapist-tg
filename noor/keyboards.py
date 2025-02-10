from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Main mune")]
],
        resize_keyboard=True,
        input_field_placeholder="Write smth...")

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="History", callback_data="history_callback"), InlineKeyboardButton(text="Fund up Messages", callback_data="fundup")],
    [InlineKeyboardButton(text="Profile", callback_data="profile"), InlineKeyboardButton(text="Audio Fund", callback_data="fund_up_audio")],
    [InlineKeyboardButton(text="Change audio voice", callback_data="voice_change")]
])

back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Back🔙", callback_data="back")]
])

history_text = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="send it as file", callback_data="send_as_file_history")],
    [InlineKeyboardButton(text="Back🔙", callback_data="back")]
])


aviable_voices = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Rachel", callback_data="Rachel_change_voice"), InlineKeyboardButton(text="Domi", callback_data="Domi_change_voice")],
    [InlineKeyboardButton(text="Joseph", callback_data="Joseph_change_voice"), InlineKeyboardButton(text="Liam", callback_data="Liam_change_voice")],
    [InlineKeyboardButton(text="Back🔙", callback_data="back")]
])