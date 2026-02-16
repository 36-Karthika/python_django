from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Category, SubCategory, Product, Cart, Order, OrderItem, Review
from .forms import ReviewForm

def home(request):
    return render(request, 'shop/home.html', {'categories': Category.objects.all()})

def category_view(request, id):
    cat = Category.objects.get(id=id)
    subs = SubCategory.objects.filter(category=cat)
    return render(request, 'shop/category.html', {'category': cat, 'subs': subs})

def subcategory_view(request, id):
    sub = SubCategory.objects.get(id=id)
    prods = Product.objects.filter(subcategory=sub)
    return render(request, 'shop/products.html', {'subcategory': sub, 'products': prods})

def product_detail(request, id):
    product = Product.objects.get(id=id)
    reviews = product.reviews.all().order_by('-created_at')
    avg = product.average_rating()
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and request.user.is_authenticated:
        if form.is_valid():
            Review.objects.update_or_create(
                product=product, user=request.user,
                defaults=form.cleaned_data
            )
            return redirect('product_detail', id=id)
    return render(request, 'shop/product_detail.html', {'product': product,'reviews': reviews,'avg': avg,'form': form})

@csrf_exempt
@login_required
def rate_product(request, id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        rating = int(request.POST.get('rating',0))
        if 1 <= rating <= 5:
            Review.objects.update_or_create(product=product,user=request.user,defaults={'rating':rating})
            return JsonResponse({'success':True,'avg':product.average_rating(),'count':product.reviews.count()})
    return JsonResponse({'success':False})

@login_required
def add_to_cart(request, id):
    p = get_object_or_404(Product, id=id)
    item, created = Cart.objects.get_or_create(user=request.user, product=p)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart')

@login_required
def cart(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(i.product.price * i.quantity for i in items)
    return render(request, 'shop/cart.html', {'items': items, 'total': total})

@login_required
def checkout(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(i.product.price * i.quantity for i in items)
    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(user=request.user, total_price=total, address=request.POST['address'])
            for i in items:
                OrderItem.objects.create(order=order, product=i.product, quantity=i.quantity, price=i.product.price)
                i.product.stock -= i.quantity
                i.product.save()
            items.delete()
        return redirect('order_success', order_id=order.id)
    return render(request, 'shop/checkout.html', {'items': items, 'total': total})

@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})

def register_user(request):
    if request.method == 'POST':
        User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
        return redirect('login')
    return render(request, 'shop/register.html')

def login_user(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user: login(request, user); return redirect('home')
    return render(request, 'shop/login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def search_products(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q) if q else []
    return render(request, 'shop/search.html', {'query': q, 'products': products})
