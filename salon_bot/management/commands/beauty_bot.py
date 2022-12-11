import os
import logging
from datetime import datetime
from datetime import time

import phonenumbers
from . import telegramcalendar, messages
from ...models import User, Service, Specialist, Salon, Purchase
from pathlib import Path
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Update, Bot
from dotenv import load_dotenv
from pathlib import Path
from telegram.error import NetworkError
from django.utils import timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.utils.request import Request
from .inline_button import *

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

APP_NAME = 'salon_bot'
FIRST, SECOND = range(2)
CALLBACK_SERVICE = 'callback_service'
PERSONAL_AREA = 'personal_area'
CHOICE_SALOON = 'choice_saloon'
CHOICE_MASTER = 'choice_master'
CHOICE_SERVICE = 'choice_service'
REQUEST_PHONE = 'request_phone'
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
END = 'end'
CALENDAR = 'calend'

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
        self.services = ''
        self.username = ''
        self.user_phone_number = ''
        self.bot = Bot(token=TOKEN_TG)
        self.date = ''
        self.time = ''
        self.confirm_pdf = False

    def handle(self, *args, **kwargs, ):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=TOKEN_TG,
        )
        print(bot.get_me())
        updater = Updater(TOKEN_TG, use_context=True)
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
                    CallbackQueryHandler(self.history, pattern='^' + 'history' + '$', pass_user_data=True),
                    CallbackQueryHandler(self.end, pattern='^' + 'replay' + '$', pass_user_data=True),
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
                # END: [
                #     CallbackQueryHandler(self.calendar_handler, pass_user_data=True),
                #     CallbackQueryHandler(self.calendar_handler, pattern='^' + 'confirm' + '$', pass_user_data=True),
                #     # CallbackQueryHandler(self.start, pattern='^' + 'main_menu' + '$', pass_user_data=True),
                # ],
                CALENDAR: [
                    # CallbackQueryHandler(self.end, pass_user_data=True),
                    CallbackQueryHandler(self.start, pattern='^' + 'confirm' + '$'),
                    CallbackQueryHandler(self.start, pattern='^' + 'main_menu' + '$'),
                ],
            },
            fallbacks=[CommandHandler('start', self.start)],
        )
        dispatcher.add_handler(conv_handler)
        phonenumber_handler = MessageHandler(Filters.contact, self.handle_phone)
        dispatcher.add_handler(phonenumber_handler)
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.finish))
        dispatcher.add_handler(CommandHandler('replay', self.replay_service))
        updater.start_polling()
        updater.idle()

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
        try:
            user = update.message.from_user
            logger.info("User %s started the conversation.", user.first_name)
        except AttributeError:
            user = update.effective_message.chat.username
            logger.info("User %s started the conversation.", user)

        keyboard = [
            [
                InlineKeyboardButton(TITLES['callback_service'], callback_data=CALLBACK_SERVICE),
            ],
            [
                InlineKeyboardButton(TITLES['personal_area'], callback_data=PERSONAL_AREA),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            update.message.reply_text("Что вы хотите сделать?", reply_markup=reply_markup)
        except AttributeError:
            self.service, self.saloon, self.specialist = '', '', ''
            self.bot.send_message(chat_id=update.effective_message.chat_id, text="Что вы хотите сделать?", reply_markup=reply_markup)
        return FIRST

    def one(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        chat_id = update.effective_message.chat_id
        print(f'мое имя {update.effective_message.chat.username}')
        self.username = update.effective_message.chat.username
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
                InlineKeyboardButton("История заказов", callback_data='history'),
                InlineKeyboardButton("Записаться", callback_data='history'),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Что вы хотите сделать?", reply_markup=reply_markup
        )
        return FIRST

    def history(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
        purcheses = Purchase.objects.all().order_by('-datetime')
        ps = [f'{count + 1}). {(p.service.title).capitalize()} у мастера {p.specialist} \n   адрес -> {p.salon} - \n \n \ ' \
              f'Что бы повторить заказ, нажми сюда 👉/replay \n \n ' for count, p in enumerate(purcheses)]
        messages = ' '.join(ps[:10])
        self.bot.send_message(
            chat_id=chat_id,
            text=messages,
        )
        return FIRST

    def replay_service(self, update: Update, context: CallbackContext):
        purcheses = Purchase.objects.all().order_by('-datetime')
        chat_id = update.message.chat.id
        self.service = purcheses[0].service.title
        self.saloon = purcheses[0].salon.address
        self.specialist = purcheses[0].specialist.name
        self.calendar_handler(update, context)


    def three(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        query = update.callback_query
        query.answer()

        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
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
            self.end(update, context)
        else:
            salons = Salon.objects.all()
            [salon for salon in salons]

            keyboard = [
                [
                    InlineKeyboardButton(f'Салон на {salons[0]}', callback_data=salons[0].address),
                ],
                [
                    InlineKeyboardButton(f'Салон на {salons[1]}', callback_data=salons[1].address),
                ],
                [
                    InlineKeyboardButton(f'Салон на {salons[2]}', callback_data=salons[2].address),
                ],
                [
                    InlineKeyboardButton(f'Салон на {salons[3]}', callback_data=salons[3].address),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            query.edit_message_text(
                text="Выберете подходящий салон из списка", reply_markup=reply_markup
            )
            return CHOICE_SALOON

    def four(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""
        query = update.callback_query
        query.answer()
        salons = [sal.address for sal in Salon.objects.all()]
        masters = [spe.name for spe in Specialist.objects.all()]
        servicess = [ser.title for ser in Service.objects.all()]
        chat_id = update.effective_message.chat_id
        specialists = Specialist.objects.all()
        # user = self.get_or_create_user(chat_id, update)

        if query.data in servicess:
            self.service = query.data
        elif query.data in salons and self.service:
            self.saloon = query.data
            service = Service.objects.filter(title=self.service).first()
            salon = Salon.objects.filter(address=query.data).first()
            specialists = Specialist.objects.filter(services=service).filter(salons=salon)
        elif query.data in salons:
            self.saloon = query.data
            specialists = Salon.objects.filter(address=query.data).first().specialists.all()
        elif query.data in masters:
            self.specialist = query.data

        if self.saloon and self.service and self.specialist:
            self.end(update, context)
        else:
            if len(specialists) == 1:
                reply_markup = keyboard_one_specialist_button(specialists)
            elif len(specialists) == 2:
                reply_markup = keyboard_two_specialist_button(specialists)
            else:
                reply_markup = keyboard_four_specialist_button(specialists)
            query.edit_message_text(
                text="Выберете подходящего мастера из списка", reply_markup=reply_markup
            )
            return CHOICE_MASTER

    def five(self, update: Update, context: CallbackContext) -> int:
        """Show new choice of buttons"""

        chat_id = update.effective_message.chat_id
        salons = [sal.address for sal in Salon.objects.all()]
        masters = [spe.name for spe in Specialist.objects.all()]
        servicess = [ser.title for ser in Service.objects.all()]
        query = update.callback_query
        query.answer()
        user = self.get_or_create_user(chat_id, update)

        if query.data in servicess:
            self.service = query.data
        elif query.data in salons:
            self.saloon = query.data
        elif query.data in masters:
            self.specialist = query.data
            self.services = Specialist.objects.get(name=query.data).services.all()
        elif query.data == CHOICE_SERVICE:
            self.services = Service.objects.all()
        if self.saloon and self.service and self.specialist:

            self.end(update, context)
        else:
            if len(self.services) == 1:
                query.edit_message_text(
                    text="Выберете подходящего услугу из списка",
                    reply_markup=keyboard_one_button(self.services)
                )
            if len(self.services) == 2:
                query.edit_message_text(
                    text="Выберете подходящего услугу из списка",
                    reply_markup=keyboard_two_button(self.services),
                )
            if len(self.services) == 4:
                query.edit_message_text(
                    text="Выберете подходящего услугу из списка",
                    reply_markup=keyboard_four_button(self.services),
                )
            if len(self.services) == 5:
                query.edit_message_text(
                    text="Выберете подходящего услугу из списка",
                    reply_markup=keyboard_five_button(self.services),
                )

            return CHOICE_SERVICE

    def end(self, update: Update, context: CallbackContext) -> str:
        chat_id = update.effective_message.chat_id
        query = update.callback_query
        user = self.get_or_create_user(chat_id, update)
        keyboard = [
            [
                InlineKeyboardButton("выбрать дату и время", callback_data="date"),
            ],
            [
                InlineKeyboardButton("Вернуться к выбору услуги", callback_data="main_menu"),
            ],
        ]
        print('user.Consent_Of_Personal_Data', user.Consent_Of_Personal_Data)
        self.confirm_pdf = user.Consent_Of_Personal_Data
        self.user_phone_number = user.phone_number
        print('user.phone_number',  user.phone_number)
        if query.data == 'date':
            self.calendar_handler(update, context)
        elif query.data == 'main_menu' or query.data == 'not_confirm_pdf':
            self.start(update, context)
        elif 'CALENDAR' in query.data:
            self.choice_time(update, context)
        elif 'time' in query.data and self.confirm_pdf == False:
            self.time = query.data
            self.consent_confirm_pdf(update, context, chat_id)
        elif 'confirm_pdf' in query.data and not self.user_phone_number:
            self.request_phone(update, context)
        elif self.user_phone_number and self.confirm_pdf and 'time' in query.data:
            self.time = query.data
            self.get_user_name(update, context)
        else:
            app_dirpath = apps.get_app_config(APP_NAME).path
            image_path = (
                    Path(app_dirpath) /
                    'management' /
                    'commands' /
                    '111.jpg'
            )
            with open(image_path, 'rb') as img_path:
                self.bot.send_photo(chat_id=chat_id, photo=img_path)
            self.bot.send_message(
                chat_id=chat_id,
                reply_markup=InlineKeyboardMarkup(keyboard),
                text=f"""Вы выбрали:
                    ➡ салон  {self.saloon},
                    ➡ мастер  {self.specialist},
                    ➡ услуга  {self.service}""",
            )

    def calendar_handler(self, update, context):
        print('you are in calendar_handler')

        try:
            query = update.callback_query
            query.answer()
            if 'date' in query.data:
                query.edit_message_text(
                    text=messages.calendar_message,
                    reply_markup=telegramcalendar.create_calendar())
        except AttributeError:
            self.bot.send_message(
                chat_id=update.effective_message.chat_id,
                text=messages.calendar_message,
                reply_markup=telegramcalendar.create_calendar())
            print(self.bot.answer_callback_query)
            self.choice_time(update, context)

    def choice_time(self, update, context):
        try:
            query = update.callback_query
            query.answer()
            self.date = query.data
            print('you are in choice_time, query.data=', query.data)
            if 'DAY' in query.data:
                query.edit_message_text(
                    text="Выберете подходящее время из свободных на эту дату",
                    reply_markup=keyboard_time_button(self.services),
                )
        except AttributeError:
            print('ggggggggg', update)
            if 'DAY' in query.data:
                query.edit_message_text(
                    text="Выберете подходящее время из свободных на эту дату",
                    reply_markup=keyboard_time_button(self.services),
                )


    def consent_confirm_pdf(self, update, context, chat_id):
        query = update.callback_query
        query.answer()
        print("You in confirm_pdf stage, query.data = ", query.data)
        if self.confirm_pdf == False:
            consent_pdf_filename = 'Consent_Of_Personal_Data_Processing.pdf'
            app_dirpath = apps.get_app_config(APP_NAME).path
            static_subfolder = settings.STATIC_URL.strip('/')
            pdf_subfolder = 'pdf'
            print("--------------", app_dirpath, static_subfolder)
            consent_pdf_filepath = (
                    Path(app_dirpath) /
                    'management' /
                    'commands' /
                    consent_pdf_filename
            )
            query.edit_message_text(
                text="Для первичной записи и дальнейшей обработки данных нужно подтвердить разрешиние на обработку данных",
                reply_markup=keyboard_two_confirm_pdf_button(),
            )
            self.send_file_to_chat(update, context, consent_pdf_filepath)

    @staticmethod
    def send_file_to_chat(update: Update, context: CallbackContext,
                          filepath: Path,
                          reply_markup: InlineKeyboardMarkup = None):
        delay = 1
        while True:
            try:
                with open(filepath, 'rb') as file:
                    context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=file,
                        reply_markup=reply_markup
                    )
                return
            except FileNotFoundError as ex:
                logger.warning(ex)
                logger.warning(f'Нет файла {filepath}')
                return
            except NetworkError as ex:
                logger.warning(ex)
                time.sleep(delay)
                delay = 10
            except Exception as ex:
                logger.warning(ex)
                return

    def handle_consent_personal_data(self, update: Update,
                                     context: CallbackContext):
        query = update.callback_query
        variant = query.data
        if variant != 'agree':
            return
        self.send_username_input_invitation(update, context)

    def request_phone(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        query.answer()
        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
        user.Consent_Of_Personal_Data = True
        user.save()
        print('you are in request_phone, query.data ==', query.data)
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

    def handle_phone(self, update: Update, context: CallbackContext):
        contact = update.effective_message.contact
        chat_id = update.effective_message.chat_id
        self.user_phone_number = contact.phone_number
        user = self.get_or_create_user(chat_id, update)
        user.phone_number = self.user_phone_number
        user.save()
        print('user_phone_number handled')
        self.get_user_name(update, context)


    def get_user_name(self,  update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
        query.edit_message_text(
            text="Как к вам обращаться?",
        )

    def finish(self, update: Update, context: CallbackContext):
        # query = update.callback_query
        # query.answer()
        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
        # print("вы попали в стадию END", f"query.data --> {query.data} --> {self.service}")

        p = Purchase(
            user=User.objects.get(name=self.username),
            salon=Salon.objects.get(address=self.saloon),
            specialist=Specialist.objects.get(name=self.specialist),
            service=Service.objects.get(title=self.service),
            datetime=datetime.now()
        )
        p.save()
        print('you are in finish stague')
        chat_id = update.effective_message.chat_id
        user = self.get_or_create_user(chat_id, update)
        user.nickname = update.message.text
        user.save()
        chat_id = update.effective_message.chat_id
        date_spisok = self.date.split(sep=";")
        date = f'{date_spisok[4]}.{date_spisok[3]}.{date_spisok[2]}'
        time = f'{self.time.split()[1]}:00'
        price = Service.objects.filter(title=self.service).first()
        keyboard = [
            [
                InlineKeyboardButton("Вернуться к выбору услуги", callback_data="main_menu"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.bot.send_message(
            chat_id,
            reply_markup=reply_markup,
            text=f'''Вы успешно записались:
            
            {date} на {time}, 
            к мастеру {self.specialist}, 
            на услугу {self.service}, 
            стоймость = {price.price} рублей.
            
            Ваши контактные данные:
                Имя -> {user.nickname},
                Тел. -> {user.phone_number}''',

        )





