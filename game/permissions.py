from rest_framework import permissions


class IsOneOfPlayers(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in [p.user for p in obj.players.all()]


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPlayer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.player.user == request.user
