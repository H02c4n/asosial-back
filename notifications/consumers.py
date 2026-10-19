import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Kullanıcıya özel WebSocket bağlantısı.
    Her kullanıcı kendi grubuna katılır: 'user_<id>'
    """

    async def connect(self):
        #print(f"\n>>> [CONSUMER] connect çağrıldı, scope.user={self.scope['user']}\n")
        user = self.scope['user']

        if user.is_anonymous:
            #print(">>> [CONSUMER] Kullanıcı ANONİM → close(4001)\n")
            await self.close(code=4001)
            return

        self.group_name = f'user_{user.id}'
        #print(f">>> [CONSUMER] accept ediliyor, grup={self.group_name}\n")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
        'type': 'connected',
        'message': f'Bildirimlere bağlısın, @{user.username}',
        }))

    async def disconnect(self, close_code):
        # Gruptan ayrıl
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        İstemciden gelen mesajlar (şimdilik ping-pong dışında bir şey yapmıyoruz).
        İleride 'mark as read' gibi komutlar buraya eklenebilir.
        """
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except json.JSONDecodeError:
            pass

    # ------------------------------------------------------------------
    # Kanal katmanından gelen olayları işleyen metotlar
    # group_send(... {"type": "notification.message", ...}) → bu metot çalışır
    # ------------------------------------------------------------------
    async def notification_message(self, event):
        """Bildirim olayını istemciye ilet."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data'],
        }))