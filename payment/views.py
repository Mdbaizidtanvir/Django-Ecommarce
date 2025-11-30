from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404,redirect
from app.cart import Cart
from django.views.decorators.http import require_POST
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
from django.contrib.auth.decorators import login_required
import stripe
from .sslcommerz import sslcommerz_payment_gateway
from django.conf import settings

# Create your views here.


from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout_info(request):
    if request.method == 'POST':
        # Save all form fields to session
        request.session['checkout_info'] = {
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'zip_code': request.POST.get('zip_code'),
        }
        return redirect('stripe_checkout')

    cart = Cart(request)
    cart_items = list(cart.get_items())
    subtotal = cart.get_total_price()

    shiping_cost = 150

    total = round(subtotal + shiping_cost, 2)
    data = {
                "cart_items": cart_items,   # [(product_id, item_dict), ...]
        "subtotal": subtotal,
        "shiping_cost": shiping_cost,
        "total": total,
    }
    return render(request, 'store/checkout_info.html',context=data)




from django.contrib import messages



import uuid
@login_required
def create_checkout_session(request):
    cart = Cart(request)
    items = dict(cart.get_items())
    checkout_info = request.session.get("checkout_info", {})

    # Create order
    order = Order.objects.create(
        user=request.user,
        email=checkout_info.get("email", ""),
        phone=checkout_info.get("phone", ""),
        address=checkout_info.get("address", ""),
        zip_code=checkout_info.get("zip_code", ""),
    )

    # Save order items
    line_items = []
    for product_id, item in items.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item["quantity"],
            price=item["offer"],
        )

        # Stripe requires line_items
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {"name": product.name},
                "unit_amount": int(item["offer"] * 100),
            },
            "quantity": item["quantity"],
        })

    # Generate token
    token = uuid.uuid4().hex
    order.success_token = token
    order.save()

    # Create Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url=request.build_absolute_uri(f'/checkout/success/{order.id}/'),
        cancel_url=request.build_absolute_uri("/checkout/cancel/"),
    )

    return redirect(session.url)


from django.http import HttpResponseForbidden

@csrf_exempt
@login_required
def checkout_success(request, order_id):
    token = request.GET.get("token")
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponseForbidden("Invalid order or token")

    order.payment_staus = 'paid'
    order.status = 'pending'
    order.save()
    Cart(request).clear()

    return render(request, 'store/checkout_success.html', {"order": order})


@csrf_exempt
@login_required
def falid_success(request):
    return render(request, 'store/checkout_cancel.html')



@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect("product_detail", slug=product.slug)  # back to product detail

    return render(request, "review_create.html", {"product": product})

