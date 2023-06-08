from uuid import UUID

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import RoomSerializer
from ..models import Room, Gym
from ..permissions import IsInSameGroup


class RoomView(APIView):
    permission_classes = [IsAuthenticated, IsInSameGroup]

    def get(self, request, pk=None):
        user_groups = request.user.groups.all()
        gyms = Gym.objects.filter(group__in=user_groups)
        if pk:
            room = Room.objects.filter(id=pk, gym__in=gyms).first()
            if room is None:
                return Response({"error": "Room not found."}, status=404)
            serializer = RoomSerializer(room)
        else:
            rooms = Room.objects.filter(gym__in=gyms)
            serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_groups = request.user.groups.all()
        gym_ids = Gym.objects.filter(group__in=user_groups).values_list('id', flat=True)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            if UUID(request.data["gym"]) not in gym_ids:
                return Response(
                    {
                        "error": "Gym not found. Are you sure the gym exists within your group?"
                    },
                    status=404,
                )
            room = serializer.save()
            return Response(RoomSerializer(room).data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Room ID not provided."}, status=400)
        user_groups = request.user.groups.all()
        room = Room.objects.filter(id=pk, gym__group__in=user_groups).first()
        if room is None:
            return Response({"error": "Room not found."}, status=404)
        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            room = serializer.save()
            return Response(RoomSerializer(room).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Room ID not provided."}, status=400)
        user_groups = request.user.groups.all()
        room = Room.objects.filter(id=pk, gym__group__in=user_groups).first()
        if room is None:
            return Response({"error": "Room not found."}, status=404)
        room.delete()
        return Response({"message": "Room has been deleted."})
