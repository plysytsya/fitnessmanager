from rest_framework import serializers
from .models import (
    Message,
    MessageContent,
    Conversation
)


class MessageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageContent
        fields = ["text", "created_at", "updated_at", "is_html"]

    def create(self, validated_data):
        return MessageContent.objects.create(**validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender_first_name = serializers.ReadOnlyField(source='sender.first_name')
    sender_last_name = serializers.ReadOnlyField(source='sender.last_name')
    sender_email = serializers.ReadOnlyField(source='sender.email')
    messagecontent_set = MessageContentSerializer(many=True)

    class Meta:
        model = Message
        fields = [
            "sender",
            "sender_first_name",
            "sender_last_name",
            "sender_email",
            "receiver",
            "subject",
            "created_at",
            "updated_at",
            "is_draft",
            "sent_at",
            "read_at",
            "is_read",
            "is_impression",
            "messagecontent_set",
        ]

    def create(self, validated_data):
        message_contents = validated_data.pop('messagecontent_set')
        message = Message.objects.create(**validated_data)

        for message_content in message_contents:
            MessageContent.objects.create(message=message, **message_content)
        return message


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'messages']
