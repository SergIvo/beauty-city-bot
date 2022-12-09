from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


def keyboard_one_button(servises):
    keyboard = [
        [
            InlineKeyboardButton(servises[0].title, callback_data=servises[0].title),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_two_button(servises):
    keyboard = [
        [
            InlineKeyboardButton(servises[0].title, callback_data=servises[0].title),
        ],
        [
            InlineKeyboardButton(servises[1].title, callback_data=servises[0].title),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)