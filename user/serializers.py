from rest_framework import serializers
from .models import User, FriendRequest


class SimpleUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_superuser', 'is_dev', 'bio', 'avatar']


class UserSerializers(serializers.ModelSerializer):
    friends = SimpleUserSerializers(many=True, read_only=True)
    blocked = SimpleUserSerializers(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'groups']


class FriendRequestSerializers(serializers.ModelSerializer):
    fromUser = SimpleUserSerializers(read_only=True)
    toUser = SimpleUserSerializers(read_only=True)

    class Meta:
        model = FriendRequest
        fields = '__all__'


class FriendsAndBlockedSerializers(serializers.ModelSerializer):
    friends = SimpleUserSerializers(many=True, read_only=True)
    blocked = SimpleUserSerializers(many=True, read_only=True)
    friendRequest = FriendRequestSerializers(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['friends', 'blocked', 'friendRequest']
