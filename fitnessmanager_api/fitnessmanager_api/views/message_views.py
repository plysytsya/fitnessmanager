from typing import Optional

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Message
from ..serializers import MessageSerializer


class CustomPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "num_pages": self.page.paginator.num_pages,
                "results": data,
                "next": self.get_next_link(),
                "current_page": self.page.number,
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
        ).order_by("-sent_at")

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


class MessageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, message_id: int) -> Response:
        """
        Retrieve details of a specific message.

        :param request: HTTP request from the client.
        :param message_id: ID of the message.
        :return: HTTP response with the details of the message.
        """
        message = get_object_or_404(Message, id=message_id, receiver=request.user)
        serialized_message = MessageSerializer(message)
        return Response(serialized_message.data)

    def put(self, request: Request, message_id: int) -> Response:
        """
        Modify a specific message.

        :param request: HTTP request from the client.
        :param message_id: ID of the message.
        :return: HTTP response with the modified message or error message.
        """
        message = get_object_or_404(Message, id=message_id)

        if request.user == message.sender:
            response = self._handle_sender_modification(request, message)
        elif request.user == message.receiver:
            response = self._handle_receiver_modification(request, message)
        else:
            response = Response(
                {"detail": "You are not allowed to modify this message."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if response:
            return response

        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _handle_sender_modification(request: Request, message: Message) -> Optional[Response]:
        """
        Handle modification request from the sender.

        :param request: HTTP request from the client.
        :return: HTTP response with error message if sender tries to modify 'is_read' or 'is_impression',
        None otherwise.
        """
        if request.user == message.receiver:  # sent to himself
            return None
        if "is_read" in request.data or "is_impression" in request.data:
            return Response(
                {"detail": "Only the receiver can modify is_read or is_impression."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    @staticmethod
    def _handle_receiver_modification(request: Request, message: Message) -> Optional[Response]:
        """
        Handle modification request from the receiver.

        :param request: HTTP request from the client.
        :return: HTTP response with error message if receiver tries to modify fields other than
        'is_read' and 'is_impression', None otherwise.
        """
        if request.user == message.sender:  # sent to himself
            return None
        if any(key not in ["is_read", "is_impression"] for key in request.data.keys()):
            return Response(
                {
                    "detail": "You are only allowed to modify 'is_read' and 'is_impression'"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None
