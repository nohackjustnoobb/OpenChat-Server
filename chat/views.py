from rest_framework import viewsets
from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Group, Message
from .serializers import SimpleGroupSerializers, GroupSerializers, DMSerializers, MessageSerializers, \
    MessageReadSerializers
from user.models import User
from user.serializers import SimpleUserSerializers, UserSerializers


class AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj.owner or request.user in obj.groupAdmins.all() or (
                request.user in obj.members.all() and request.method in permissions.SAFE_METHODS)


class GroupViewSets(viewsets.ViewSet):
    queryset = Group.objects.filter(isDM=False)
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def list(self, request):
        user = request.user
        groupsList = Group.objects.filter(members__in=[user], isDM=False).distinct()
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

    def partial_update(self, request, pk=None):
        group = get_object_or_404(self.queryset, pk=pk)
        updateData = request.data
        self.check_object_permissions(request, group)
        allowUpdate = ['groupName', 'description', 'avatar']
        filteredData = {}
        for key, value in updateData.items():
            if key in allowUpdate:
                filteredData[key] = value
        serializer = GroupSerializers(group, data=filteredData, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupMembersViewSets(viewsets.ViewSet):
    queryset = Group.members
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def list(self, request, pk=None):
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
        self.check_object_permissions(request, group)
        serializer = SimpleUserSerializers(group.members.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Maybe todo: user can only invite them friends
    def create(self, request, pk=None):
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
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
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
        self.check_object_permissions(request, group)
        kickMember = get_object_or_404(group.members.all(), pk=userPK)
        if not kickMember == group.owner and kickMember != request.user:
            if kickMember not in group.groupAdmins.all() or request.user == group.owner:
                group.members.remove(kickMember)
                if kickMember in group.groupAdmins.all():
                    group.groupAdmins.remove(kickMember)
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class GroupAdminsViewSets(viewsets.ViewSet):
    queryset = Group.groupAdmins
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def list(self, request, pk=None):
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
        self.check_object_permissions(request, group)
        serializer = SimpleUserSerializers(group.groupAdmins.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
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
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
        self.check_object_permissions(request, group)
        if request.user == group.owner:
            removeAdmin = get_object_or_404(group.groupAdmins.all(), pk=userPK)
            group.groupAdmins.remove(removeAdmin)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LeaveGroup(APIView):
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def get(self, request, pk=None):
        group = get_object_or_404(Group.objects.filter(isDM=False), pk=pk)
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


class DMViewSets(viewsets.ViewSet):
    queryset = Group.objects.filter(isDM=True)
    permission_classes = [IsAuthenticated, AdminOrIsGroupAdminOrIsGroupMemberReadOnlyPermission]

    def list(self, request):
        user = request.user
        serializer = DMSerializers(self.queryset.filter(members=user.id), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        user = request.user
        DM = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, DM)
        DMUser = DM.members.exclude(pk=user.id).first()
        serializer = UserSerializers(DMUser)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateDM(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        userFriendPK = request.data.get('friend')
        if userFriendPK:
            userFriend = get_object_or_404(user.friends.all(), pk=userFriendPK)
            DMGroupList = Group.objects.filter(isDM=True, members=user.id).filter(members=userFriendPK)
            if DMGroupList.exists():
                serializer = DMSerializers(DMGroupList.first())
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                groupName = f'{user.id}, {userFriend.id}'
                DMCreated = Group.objects.create(groupName=groupName, isDM=True)
                DMCreated.members.add(user, userFriend)
                serializer = DMSerializers(DMCreated)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IsGroupMemberPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all()


class MessageViewSets(viewsets.ViewSet):
    queryset = Message.objects.all()
    permission_classes = [IsGroupMemberPermission]

    def list(self, request, pk=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        for message in group.messages.exclude(memberRead__in=[request.user.id]):
            message.memberRead.add(request.user)
        serializer = MessageSerializers(group.messages.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        group = get_object_or_404(Group.objects.all(), pk=pk)
        self.check_object_permissions(request, group)
        messageData = request.data
        additionFile = messageData.get('additionFile')
        additionImage = messageData.get('additionImage')
        content = messageData.get('content')
        relyTo = messageData.get('relyTo')
        if relyTo:
            relyTo = get_object_or_404(group.messages.all(), pk=relyTo)
        messageCreated = Message.objects.create(owner=request.user, additionFile=additionFile,
                                                additionImage=additionImage, content=content, relyTo=relyTo)
        messageCreated.MemberRead.add(request.user)
        group.messages.add(messageCreated)
        serializer = MessageSerializers(messageCreated)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
