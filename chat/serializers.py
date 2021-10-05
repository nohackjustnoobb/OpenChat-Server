from .models import Message, Group, ModifyLog
from rest_framework import serializers


class ChoicesSerializerField(serializers.SerializerMethodField):

    def to_representation(self, value):
        method_name = 'get_{field_name}_display'.format(field_name=self.field_name)
        method = getattr(value, method_name)
        return method()


class SimpleMessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ['replyTo', 'memberRead']


class MessageReadSerializers(serializers.ModelSerializer):
    replyTo = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MessageSerializers(serializers.ModelSerializer):
    replyTo = SimpleMessageSerializers(read_only=True)
    pinned = serializers.SerializerMethodField(required=False)

    def get_pinned(self, obj):
        return obj.pinnedMessages.all().exists()

    class Meta:
        model = Message
        exclude = ['memberRead']


class GroupSerializers(serializers.ModelSerializer):
    lastMessage = SimpleMessageSerializers(read_only=True)
    unReadMessage = serializers.SerializerMethodField(required=False)

    def get_unReadMessage(self, obj):
        user = self.context.get('user')
        if user:
            return obj.messages.exclude(memberRead__in=[user.id]).count()
        return

    class Meta:
        model = Group
        exclude = ['messages', 'logs', 'pinnedMessages']


class DMSerializers(serializers.ModelSerializer):
    lastMessage = SimpleMessageSerializers(read_only=True)
    unReadMessage = serializers.SerializerMethodField(required=False)

    def get_unReadMessage(self, obj):
        user = self.context.get('user')
        if user:
            return obj.messages.exclude(memberRead__in=[user.id]).count()
        return

    class Meta:
        model = Group
        fields = ['members', 'pinnedMessages', 'id', 'createDate', 'lastMessage', 'unReadMessage']


class ModifyLogSerializers(serializers.ModelSerializer):
    action = ChoicesSerializerField()

    class Meta:
        model = ModifyLog
        exclude = ['id', 'memberSaw']
