# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated and (self.scope["user"].is_staff or self.scope["user"].is_superuser):
            self.group_name = 'staff_notifications' if self.scope["user"].is_staff else 'admin_notifications'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
