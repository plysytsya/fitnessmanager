from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from ..models import Message, MessageContent, Customer, Conversation
from ..serializers import MessageSerializer, ConversationSerializer


class CustomPagination(PageNumberPagination):
    page_size = 3  # Number of items per page
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "num_pages": self.page.paginator.num_pages,
                "results": data,
                "next": self.get_next_link(),
            }
        )


class UnreadMessageCountView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        unread_messages = Message.objects.filter(
            receiver=user,
            is_deleted_by_recepient=False,
            is_deleted_by_sender=False,
            is_read=False,
            is_draft=False,
        )
        return Response({"unread_messages": unread_messages.count()})


class SentMessageView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        sent_messages = Message.objects.filter(
            sender=user,
            is_deleted_by_sender=False,
        )

        serialized_messages = MessageSerializer(sent_messages, many=True)

        return Response({"sent_messages": serialized_messages.data})


class InboxView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        incoming_messages = Message.objects.filter(
            receiver=user,
            is_deleted_by_sender=False,
            is_deleted_by_recepient=False,
            is_draft=False,
            sent_at__isnull=False,
        )

        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(incoming_messages, request)
        serialized_messages = MessageSerializer(result_page, many=True)
        return paginator.get_paginated_response(serialized_messages.data)


class SendMessageView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Check if the user is a participant of the conversation
        if request.user not in conversation.participants.all():
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)