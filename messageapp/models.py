from django.db import models
from app.models import *

# Create your models here.
class Message(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_admin = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)  # ✅ new field
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} on Order {self.order.id}"
