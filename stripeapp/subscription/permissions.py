from rest_framework.permissions import BasePermission


class IsSameUser(BasePermission):
    def has_permission(self, request, view):
        user_id = view.kwargs.get('user_id')
        if(request.user):
            return str(request.user.id) == user_id
        return false
