from django.shortcuts import render, get_object_or_404,redirect
from .cart import Cart
from django.views.decorators.http import require_POST
from .forms import *  # <-- import your form
from django.contrib.auth import login
from app.models import *
# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.core.paginator import Paginator


def search_suggestions(request):
    q = request.GET.get("q", "")
    if q:
        products = Product.objects.filter(name__icontains=q)[:5]  # top 5 suggestions
        results = [
            {
                "name": p.name,
                "image": p.main_image.url if p.main_image else "",  # ✅ use .url
            }
            for p in products
        ]
    else:
        results = []
    return JsonResponse(results, safe=False)





def store(request, slug=None):
    # If slug is provided, filter by category
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = Product.objects.filter(category=category)
    else:
        category = None  # No current category
        products = Product.objects.all()

    # ❤️ Favorite IDs
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    # 🔍 Search filter
    search_query = request.GET.get("search", "")
    if search_query:
        products = products.filter(name__icontains=search_query)

    # 🎨 Color filter
    selected_color = request.GET.get("color", "")
    if selected_color:
        products = products.filter(colors__name__iexact=selected_color)

    # 📏 Size filter
    selected_size = request.GET.get("size", "")
    if selected_size:
        products = products.filter(sizes__name__iexact=selected_size)

    # 🟡 Category filter by GET (for “All” option in sidebar)
    selected_category = request.GET.get("category", "")
    if selected_category:
        products = products.filter(category__name__iexact=selected_category)

    # 💰 Price filter
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # 📦 Get all filters for sidebar
    categories = Category.objects.all()
    sizes = Size.objects.all()
    colors = Color.objects.all()

    # 🔢 Pagination
    paginator = Paginator(products.distinct(), 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
        'current_category': category,  # None if “all” products
        'selected': {
            'search': search_query,
            'color': selected_color,
            'size': selected_size,
            'category': selected_category,
            'price_min': price_min or "",
            'price_max': price_max or ""
        },
        'favorite_ids': favorite_ids
    }

    return render(request, "store/store.html", context)



from ui_app.models import *

@csrf_exempt
def Home(request):
    products= Product.objects.all()
    banner = Banner.objects.last()  # latest created


    campaigns = Campaign.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )
    categories=Category.objects.all()

    deals_of_the_days = Deals_of_the_Day.objects.filter(end_date__gte=timezone.now()).prefetch_related('products')

    context = {
        "products":products,
                'favorite_ids': favorite_ids,
"categories":categories,
        "deals_of_the_days": deals_of_the_days,
                "banner": banner,
"campaigns": campaigns

    }
    return render(request,'store/Home.html',context)

from django.db.models import Avg


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(slug=slug)[:4]  # Show 4 related products

    reviews = product.reviews.all()  # from related_name="reviews"
    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]

    return render(request, 'store/product_detail.html', {'product': product, 'related_products': related_products,            "reviews": reviews,
        "avg_rating": round(avg_rating, 1) if avg_rating else None,
            'favorite_ids': favorite_ids,
})


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("size")
    color = request.POST.get("color")

    cart = Cart(request)
    cart.add(product, quantity=quantity, size=size, color=color)
    return redirect("view_cart")

def view_cart(request):
    cart = Cart(request)
    cart_items = list(cart.get_items())
    subtotal = cart.get_total_price()
    tax = 150  # 10% example
    total = round(subtotal + tax, 2)
    total_savings = sum((float(item["original_price"]) - float(item["price"])) * item["quantity"] for _, item in cart_items)

    return render(request, "store/cart.html", {
        "cart_items": cart_items,   # [(product_id, item_dict), ...]
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "total_savings":total_savings,
    })

def remove_from_cart(request, pk):
    cart = Cart(request)
    cart.remove(pk)
    return redirect("view_cart")

@require_POST
def update_cart(request, pk):
    cart = Cart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.update(pk, quantity)
    return redirect("view_cart")


from .models import DiscountCode

def apply_discount_code(request):
    code = request.POST.get("discount_code", "").strip()
    cart = Cart(request)

    try:
        discount = DiscountCode.objects.get(code__iexact=code, active=True)
        cart.apply_discount(discount.percentage)
        messages.success(request, f"Discount code applied! You saved {discount.percentage}%")
    except DiscountCode.DoesNotExist:
        messages.error(request, "Invalid or inactive discount code.")

    return redirect("view_cart")



def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after register
            return redirect('home')  # or redirect to 'view_cart', etc.
    else:
        form = CustomRegisterForm()
    return render(request, 'auth/register.html', {'form': form})


@require_POST
@login_required
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Order cancelled and payment refunded.")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    return redirect('orders')



@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'cancelled':
        order.delete()
        messages.success(request, "Order deleted successfully.")
    else:
        messages.error(request, "Only cancelled orders can be deleted.")

    return redirect('orders')




@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user,payment_staus="paid").prefetch_related('orderitem_set__product')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status == 'pending':
            form = OrderAddressForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                return redirect('orders')
    else:
        for order in orders:
            if order.status == 'pending':
                order.address_form = OrderAddressForm(instance=order)


    return render(request, 'store/my_orders.html', {'orders': orders})




@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return redirect('favorites')

@login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return redirect('favorites')

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/favorites.html', {'favorites': favorites})


def about(request):
    return render(request, 'store/about.html')



from django.contrib import messages

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            NewsletterEmail.objects.get_or_create(email=email)
            messages.success(request, "Thanks for subscribing!")
    return redirect('home')



@login_required
def return_requests_list(request):
    requests = ReturnRequest.objects.filter(user=request.user)
    return render(request, 'returns/return_requests_list.html', {'requests': requests})

from django.utils.timezone import now


@login_required
def create_return_request(request):
    # ✅ Filter only delivered OrderItems
    delivered_items = OrderItem.objects.filter(
        order__user=request.user,
        order__status='delivered'
    )

    if request.method == 'POST':
        order_item_id = request.POST.get('order_item')
        reason = request.POST.get('reason')
        pickup_date = now().date()

        order_item = OrderItem.objects.get(id=order_item_id, order__user=request.user)

        ReturnRequest.objects.create(
            user=request.user,
            order_item=order_item,
            reason=reason,
            pickup_date=pickup_date
        )
        messages.success(request, 'Your return request has been submitted.')
        return redirect('return_requests')

    return render(request, 'returns/create_return_request.html', {
        'delivered_items': delivered_items
    })


