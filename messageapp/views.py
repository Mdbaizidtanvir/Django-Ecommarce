from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest,JsonResponse,HttpResponseForbidden
from app.models import Order
from .models import Message

from django.contrib.admin.views.decorators import staff_member_required


@login_required
def order_messages(request, order_id):
    """
    Customer can view & chat on their own order.
    """
    order = get_object_or_404(Order, id=order_id)

    # Make sure customer can only access their own orders
    if not request.user.is_staff and order.user != request.user:
        return HttpResponseForbidden("You cannot access this order.")

    messages = order.messages.all().order_by('timestamp')
    return render(request, 'message/order_messages.html', {
        'order': order,
        'messages': messages
    })


@login_required
def my_message(request):
    orders = (
        Order.objects
        .filter(user=request.user, payment_staus="paid")
        .prefetch_related('orderitem_set__product', 'messages__sender')
    )

    # Count only unread messages not sent by the current user
    for order in orders:
        order.new_messages_count = order.messages.filter(is_read=False).exclude(sender=request.user).count()

    return render(request, "message.html", {
        "orders": orders,
    })



@login_required
def mark_messages_read(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        return redirect('my_messages')
    return JsonResponse({"success": False}, status=400)




@staff_member_required
def admin_orders_chat_view(request):
    orders = Order.objects.filter(payment_staus="paid")  # latest first
    return render(request, "message/admin_order_chat.html", {
        'orders': orders,
    })


