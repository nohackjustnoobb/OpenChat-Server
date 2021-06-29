from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Group, Message
from .serializers import SimpleGroupSerializers, GroupSerializers
from user.models import User


class GroupViewSets(viewsets.ViewSet):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        groupsList = Group.objects.filter(members__in=[user]).distinct()
        if request.user.is_superuser:
            serializer = GroupSerializers(self.queryset, many=True)
        else:
            serializer = SimpleGroupSerializers(groupsList, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        user = request.user
        group = get_object_or_404(self.queryset, pk=pk)
        if user in group.members.all() or request.user.is_superuser:
            serializer = GroupSerializers(group)
        else:
            serializer = SimpleGroupSerializers(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = request.user
        group = get_object_or_404(self.queryset, pk=pk)
        if group.owner == user or user.is_superuser:
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN)


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
