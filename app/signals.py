from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order


@receiver(post_save, sender=Order)
def order_status_change_or_create(sender, instance, created, **kwargs):
    if created:
        # 🔔 Case 1: New Order Created
        subject = f"New Order Created - #{instance.id}"
        message = f"A new order has been created.\n\nOrder ID: {instance.id}\nCustomer: {instance.user.username}\nTotal: {instance.total_price}\nStatus: {instance.status}"
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ["tanvirislambaizid@gmail.com"],  # 📩 admin email
            fail_silently=False,
        )
        print(f"✅ Email sent to admin (tanvirislambaizid@gmail.com) for new order #{instance.id}")

    else:
        # 🔔 Case 2: Order Status Updated
        subject = f"Order #{instance.id} Status Updated"
        message = f"Hello {instance.user.username},\n\nYour order (ID: {instance.id}) status has been updated to: {instance.status}."
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],  # 📩 customer email
            fail_silently=False,
        )
        print(f"✅ Email sent to customer ({instance.user.email}) for order #{instance.id} status change to {instance.status}")
