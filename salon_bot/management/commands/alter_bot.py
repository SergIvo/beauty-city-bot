import os
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Update, Bot
from dotenv import load_dotenv
from ...models import User, Service, Specialist, Salon, Purchase
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.utils.request import Request
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    Filters
)


load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
logger = logging.getLogger(__name__)
FIRST, SECOND = range(2)
CALLBACK_SERVICE = 'callback_service'
PERSONAL_AREA = 'personal_area'
CHOICE_SALOON = 'choice_saloon'
CHOICE_MASTER = 'choice_master'
CHOICE_SERVICE = 'choice_service'
REQUEST_PHONE = 'request_phone'
END = ''

TITLES = {
    'callback_service': 'Записаться на услугу',
    'personal_area': 'Личный кабинет',
    'choice_saloon': 'Выбор салона',
    'choice_master': 'Выбор мастера',
    'choice_service': 'Выбор услуги',
}


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def publish_photo(update: Update, context: CallbackContext):
    bot = Bot(token=TOKEN_TG)
    image_path = Path() / '..' / 'image' / 'images.jpeg'
    with open(image_path, 'rb') as img_path:
        bot.send_document(chat_id=update.effective_chat.id, document=img_path)


class Command(BaseCommand):
    help = 'Команда настройки Telegram-бота в приложении Django.'

    def __init__(self):
        self.saloon = ''
        self.specialist = ''
        self.service = ''
        self.user_phone_number = ''

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
            entry_points=[CommandHandler('start', self.start)],
            states={
                FIRST: [
                    CallbackQueryHandler(self.one, pattern='^' + CALLBACK_SERVICE + '$', pass_user_data=True),
                    CallbackQueryHandler(self.two, pattern='^' + PERSONAL_AREA + '$', pass_user_data=True),
                    CallbackQueryHandler(self.three, pattern='^' + CHOICE_SALOON + '$', pass_user_data=True),
                    CallbackQueryHandler(self.four, pattern='^' + CHOICE_MASTER + '$', pass_user_data=True),
                    CallbackQueryHandler(self.five, pattern='^' + CHOICE_SERVICE + '$', pass_user_data=True),
                ],
                CHOICE_MASTER: [
                    CallbackQueryHandler(self.five, pass_user_data=True),
                ],
                CHOICE_SALOON: [
                    CallbackQueryHandler(self.four, pass_user_data=True),
                ],
                CHOICE_SERVICE: [
                    CallbackQueryHandler(self.three, pass_user_data=True),
                ],
                REQUEST_PHONE: [
                    CallbackQueryHandler(self.request_phone, pass_user_data=True)
                ],
                END: [
                    CallbackQueryHandler(self.end, pass_user_data=True),
                ],
            },
            fallbacks=[CommandHandler('start', self.start)],
        )
        dispatcher.add_handler(conv_handler)

        phonenumber_handler = MessageHandler(Filters.contact, self.handle_phone)
        dispatcher.add_handler(phonenumber_handler)

        updater.start_polling()
        updater.idle()

    def handle_phone(self, update: Update, context: CallbackContext):
        contact = update.effective_message.contact
        self.user_phone_number = contact.phone_number
        print(dir(context))
        print('user_phone_number handled')
        self.end(update, context)

    def get_or_create_user(self, chat_id, update: Update):
        user, _ = User.objects.get_or_create(
            chat_id=chat_id,
            defaults={
                'name': update.effective_message.chat.username,
            }
        )
        return user

    def start(self, update: Update, context: CallbackContext) -> int:
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

    def one(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        chat_id = update.effective_message.chat_id
        print(f'мое имя {update.effective_message.chat.username}')
        user = self.get_or_create_user(chat_id, update)

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

    def two(self, update: Update, context: CallbackContext) -> int:
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

    def three(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        query = update.callback_query
        query.answer()

        salons = [sal.address for sal in Salon.objects.all()]
        masters = [spe.name for spe in Specialist.objects.all()]
        services = [ser.title for ser in Service.objects.all()]

        if query.data in services:
            self.service = query.data
        elif query.data in salons:
            self.saloon = query.data
        elif query.data in masters:
            self.specialist = query.data
        if self.saloon and self.service and self.specialist:
            return END
        print('SALON: вы выбрали следующие пункты:', self.saloon, self.service, self.specialist)

        salons = Salon.objects.all()

        keyboard = []
        for salon in salons:
            keyboard.append(
                [InlineKeyboardButton(f'Салон на {salon}', callback_data=salon.address)]
            )
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text="Выберете подходящий салон из списка", reply_markup=reply_markup
        )

        # Transfer to conversation state `SECOND`
        return CHOICE_SALOON

    def four(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        query = update.callback_query
        query.answer()
        salons = [sal.address for sal in Salon.objects.all()]
        masters = [spe.name for spe in Specialist.objects.all()]
        servicess = [ser.title for ser in Service.objects.all()]

        specialists = Salon.objects.filter(address=query.data).first().specialists.all()
        services = [service.title for service in specialists[0].services.all()]

        if query.data in servicess:
            self.service = query.data
        elif query.data in salons:
            self.saloon = query.data
        elif query.data in masters:
            self.specialist = query.data
        if self.saloon and self.service and self.specialist:
            return END
        print('SPEC: вы выбрали следующие пункты:', self.saloon, self.service, self.specialist)

        keyboard = []
        for specialist in specialists:
            specialist_services = ", ".join([service.title for service in specialist.services.all()])
            keyboard.append(
                [InlineKeyboardButton(f'Мастер {specialist.name}: {specialist_services}', callback_data=specialist.name)]
            )
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text="Выберете подходящего мастера из списка", reply_markup=reply_markup
        )
        return CHOICE_MASTER

    def five(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        salons = [sal.address for sal in Salon.objects.all()]
        masters = [spe.name for spe in Specialist.objects.all()]
        servicess = [ser.title for ser in Service.objects.all()]

        query = update.callback_query
        query.answer()
        print('ghhghghghghghgh', query.data)
        services = Specialist.objects.get(name=query.data).services.all()

        if query.data in servicess:
            self.service = query.data
        elif query.data in salons:
            self.saloon = query.data
        elif query.data in masters:
            self.specialist = query.data
        if self.saloon and self.service and self.specialist:
            return END
        print('SERVICE: вы выбрали следующие пункты:', self.saloon, self.service, self.specialist)

        keyboard = []
        for service in services:
            keyboard.append(
                [InlineKeyboardButton(service.title, callback_data=service.title),]
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
                text="Выберете подходящего услугу из списка",
                reply_markup=reply_markup
            )

        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
        if not user.phone_number:
            return REQUEST_PHONE

        return END

    def request_phone(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        query.answer()
        print(dir(context))
        self.service = query.data
        print('REQUEST_PHONE: вы выбрали следующие пункты:', self.saloon, self.service, self.specialist)
        keyboard = [
            [
                KeyboardButton('Send phone', callback_data=REQUEST_PHONE, request_contact=True),
            ],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        chat_id = query.message['chat']['id']
        query.bot.send_message(
            chat_id,
            text='Подтвердите использование номера телефона из Telegram',
            reply_markup=reply_markup
        )

    def end(self, update: Update, context: CallbackContext) -> int:
        if update.callback_query:
            self.service = update.callback_query.data
        print('END: вы выбрали следующие пункты:', self.saloon, self.service, self.specialist)

        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)

        print('User phonenumber:', self.user_phone_number)

        p = Purchase(
            user=user,
            salon=Salon.objects.get(address=self.saloon),
            specialist=Specialist.objects.get(name=self.specialist),
            service=Service.objects.get(title=self.service),
            datetime=timezone.now()
        )
        p.save()
        print('Purchase object created')
        #query.answer() # brokes here
        keyboard = [
            [
                InlineKeyboardButton("Подтвердить", callback_data="Подтвердить"),
            ],
        ]
        print(dir(context))
        if update.callback_query:
            update.callback_query.edit_message_text(
                reply_markup=InlineKeyboardMarkup(keyboard),
                text=f"""Вы выбрали:
                        салон на улице ➡ {self.saloon}, 
                        мастер ➡ {self.specialist}, 
                        услуга ➡ {self.service} 
                        цена ➡ {p.service.price} рублей""",
            )
        else:
            context.bot.send_message(
                chat_id,
                text=f"""Вы выбрали:
                        салон на улице ➡ {self.saloon}, 
                        мастер ➡ {self.specialist}, 
                        услуга ➡ {self.service} 
                        цена ➡ {p.service.price} рублей""",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        return FIRST