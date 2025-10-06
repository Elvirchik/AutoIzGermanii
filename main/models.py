from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class ActiveCarManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('The given phone must be set')
        phone = self.model.normalize_username(phone)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)


class User(AbstractUser):
    middle_name = models.CharField("Отчество", max_length=30, blank=True)
    phone = models.CharField("Номер телефона", max_length=20, unique=True)
    address = models.TextField("Адрес доставки", blank=True)
    username = None

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"


class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('auto', 'Автомат'),
        ('manual', 'Механика'),
        ('robot', 'Робот'),
    ]

    FUEL_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('electric', 'Электро'),
        ('hybrid', 'Гибрид'),
    ]

    DRIVE_CHOICES = [
        ('rear', 'Задний'),
        ('front', 'Передний'),
        ('full', 'Полный'),
    ]

    is_deleted = models.BooleanField(default=False)

    photo = models.ImageField("Фото", upload_to='cars/')
    price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2)
    power = models.PositiveIntegerField("Лошадиные силы")
    mileage = models.PositiveIntegerField("Пробег (км)")
    transmission = models.CharField("Коробка передач", max_length=10, choices=TRANSMISSION_CHOICES)
    color = models.CharField("Цвет", max_length=50)
    drive = models.CharField("Привод", max_length=10, choices=DRIVE_CHOICES)
    fuel_type = models.CharField("Тип топлива", max_length=10, choices=FUEL_CHOICES)
    configuration = models.CharField("Название", max_length=100)
    configuration_desc = models.TextField("Описание", blank=True)

    objects = ActiveCarManager()
    all_objects = models.Manager()

    def __str__(self):
        return f"{self.configuration} - {self.price} руб."


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'car')


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('processed', 'Обработан'),
        ('in_process', 'Авто в процессе'),
        ('in_delivery', 'Авто в доставке'),
        ('delivered', 'Доставлен'),
        ('completed', 'Завершён'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    address = models.TextField("Адрес доставки")

    def __str__(self):
        return f"Заказ {self.id} - {self.user.first_name} {self.user.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)