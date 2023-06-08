from rest_framework import permissions


class IsInSameGroup(permissions.BasePermission):
    """
    Custom permission to only allow users in the same group to access the object.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the group of the user making the request is the same as that of the room.
        return obj.gym.group in request.user.groups.all()
