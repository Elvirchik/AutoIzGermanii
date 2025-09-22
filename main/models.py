from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название роли")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"


class CustomUser(AbstractUser):
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, verbose_name="Отчество", blank=True)
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    email = models.EmailField(unique=True, verbose_name="Почта")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="Роль")
    address = models.TextField(verbose_name="Адрес проживания")

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        related_query_name="customuser",
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name=_("groups"),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        related_query_name="customuser",
        blank=True,
        help_text=_("Specific permissions for this user."),
        verbose_name=_("user permissions"),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'last_name', 'first_name', 'role']

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class CarMake(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название марки")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Марка авто"
        verbose_name_plural = "Марки авто"


class Car(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, verbose_name="Марка авто")
    model_name = models.CharField(max_length=100, verbose_name="Модель")
    trim = models.CharField(max_length=100, verbose_name="Комплектация")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    mileage = models.PositiveIntegerField(verbose_name="Пробег")
    horsepower = models.PositiveIntegerField(verbose_name="Лошадиные силы")
    color = models.CharField(max_length=50, verbose_name="Цвет")
    transmission = models.CharField(max_length=50, verbose_name="Коробка передач")
    gears = models.PositiveIntegerField(verbose_name="Количество ступеней")
    description = models.TextField(verbose_name="Описание", blank=True)
    drivetrain = models.CharField(max_length=50, verbose_name="Привод")

    def __str__(self):
        return f"{self.make.name} {self.model_name} {self.trim}"

    class Meta:
        verbose_name = "Авто"
        verbose_name_plural = "Автомобили"


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'Обработка'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус заказа")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Итоговая сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оформления заказа")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения заказа")

    def __str__(self):
        return f"Заказ #{self.id} от {self.user}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    car = models.ForeignKey(Car, on_delete=models.PROTECT, verbose_name="Авто")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.car} в заказе #{self.order.id}"

    class Meta:
        verbose_name = "Состав заказа"
        verbose_name_plural = "Состав заказов"
