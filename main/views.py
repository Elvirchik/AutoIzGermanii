from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import User, Car, Order
from .forms import UserForm, CarForm, OrderForm, RegisterForm
from .forms import PhoneAuthForm
from django.contrib.auth import authenticate, login, logout
from .models import CartItem
from .models import OrderItem
from django.views.decorators.http import require_POST  # Убедимся, что импорт на месте


def home(request):
    return render(request, 'main/home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'main/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = PhoneAuthForm(request, data=request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, phone=phone, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Неверный номер телефона или пароль')
    else:
        form = PhoneAuthForm()
    return render(request, 'main/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def catalog(request):
    # Теперь Car.objects.all() автоматически исключает удаленные авто
    cars = Car.objects.all()
    return render(request, 'main/catalog.html', {'cars': cars})


def car_detail(request, car_id):
    # Используем Car.objects.all() - он автоматически проверит is_deleted=False
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'main/car_detail.html', {'car': car})


@login_required
def add_to_cart(request, car_id):
    # Убедимся, что добавляемый в корзину автомобиль не удален
    car = get_object_or_404(Car, id=car_id)
    if car.is_deleted:
        messages.error(request, 'Этот автомобиль больше не доступен.')
        return redirect('catalog')

    cart_item, created = CartItem.objects.get_or_create(user=request.user, car=car)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    # При расчете общей цены удаленные авто будут иметь цену, но пользователь их видит, пока не очистит корзину.
    total_price = sum(item.car.price * item.quantity for item in items)
    return render(request, 'main/cart.html', {'items': items, 'total_price': total_price})


@login_required
def place_order(request):
    user = request.user
    if not user.address:
        messages.error(request, 'Пожалуйста, добавьте адрес доставки в профиле.')
        return redirect('profile')
    items = CartItem.objects.filter(user=user)
    if not items.exists():
        messages.error(request, 'Ваша корзина пуста.')
        return redirect('catalog')

    # Можно добавить проверку, что все авто в корзине не удалены, но Django
    # по умолчанию позволит создать заказ, даже если авто удалено после добавления в корзину.

    order = Order.objects.create(user=user, address=user.address)
    for item in items:
        OrderItem.objects.create(order=order, car=item.car, quantity=item.quantity)
    items.delete()
    messages.success(request, 'Заказ успешно создан.')
    return redirect('profile')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        address = request.POST.get('address')
        if address:
            user.address = address
            user.save()
            messages.success(request, 'Адрес обновлен')
        return redirect('profile')
    orders = user.orders.all()
    return render(request, 'main/profile.html', {'user': user, 'orders': orders})


def admin_check(user):
    return user.is_superuser


@user_passes_test(admin_check)
def admin_page(request):
    users = User.objects.all()
    # Используем all_objects, чтобы видеть все авто, включая "удаленные"
    cars = Car.all_objects.all()
    orders = Order.objects.all()
    return render(request, 'main/admin_page.html', {
        'users': users,
        'cars': cars,
        'orders': orders,
    })


@user_passes_test(admin_check)
@require_POST
def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
    return redirect('admin_page')


# Пользователи (код без изменений)
@user_passes_test(lambda u: u.is_superuser)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь обновлен")
            return redirect('admin_page')
    else:
        form = UserForm(instance=user)
    return render(request, 'main/admin_user_form.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Пользователь удален")
        return redirect('admin_page')
    return render(request, 'main/admin_confirm_delete.html', {'object': user, 'type': 'пользователь'})


# Автомобили (код без изменений)
@user_passes_test(lambda u: u.is_superuser)
def car_add(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Автомобиль добавлен")
            return redirect('admin_page')
    else:
        form = CarForm()
    return render(request, 'main/admin_car_form.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def car_edit(request, car_id):
    # Используем all_objects, чтобы можно было редактировать даже "удаленный" автомобиль
    car = get_object_or_404(Car.all_objects, id=car_id)
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "Автомобиль обновлен")
            return redirect('admin_page')
    else:
        form = CarForm(instance=car)
    return render(request, 'main/admin_car_form.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def car_delete(request, car_id):
    # Изменена логика: вместо delete() устанавливаем is_deleted=True
    car = get_object_or_404(Car.all_objects,
                            id=car_id)  # Используем all_objects, чтобы найти авто, даже если оно уже удалено
    if request.method == 'POST':
        if car.is_deleted:
            # Если уже удален, то можно восстановить (по желанию, тут просто удалим)
            car.is_deleted = False
            car.save()
            messages.success(request, f"Автомобиль '{car.configuration}' восстановлен.")
        else:
            car.is_deleted = True
            car.save()
            messages.success(request, f"Автомобиль '{car.configuration}' помечен как удаленный.")
        return redirect('admin_page')

    # Изменяем текст, который видит пользователь в форме подтверждения
    action = "удалить" if not car.is_deleted else "восстановить"
    return render(request, 'main/admin_confirm_delete.html', {'object': car, 'type': 'автомобиль', 'action': action})


# Заказы (код без изменений)
@user_passes_test(lambda u: u.is_superuser)
def order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Заказ обновлен")
            return redirect('admin_page')
    else:
        form = OrderForm(instance=order)
    return render(request, 'main/admin_order_form.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, "Заказ удален")
        return redirect('admin_page')
    return render(request, 'main/admin_confirm_delete.html', {'object': order, 'type': 'заказ'})


@login_required
@require_http_methods(["POST"])
def update_cart_quantity(request, item_id, action):
    """Обновляет количество товара в корзине или полностью удаляет его."""
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if action == 'add':
        item.quantity += 1
        item.save()
        messages.success(request, f'Количество "{item.car.configuration}" увеличено.')

    elif action == 'remove':
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
            messages.info(request, f'Автомобиль "{item.car.configuration}" удален из корзины.')
        else:
            item.save()
            messages.success(request, f'Количество "{item.car.configuration}" уменьшено.')

    elif action == 'delete':
        item.delete()
        messages.info(request, f'Автомобиль "{item.car.configuration}" полностью удален из корзины.')

    return redirect('cart')