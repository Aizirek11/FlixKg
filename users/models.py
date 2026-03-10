from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Возраст')
    is_pensioner_pending = models.BooleanField(default=False, verbose_name='Ожидает подтверждения')
    is_pensioner = models.BooleanField(default=False, verbose_name='Подтверждённый пенсионер')
    pensioner_promo_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Промокод пенсионера')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username