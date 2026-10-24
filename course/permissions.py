from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет принадлежность пользователя к модераторам."""

    def has_permission(self, request, view):
        """Проверяет, входит ли пользователь в группу модераторов."""
        return request.user.groups.filter(name='Модераторы').exists()

    def has_object_permission(self, request, view, obj):
        """Проверяет права модератора для объекта."""
        return self.has_permission(request, view)


class IsOwner(BasePermission):
    """Проверяет владельца объекта."""

    def has_object_permission(self, request, view, obj):
        """Проверяет, принадлежит ли объект пользователю."""
        return obj.owner == request.user
