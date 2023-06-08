from uuid import UUID

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import CourseSerializer
from ..models import Course, Gym, Room


class CourseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        gyms = self._get_gyms_within_user_group(request)
        if pk:
            course = Course.objects.filter(id=pk, gym__in=gyms).first()
            if course is None:
                return Response({"error": "Course not found."}, status=404)
            serializer = CourseSerializer(course)
        else:
            courses = Course.objects.filter(gym__in=gyms).all()
            serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        gym_ids = [gym.id for gym in self._get_gyms_within_user_group(request)]
        room_ids = Room.objects.filter(gym__in=gym_ids).values_list('id', flat=True)
        if UUID(request.data["gym"]) not in gym_ids or UUID(request.data["room"]) not in room_ids:
            return Response(
                {
                    "error": "Gym/Room not found. Are you sure the gym/room exists within your group?"
                },
                status=404,
            )
        if serializer.is_valid():
            course = serializer.save()
            return Response(CourseSerializer(course).data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Course ID not provided."}, status=400)
        course = Course.objects.filter(id=pk).first()
        if course is None:
            return Response({"error": "Course not found."}, status=404)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            course = serializer.save()
            return Response(CourseSerializer(course).data)
        return Response(serializer.errors, status=400)

    @staticmethod
    def _get_gyms_within_user_group(request):
        user_groups = request.user.groups.all()
        gyms = Gym.objects.filter(group__in=user_groups)
        return gyms
