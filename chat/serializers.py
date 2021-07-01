from .models import Message, Group
from user.serializers import SimpleUserSerializers
from rest_framework import serializers


class SimpleMessageSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers(read_only=True)

    class Meta:
        model = Message
        exclude = ['relyTo', 'MemberRead', 'sentGroup']


class SimpleGroupSerializers(serializers.ModelSerializer):
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'groupName', 'avatar', 'lastMessage']


class MessageSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers(read_only=True)
    sentGroup = SimpleGroupSerializers(read_only=True)
    relyTo = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class GroupSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers()
    members = SimpleUserSerializers(many=True, read_only=True)
    groupAdmins = SimpleUserSerializers(many=True, read_only=True)
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        exclude = ['isDM']


class DMSerializers(serializers.ModelSerializer):
    members = SimpleUserSerializers(many=True, read_only=True)
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        fields = ['members', 'pinnedMessage', 'id', 'createDate', 'lastMessage']
