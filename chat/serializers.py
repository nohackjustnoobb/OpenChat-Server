from .models import Message, Group
from user.serializers import SimpleUserSerializers
from rest_framework import serializers


class SimpleMessageSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers(read_only=True)

    class Meta:
        model = Message
        exclude = ['relyTo', 'memberRead']


class SimpleGroupSerializers(serializers.ModelSerializer):
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'groupName', 'avatar', 'lastMessage']


class MessageReadSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers(read_only=True)
    sentGroup = SimpleGroupSerializers(read_only=True)
    relyTo = SimpleMessageSerializers(read_only=True)
    memberRead = SimpleUserSerializers(many=True, read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MessageSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers(read_only=True)
    sentGroup = SimpleGroupSerializers(read_only=True)
    relyTo = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Message
        exclude = ['memberRead']


class GroupSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers()
    members = SimpleUserSerializers(many=True, read_only=True)
    groupAdmins = SimpleUserSerializers(many=True, read_only=True)
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        exclude = ['isDM', 'messages']


class DMSerializers(serializers.ModelSerializer):
    members = SimpleUserSerializers(many=True, read_only=True)
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        fields = ['members', 'pinnedMessage', 'id', 'createDate', 'lastMessage']
