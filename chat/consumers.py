import asyncio
import json
from rest_framework.authtoken.models import Token
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from user.serializers import UserSerializers, SimpleUserSerializers
from chat.serializers import GroupSerializers
from chat.models import Group
from user.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scope['user'] = AnonymousUser()
        await self.accept()

    async def disconnect(self, close_code):
        await database_sync_to_async(self.toggleOnline)(False)
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(str(self.scope['user'].id), self.channel_name)

    async def receive(self, text_data):
        jsonData = json.loads(text_data)

        # Authorization
        Authorization = jsonData.get('Authorization')
        if Authorization:
            token = Authorization.split()[1]
            if self.scope['user'].is_authenticated:
                await self.send(text_data=json.dumps({'yourInfo': UserSerializers(self.scope['user']).data}))
            else:
                user = await self.AuthorizationByToken(token)
                if user.is_authenticated:
                    await self.channel_layer.group_add(str(user.id), self.channel_name)
                    groupsList = await self.getUserGroupAndDM()
                    await self.send(text_data=json.dumps({'yourInfo': UserSerializers(user).data,
                                                          'group': groupsList}))
                else:
                    await self.send(text_data=json.dumps({'error': 'Token is not valid'}))

        # get User Data
        getUsers = jsonData.get('users')
        if self.scope['user'].is_authenticated and getUsers:
            usersList = await self.getUserInfo(getUsers)
            await self.send(text_data=json.dumps({'users': usersList}))

    @database_sync_to_async
    def getUserInfo(self, users):
        usersList = User.objects.filter(pk__in=users)
        userFriendPK = [user.id for user in self.scope['user'].friends.all()]
        isFriend = usersList.filter(pk__in=userFriendPK)
        notFriend = usersList.exclude(pk__in=userFriendPK)
        return [*SimpleUserSerializers(notFriend, many=True).data, *UserSerializers(isFriend, many=True).data]

    @database_sync_to_async
    def getUserGroupAndDM(self):
        groupsList = Group.objects.filter(members__in=[self.scope['user'].id])
        return GroupSerializers(groupsList.all(), many=True).data

    @database_sync_to_async
    def AuthorizationByToken(self, tokenKey):
        try:
            if self.scope['user'].is_authenticated:
                raise Token.DoesNotExist
            self.scope['user'] = Token.objects.get(key=tokenKey).user
            self.toggleOnline(True)
            return self.scope['user']
        except Token.DoesNotExist:
            return self.scope['user']

    def toggleOnline(self, status):
        self.scope['user'].isOnline = status
        self.scope['user'].save()

    async def sendMessage(self, event):
        await self.send(text_data=event['message'])
