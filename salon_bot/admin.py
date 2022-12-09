from django.contrib import admin

from .models import User, Service, Specialist, Salon, Purchase


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price')


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('address', 'latitude', 'longitude',)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('datetime',)
