import os
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from telegram import Update, Bot
from dotenv import load_dotenv
from ...models import User, Service, Specialist, Salon, Purchase
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.utils.request import Request
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

saloon = ''
master = ''
service = ''

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR, FIVE = range(5)

CALLBACK_SERVICE = 'callback_service'
PERSONAL_AREA = 'personal_area'
CHOICE_SALOON = 'choice_saloon'
CHOICE_MASTER = 'choice_master'
CHOICE_SERVICE = 'choice_service'
FIRST_MASTER = 'first_master'
SECOND_MASTER = 'second_master'
THIRD_MASTER = 'third_master'
FOURTH_MASTER = 'fourth_master'
SALOON_PIONERSKAYA = 'saloon_pionerskaya'
SALOON_MOSKOVSKAYA = 'saloon_moskovskaya'
SALOON_LENINGRADSKAYA = 'saloon_leningradskaya'
SALOON_KAMISHOVAYA = 'saloon_kamishovaya'
HAIRCUT = 'haircut'
MANICURE = 'manicure'
SOLARIUM = 'solarium'
COLORING = 'coloring'
END = ''

TITLES = {
    'callback_service': 'Записаться на услугу',
    'personal_area': 'Личный кабинет',
    'choice_saloon': 'Выбор салона',
    'choice_master': 'Выбор мастера',
    'choice_service': 'Выбор услуги',
    'first_master': 'Мария',
    'second_master': 'Анна',
    'third_master': 'Вика',
    'fourth_master': 'Лиза',
    'saloon_pionerskaya': 'Салон на Пионерской 21',
    'saloon_moskovskaya': 'Салон на Московской 54',
    'saloon_leningradskaya': 'Салон на Ленинградской 62',
    'saloon_kamishovaya': 'Салон на Камышовой 1',
    'haircut': 'Стрижка',
    'manicure': 'Маникюр',
    'solarium': 'Солярий',
    'coloring': 'Окрашивание',
}


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    keyboard = [
        [
            InlineKeyboardButton(TITLES['callback_service'], callback_data=CALLBACK_SERVICE),
        ],
        [
            InlineKeyboardButton(TITLES['personal_area'], callback_data=PERSONAL_AREA),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Что вы хотите сделать?", reply_markup=reply_markup)
    return FIRST


def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton(TITLES['callback_service'], callback_data=CALLBACK_SERVICE),
            InlineKeyboardButton(TITLES['personal_area'], callback_data=PERSONAL_AREA),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Что вы хотите сделать?", reply_markup=reply_markup)
    return FIRST


def one(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton(TITLES['choice_saloon'], callback_data=CHOICE_SALOON),
        ],
        [
            InlineKeyboardButton(TITLES['choice_master'], callback_data=CHOICE_MASTER),
        ],
        [
            InlineKeyboardButton(TITLES['choice_service'], callback_data=CHOICE_SERVICE),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выберете дальнейшее действие", reply_markup=reply_markup
    )
    return FIRST


def two(update: Update, context: CallbackContext) -> int:
    """Личный кабинет"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("История заказов", callback_data=str(ONE)),
            InlineKeyboardButton("Записаться", callback_data=str(ONE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Что вы хотите сделать?", reply_markup=reply_markup
    )
    return FIRST


def three(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    service = TITLES[query.data]
    print(query)
    print(f'{service}, {saloon}, {master}')
    if service and saloon and master:
        return END
    keyboard = [
        [
            InlineKeyboardButton(TITLES['saloon_pionerskaya'], callback_data=SALOON_PIONERSKAYA),
        ],
        [
            InlineKeyboardButton(TITLES['saloon_moskovskaya'], callback_data=SALOON_MOSKOVSKAYA),
        ],
        [
            InlineKeyboardButton(TITLES['saloon_leningradskaya'], callback_data=SALOON_LENINGRADSKAYA),
        ],
        [
            InlineKeyboardButton(TITLES['saloon_kamishovaya'], callback_data=SALOON_KAMISHOVAYA),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выберете подходящий салон из списка", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return CHOICE_SALOON


def four(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # reply_markup
    # inline_keyboard
    # text
    saloon = TITLES[query.data]
    print(f'{service}, {saloon}, {master}')
    keyboard = [
        [
            InlineKeyboardButton(TITLES['first_master'], callback_data=FIRST_MASTER),
        ],
        [
            InlineKeyboardButton(TITLES['second_master'], callback_data=SECOND_MASTER),
        ],
        [
            InlineKeyboardButton(TITLES['third_master'], callback_data=THIRD_MASTER),
        ],
        [
            InlineKeyboardButton(TITLES['fourth_master'], callback_data=FOURTH_MASTER),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выберете подходящего мастера из списка", reply_markup=reply_markup
    )
    return CHOICE_MASTER


def five(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    master = TITLES[query.data]
    print(f'{service}, {saloon}, {master}')
    keyboard = [
        [
            InlineKeyboardButton(TITLES['haircut'], callback_data=HAIRCUT),
        ],
        [
            InlineKeyboardButton(TITLES['manicure'], callback_data=MANICURE),
        ],
        [
            InlineKeyboardButton(TITLES['solarium'], callback_data=SOLARIUM),
        ],
        [
            InlineKeyboardButton(TITLES['coloring'], callback_data=COLORING),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выберете подходящего услугу из списка", reply_markup=reply_markup
    )
    return CHOICE_SERVICE


def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def publish_photo(update: Update, context: CallbackContext):
    bot = Bot(token=TOKEN_TG)
    image_path = Path() / '..' / 'image' / 'images.jpeg'
    with open(image_path, 'rb') as img_path:
        bot.send_document(chat_id=update.effective_chat.id, document=img_path)


class Command(BaseCommand):
    help = 'Команда настройки Telegram-бота в приложении Django.'

    def handle(self, *args, **kwargs):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=TOKEN_TG,
        )
        print(bot.get_me())
        updater = Updater(TOKEN_TG)
        dispatcher = updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                FIRST: [
                    CallbackQueryHandler(one, pattern='^' + CALLBACK_SERVICE + '$', pass_user_data=True),
                    CallbackQueryHandler(two, pattern='^' + PERSONAL_AREA + '$', pass_user_data=True),
                    CallbackQueryHandler(three, pattern='^' + CHOICE_SALOON + '$', pass_user_data=True),
                    CallbackQueryHandler(four, pattern='^' + CHOICE_MASTER + '$', pass_user_data=True),
                    CallbackQueryHandler(five, pattern='^' + CHOICE_SERVICE + '$', pass_user_data=True),
                ],
                CHOICE_MASTER: [
                    CallbackQueryHandler(five, pass_user_data=True),
                ],
                CHOICE_SALOON: [
                    CallbackQueryHandler(four, pass_user_data=True),
                ],
                CHOICE_SERVICE: [
                    CallbackQueryHandler(three, pass_user_data=True),
                ],
                END: [
                    CallbackQueryHandler(end, ),
                ],
            },
            fallbacks=[CommandHandler('start', start)],
        )
        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()



# bot = Bot(token=TOKEN_TG, )
# updates = bot.get_updates()
#
# # Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)






# def main() -> None:
#     """Run the bot."""
#     # Create the Updater and pass it your bot's token.
#     updater = Updater(TOKEN_TG)
#
#     # Get the dispatcher to register handlers
#     dispatcher = updater.dispatcher
#
#     # ^ means "start of line/string"
#     # $ means "end of line/string"
#     # So ^ABC$ will only allow 'ABC'
#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start)],
#         states={
#             FIRST: [
#                 CallbackQueryHandler(one, pattern='^' + CALLBACK_SERVICE + '$', pass_user_data=True),
#                 CallbackQueryHandler(two, pattern='^' + PERSONAL_AREA + '$', pass_user_data=True),
#                 CallbackQueryHandler(three, pattern='^' + CHOICE_SALOON + '$', pass_user_data=True),
#                 CallbackQueryHandler(four, pattern='^' + CHOICE_MASTER + '$', pass_user_data=True),
#                 CallbackQueryHandler(five, pattern='^' + CHOICE_SERVICE + '$', pass_user_data=True),
#             ],
#             CHOICE_MASTER: [
#                 # CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
#                 CallbackQueryHandler(five, pass_user_data=True),
#             ],
#             CHOICE_SALOON: [
#                 # CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
#                 CallbackQueryHandler(four, pass_user_data=True),
#             ],
#             CHOICE_SERVICE: [
#                 # CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
#                 CallbackQueryHandler(three, pass_user_data=True),
#             ],
#             END: [
#                 # CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
#                 CallbackQueryHandler(end,),
#             ],
#         },
#         fallbacks=[CommandHandler('start', start)],
#     )
#
#     # Add ConversationHandler to dispatcher that will be used for handling updates
#     dispatcher.add_handler(conv_handler)
#
#     # Start the Bot
#     updater.start_polling()
#
#     # Run the bot until you press Ctrl-C or the process receives SIGINT,
#     # SIGTERM or SIGABRT. This should be used most of the time, since
#     # start_polling() is non-blocking and will stop the bot gracefully.
#     updater.idle()
#
#
# if __name__ == '__main__':
#     main()
