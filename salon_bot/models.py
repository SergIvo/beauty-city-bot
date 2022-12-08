from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractBaseUser):
    name = models.CharField('Имя клиента', max_length=50)
    phone_number = PhoneNumberField('Номер телефона клиента', region='RU', unique=True)

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

    def __str__(self):
        return self.address


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Покупатель'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга'
    )
    datetime = models.DateTimeField('Дата и время оказания услуги')
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        verbose_name='Салон'
    )
    specialist = models.ForeignKey(
        Specialist,
        on_delete=models.CASCADE,
        verbose_name='Мастер'
    )

