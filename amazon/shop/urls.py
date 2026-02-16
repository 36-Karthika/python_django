from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:id>/', views.category_view, name='category_view'),
    path('subcategory/<int:id>/', views.subcategory_view, name='subcategory_view'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('rate_product/<int:id>/', views.rate_product, name='rate_product'),
    path('search/', views.search_products, name='search'),
]
