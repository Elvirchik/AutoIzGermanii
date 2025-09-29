from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('catalog/', views.catalog, name='catalog'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('add_to_cart/<int:car_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('place_order/', views.place_order, name='place_order'),
    path('profile/', views.profile, name='profile'),

    path('admin_page/', views.admin_page, name='admin_page'),
    path('change_order_status/<int:order_id>/', views.change_order_status, name='change_order_status'),

    # Кастомные CRUD для админки с префиксом manage
    path('manage/user/edit/<int:user_id>/', views.user_edit, name='admin_user_edit'),
    path('manage/user/delete/<int:user_id>/', views.user_delete, name='admin_user_delete'),

    path('manage/car/add/', views.car_add, name='admin_car_add'),
    path('manage/car/edit/<int:car_id>/', views.car_edit, name='admin_car_edit'),
    path('manage/car/delete/<int:car_id>/', views.car_delete, name='admin_car_delete'),

    path('manage/order/edit/<int:order_id>/', views.order_edit, name='admin_order_edit'),
    path('manage/order/delete/<int:order_id>/', views.order_delete, name='admin_order_delete'),
]
