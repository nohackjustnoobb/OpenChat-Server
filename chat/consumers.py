import asyncio
import json
from rest_framework.authtoken.models import Token
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from user.serializers import UserSerializers


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scope['user'] = AnonymousUser()
        await self.accept()

    async def disconnect(self, close_code):
        await database_sync_to_async(self.toggleOnline)()

    async def receive(self, text_data):
        jsonData = json.loads(text_data)
        Authorization = jsonData.get('Authorization')
        if Authorization:
            token = Authorization.split()[1]
            user = await self.AuthorizationByToken(token)
            if user.is_authenticated:
                await self.send(text_data=json.dumps(UserSerializers(user).data))
            else:
                await self.send(text_data=json.dumps({'error': 'Token is not valid'}))

    @database_sync_to_async
    def AuthorizationByToken(self, tokenKey):
        try:
            if self.scope['user'].is_authenticated:
                raise Token.DoesNotExist
            self.scope['user'] = Token.objects.get(key=tokenKey).user
            self.toggleOnline()
            return self.scope['user']
        except Token.DoesNotExist:
            return self.scope['user']

    def toggleOnline(self):
        self.scope['user'].isOnline = not self.scope['user'].isOnline
        self.scope['user'].save()
