# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class OrderChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']

        user = self.scope['user']
        is_admin = user.is_staff  # ✅ Check if sender is admin

        # Save message to DB
        message = await self.create_message(user, message_text, is_admin)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.text,
                'sender': user.username,
                'is_admin': message.is_admin,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def create_message(self, user, text, is_admin):
        from app.models import Order   # ✅ Lazy import
        from .models import Message    # ✅ Lazy import
        order = Order.objects.get(id=self.order_id)
        return Message.objects.create(order=order, sender=user, text=text, is_admin=is_admin)
