from .models import Message, Group
from user.serializers import SimpleUserSerializers
from rest_framework import serializers


class SimpleGroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'groupName', 'description', 'avatar']


class SimpleMessageSerializers(serializers.ModelSerializer):
    owner = SimpleUserSerializers(read_only=True)

    class Meta:
        model = Message
        exclude = ['sendDateTime', 'relyTo', 'MemberRead', 'sentGroup']


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

    class Meta:
        model = Group
        fields = '__all__'
