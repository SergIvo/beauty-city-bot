from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractBaseUser):
    chat_id = models.CharField('Id чата', max_length=50, default=None, unique=True)
    name = models.CharField('Имя клиента', max_length=50)
    nickname = models.CharField('Обращение к клиенту', max_length=50, default='')
    phone_number = PhoneNumberField('Номер телефона клиента', region='RU')
    Consent_Of_Personal_Data = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return f'{self.name} {self.phone_number}'


class Service(models.Model):
    title = models.CharField('Название услуги', max_length=30)
    price = models.IntegerField('Стоимость услуги')

    def __str__(self):
        return self.title


class Specialist(models.Model):
    name = models.CharField('Имя мастера', max_length=50)
    services = models.ManyToManyField(
        Service,
        related_name='specialists',
        verbose_name='Оказываемые услуги'
    )

    def __str__(self):
        return self.name


class Salon(models.Model):
    address = models.TextField('Адрес салона', max_length=200)
    latitude = models.FloatField('Широта')
    longitude = models.FloatField('Долгота')
    specialists = models.ManyToManyField(
        Specialist,
        related_name='salons',
        verbose_name='Мастера')
    services = models.ManyToManyField(Service, related_name='salons',
                                      verbose_name='Услуги')

    def __str__(self):
        return self.address


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Покупатель',
        null=True,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга',
        null=True,
        blank=True
    )
    datetime = models.DateTimeField('Дата и время оказания услуги', null=True,)
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        verbose_name='Салон',
        null=True,
        blank=True
    )
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        verbose_name='Мастер',
        null=True,
        blank=True
    )

