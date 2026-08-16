import re
import random
from django.db import models

class Category(models.Model):
    STATUS = (
        ('True', 'Да'),
        ('False', 'Нет'),
    )
    title = models.CharField(max_length=1000, verbose_name='Заголовок')
    image = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS, default='True', verbose_name='Статусы')
    create_at = models.DateField(auto_now=True, verbose_name='Создать в')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категория'


class Product(models.Model):
    STATUS = (
        ('True', 'Да'),
        ('False', 'Нет'),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    image = models.URLField()
    title = models.CharField(max_length=1000, verbose_name='Заголовок')
    price = models.IntegerField(default=0, verbose_name='Цена')
    description = models.TextField(blank=True, null=True, verbose_name='описание')
    status = models.CharField(max_length=15, choices=STATUS, default='True', verbose_name='Статусы')
    create_at = models.DateField(auto_now=True, verbose_name='Создать в')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукт'

class Feedback(models.Model):
    user_id = models.CharField(max_length=1000, verbose_name='Пользователь ID')
    username = models.CharField(max_length=1000, verbose_name='Имя пользователя')
    comment = models.TextField(verbose_name='комментарий')
    create_at = models.DateField(auto_now=True, verbose_name='Создать в')
    def __str__(self):
        return self.comment
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарий'


class Driver(models.Model):
    fullname = models.CharField(max_length=1000, verbose_name='Ф.И.О')
    phone = models.CharField(max_length=1000, verbose_name='телефон')
    car_number = models.CharField(max_length=1000, verbose_name='Номер автомобиля')

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водитель'


class ShopCart(models.Model):
    STATUS = (
        ('New', 'Новый'),
        ('Not-accepted', 'Не-принято'),
    )
    user_id = models.CharField(max_length=1000, verbose_name='пользователь ID')
    username = models.CharField(max_length=1000, blank=True, null=True, verbose_name='пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукты')
    quantity = models.IntegerField(default=1, verbose_name='количество')
    total_price = models.CharField(max_length=1000, verbose_name='общая цена')
    status = models.CharField(max_length=50, choices=STATUS, default='New', verbose_name='Статусы')
    create_at = models.DateField(auto_now=True, verbose_name='Создать в')
    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

class Order(models.Model):
    STATUS = (
        ('New', 'Новый'),
        ('Accepted', 'Принял'),
        ('Rejected', 'Отклоненный'),
        ('Expired', 'Истекший'),
    )
    product = models.ManyToManyField(Product, verbose_name='Продукты')
    driver = models.ForeignKey(Driver, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Водитель')
    location = models.CharField(max_length=1000, verbose_name='геолокация')
    full_address = models.TextField(blank=True, null=True, verbose_name='полный адрес')
    user_id = models.CharField(max_length=1000, verbose_name='пользователь ID')
    phone = models.CharField(max_length=1000, verbose_name='телефон')
    code = models.CharField(max_length=8, blank=True, null=True, unique=True, verbose_name='код')
    language = models.CharField(max_length=8, blank=True, null=True, verbose_name='язык')
    product_data = models.JSONField(default=dict, blank=True, verbose_name="Данные о продукте")
    status = models.CharField(max_length=50, choices=STATUS, default='New', verbose_name='Статусы')
    link = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Линк')
    time = models.TimeField(auto_now_add=True, verbose_name='Время')
    create_at = models.DateField(auto_now_add=True, verbose_name='Создать в')
    def __str__(self):
        return self.location

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        if self.location:
            parts = re.split(r'[,\s-]+', self.location.strip())
            if len(parts) >= 2:
                lat = float(parts[0])
                lon = float(parts[1])
                self.link = f"https://yandex.ru/maps/?ll={lon},{lat}&z=15&pt={lon},{lat},pmrdl"
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            if not Order.objects.filter(code=code).exists():
                return code
    class Meta:
        verbose_name = 'Заказы'
        verbose_name_plural = 'Заказы'



