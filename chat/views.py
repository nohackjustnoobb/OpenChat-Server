from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Group, Message
from .serializers import SimpleGroupSerializers, GroupSerializers
from user.models import User
from user.serializers import SimpleUserSerializers


class AdminOrIsMemberPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all() or request.user.is_superuser


# todo: patch server info
class GroupViewSets(viewsets.ViewSet):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, AdminOrIsMemberPermission]

    def list(self, request):
        user = request.user
        groupsList = Group.objects.filter(members__in=[user]).distinct()
        serializer = SimpleGroupSerializers(groupsList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        group = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, group)
        serializer = GroupSerializers(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # delete server
    def destroy(self, request, pk=None):
        user = request.user
        group = get_object_or_404(self.queryset, pk=pk)
        if group.owner == user or user.is_superuser:
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)


class AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj.owner or request.user in obj.groupAdmins.all() or (
                request.user in obj.members.all() and request.method in permissions.SAFE_METHODS)


class GroupMembersViewSets(viewsets.ViewSet):
    queryset = Group.members
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def list(self, request, pk=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        serializer = SimpleUserSerializers(group.members.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Maybe todo: user can only invite them friends
    def create(self, request, pk=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        addMembers = request.data.get('members')
        # not allow empty list
        if addMembers:
            # convert pk to objects
            addMembersList = User.objects.filter(pk__in=addMembers)
            if addMembersList.count() != len(addMembers):
                return Response(status=status.HTTP_404_NOT_FOUND)
            # not allow to add user that is already in group
            if not group.members.filter(pk__in=addMembers).exists():
                group.members.add(*addMembersList)
                serializer = SimpleUserSerializers(group.members.all(), many=True)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, userPK=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        kickMember = get_object_or_404(group.members.all(), pk=userPK)
        if not kickMember == group.owner and not kickMember != request.user:
            if kickMember in group.groupAdmins.all() or request.user == group.owner:
                group.members.remove(kickMember)
                if kickMember in group.groupAdmins.all():
                    group.groupAdmins.remove(kickMember)
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GroupAdminsViewSets(viewsets.ViewSet):
    queryset = Group.groupAdmins
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def list(self, request, pk=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        serializer = SimpleUserSerializers(group.groupAdmins.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        # only owner can add user to group admins
        if request.user != group.owner:
            Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        addAdmins = request.data.get('admins')
        if addAdmins and group.owner.id not in addAdmins:
            addAdminsList = group.members.filter(pk__in=addAdmins)
            if addAdminsList.count() == len(addAdmins) and not group.groupAdmins.filter(pk__in=addAdmins).exists():
                group.groupAdmins.add(*addAdminsList)
                serializer = SimpleUserSerializers(group.groupAdmins.all(), many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, userPK=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        if request.user == group.owner:
            removeAdmin = get_object_or_404(group.groupAdmins.all(), pk=userPK)
            group.groupAdmins.remove(removeAdmin)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LeaveGroup(APIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def get(self, request, pk=None):
        group = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, group)
        user = request.user
        group.members.remove(user)
        if user in group.groupAdmins.all():
            group.groupAdmins.remove(user)
        return Response(status=status.HTTP_202_ACCEPTED)


class CreateGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            groupName = request.data['groupName']
            owner = request.user
            description = request.data.get('description')
            avatar = request.data.get('avatar')
            members = request.data['members']

            if not len(members) or type(members) != list or owner.id in members or not len(groupName):
                raise KeyError
            else:
                membersLists = User.objects.filter(pk__in=members)
                if membersLists.count() != len(members):
                    return Response(status=status.HTTP_404_NOT_FOUND)

            if not description:
                description = ''

            groupCreated = Group.objects.create(groupName=groupName, owner=owner, isDM=False, description=description,
                                                avatar=avatar)
            groupCreated.members.add(owner, *membersLists)
            serializer = GroupSerializers(groupCreated)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
