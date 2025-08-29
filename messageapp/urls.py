from django.urls import path
from messageapp import views
urlpatterns = [
  
    path("messages/", views.my_message, name="my_messages"),

    # Customer: view chat for a specific order
    path("messages/order/<int:order_id>/", views.order_messages, name="order_messages"),

    # Customer: mark messages as read
    path("messages/order/<int:order_id>/mark-read/", views.mark_messages_read, name="mark_messages_read"),

    # Admin: all orders chat view
    path("admin-chat/", views.admin_orders_chat_view, name="admin_orders_chat"),

 
]

