from rest_framework import serializers
from .models import User, FriendRequest


class SimpleUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_superuser', 'bio', 'avatar']


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'user_permissions', 'groups', 'friends', 'blocked', 'is_active', 'date_joined']


class FriendRequestSerializers(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'


class FriendsAndBlockedSerializers(serializers.ModelSerializer):
    friendRequest = serializers.SerializerMethodField(required=False)

    def get_friendRequest(self, obj):
        friendRequestsList = FriendRequest.objects.filter(toUser=obj) | FriendRequest.objects.filter(fromUser=obj)
        serializer = FriendRequestSerializers(friendRequestsList, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = ['friends', 'blocked', 'friendRequest']
