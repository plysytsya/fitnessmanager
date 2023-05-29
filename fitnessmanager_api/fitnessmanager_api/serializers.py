from rest_framework import serializers
from .models import (
    Message,
    MessageContent,
)


class MessageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageContent
        fields = ["text", "created_at", "updated_at", "is_html"]

    def create(self, validated_data):
        return MessageContent.objects.create(**validated_data)


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.ReadOnlyField(source='id')  # Add this line

    sender_first_name = serializers.ReadOnlyField(source='sender.first_name')
    sender_last_name = serializers.ReadOnlyField(source='sender.last_name')
    sender_email = serializers.ReadOnlyField(source='sender.email')
    messagecontent_set = MessageContentSerializer(many=True)

    class Meta:
        model = Message
        fields = [
            "message_id",  # Include the message ID field
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
