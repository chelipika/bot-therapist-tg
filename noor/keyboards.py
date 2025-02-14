from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_LINK
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Main mune")]
],
        resize_keyboard=True,
        input_field_placeholder="Write smth...")

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="History", callback_data="history_callback")],
    [InlineKeyboardButton(text="Profile", callback_data="profile")],
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
    [InlineKeyboardButton(text="Preview of the voices", url="https://chelipika.github.io/bot-therapist-tg/")],
    [InlineKeyboardButton(text="Back🔙", callback_data="back")]
])


profile_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Show my profile", callback_data="show_users_profliee"), InlineKeyboardButton(text="Create/change profile", callback_data="create_update_profile")],
    [InlineKeyboardButton(text="Back🔙", callback_data="back")]

])
subscribe_channel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Subscribe", url=CHANNEL_LINK)],
    [InlineKeyboardButton(text="Check", callback_data="subchek")]
])

profile_creating = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Create your profile", callback_data="create_update_profile")]
])
