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
        exclude = ['relyTo', 'memberRead']


class MessageReadSerializers(serializers.ModelSerializer):
    relyTo = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MessageSerializers(serializers.ModelSerializer):
    relyTo = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Message
        exclude = ['memberRead']


class GroupSerializers(serializers.ModelSerializer):
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        exclude = ['messages', 'logs', 'pinnedMessages']


class DMSerializers(serializers.ModelSerializer):
    lastMessage = SimpleMessageSerializers(read_only=True)

    class Meta:
        model = Group
        fields = ['members', 'pinnedMessages', 'id', 'createDate', 'lastMessage']


class ModifyLogSerializers(serializers.ModelSerializer):
    action = ChoicesSerializerField()

    class Meta:
        model = ModifyLog
        exclude = ['id', 'memberSaw']
