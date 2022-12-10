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
            InlineKeyboardButton(servises[1].title, callback_data=servises[1].title),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_four_button(servises):
    keyboard = [
        [
            InlineKeyboardButton(servises[0].title, callback_data=servises[0].title),
        ],
        [
            InlineKeyboardButton(servises[1].title, callback_data=servises[1].title),
        ],
        [
            InlineKeyboardButton(servises[2].title, callback_data=servises[2].title),
        ],
        [
            InlineKeyboardButton(servises[3].title, callback_data=servises[3].title),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def keyboard_five_button(servises):
    keyboard = [
        [
            InlineKeyboardButton(servises[0].title, callback_data=servises[0].title),
        ],
        [
            InlineKeyboardButton(servises[1].title, callback_data=servises[1].title),
        ],
        [
            InlineKeyboardButton(servises[2].title, callback_data=servises[2].title),
        ],
        [
            InlineKeyboardButton(servises[3].title, callback_data=servises[3].title),
        ],
        [
            InlineKeyboardButton(servises[4].title, callback_data=servises[4].title),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def keyboard_one_specialist_button(specialists):
    keyboard = [
        [
            InlineKeyboardButton(specialists[0].name, callback_data=specialists[0].name),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_two_specialist_button(specialists):
    keyboard = [
        [
            InlineKeyboardButton(specialists[0].name, callback_data=specialists[0].name),
        ],
        [
            InlineKeyboardButton(specialists[1].name, callback_data=specialists[1].name),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_four_specialist_button(specialists):
    keyboard = [
        [
            InlineKeyboardButton(
                f'Мастер {specialists[0].name}: {", ".join([service.title for service in specialists[0].services.all()])}',
                callback_data=specialists[0].name),
        ],
        [
            InlineKeyboardButton(
                f'Мастер {specialists[1].name}: {", ".join([service.title for service in specialists[1].services.all()])}',
                callback_data=specialists[1].name),
        ],
        [
            InlineKeyboardButton(
                f'Мастер {specialists[2].name}: {", ".join([service.title for service in specialists[2].services.all()])}',
                callback_data=specialists[2].name),
        ],
        [
            InlineKeyboardButton(
                f'Мастер {specialists[3].name}: {", ".join([service.title for service in specialists[2].services.all()])}',
                callback_data=specialists[3].name),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


