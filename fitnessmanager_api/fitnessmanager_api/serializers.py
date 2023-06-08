from rest_framework import serializers
from .models import (
    Message,
    MessageContent,
    Room,
    Course, Gym, Customer,
)


class MessageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageContent
        fields = ["text", "created_at", "updated_at", "is_html"]

    def create(self, validated_data):
        return MessageContent.objects.create(**validated_data)


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.ReadOnlyField(source="id")  # Add this line

    sender_first_name = serializers.ReadOnlyField(source="sender.first_name")
    sender_last_name = serializers.ReadOnlyField(source="sender.last_name")
    sender_email = serializers.ReadOnlyField(source="sender.email")
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
        message_contents = validated_data.pop("messagecontent_set")
        message = Message.objects.create(**validated_data)

        for message_content in message_contents:
            MessageContent.objects.create(message=message, **message_content)
        return message


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "gym"]


class CourseSerializer(serializers.ModelSerializer):
    gym = serializers.PrimaryKeyRelatedField(queryset=Gym.objects.all())
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), required=True)
    trainer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.filter(is_staff=True), required=False)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "duration",
            "max_participants",
            "gym",
            "room",
            "trainer",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        return Course.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.duration = validated_data.get("duration", instance.duration)
        instance.max_participants = validated_data.get(
            "max_participants", instance.max_participants
        )
        instance.save()
        return instance
