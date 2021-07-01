from .serializers import UserSerializers, FriendsAndBlockedSerializers, SimpleUserSerializers, FriendRequestSerializers
from .models import User, FriendRequest
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import re


# password validation
def password_check(passwd):
    SpecialSym = ['$', '@', '#', '%', '_']
    val = True
    error_message = ''

    if len(passwd) < 8:
        error_message = 'Password length should be at least 8'
        val = False
    elif len(passwd) > 20:
        error_message = 'Password length should be not be greater than 20'
        val = False
    elif not any(char.isdigit() for char in passwd):
        error_message = 'Password should have at least one numeral'
        val = False
    elif not any(char.isupper() for char in passwd) and not any(char.islower() for char in passwd):
        error_message = 'Password should have at least one uppercase/lowercase letter'
        val = False
    elif any(char in SpecialSym for char in passwd):
        error_message = 'Password should not have the symbols $@#%_'
        val = False

    return [val, error_message]


# email validation
def email_check(email):
    regex = '^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$'
    return bool(re.search(regex, email))


# User ViewSet
class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    # todo: max result return and multiple page
    def list(self, request):
        # show more info if user is admin
        if request.user.is_superuser:
            serializer = UserSerializers(self.queryset, many=True)
        else:
            serializer = SimpleUserSerializers(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        # show more info if user is admin
        if request.user.is_superuser or user.friends.filter(pk=request.user.id).exists():
            serializer = UserSerializers(user)
        else:
            serializer = SimpleUserSerializers(user)
        return Response(serializer.data)


# admin or owner can GET and PATCH with limited option permission
class AdminOrOwnerPlusSafeMethodsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        allowed_change = ['password', 'avatar', 'bio', 'username']
        if request.method in permissions.SAFE_METHODS or request.data.keys() in allowed_change \
                or request.user.is_superuser or request.method == 'PATCH':
            return True
        return False


# user own profile
class MyInfo(APIView):
    permission_classes = [IsAuthenticated, AdminOrOwnerPlusSafeMethodsPermission]

    def get(self, request, format=None):
        serializer = UserSerializers(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        user = request.user
        update_data = request.data
        # try pop the password out
        try:
            update_data.data.pop('password')
        finally:
            # update data and check if it is valid
            serializer = UserSerializers(user, data=update_data, partial=True)
            if serializer.is_valid():
                try:
                    # apply password if it is available
                    password = request.data['password']
                    password_check_result = password_check(password)
                    if password_check_result[0]:
                        user.set_password(password)
                    else:
                        return Response({'error': password_check_result[1]}, status=status.HTTP_400_BAD_REQUEST)
                finally:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'error': 'Data is invalid'}, status=status.HTTP_400_BAD_REQUEST)


class FriendsAndBlockedViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_class = [IsAuthenticated]

    def list(self, request):
        user = request.user
        serializer = FriendsAndBlockedSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = request.user
        friend = get_object_or_404(user.friends.all(), pk=pk)
        user.friends.remove(friend)
        friend.friends.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateFriendsRequest(APIView):
    queryset = FriendRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        user = request.user
        # try to get message for friend request
        try:
            message = request.data['message']
        except KeyError:
            message = ''
        # user can't make friend request to themselves
        if user.id == pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        toUser = get_object_or_404(User.objects.all(), pk=pk)
        try:
            toUser.blocked.get(pk=user.id)
            return Response({'error': 'Blocked'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            # user can't make friend request to their friends
            try:
                user.friends.get(pk=toUser.id)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # user can't spam friends request
                requestMade = FriendRequest.objects.filter(fromUser=user, toUser=toUser)
                if requestMade:
                    # if user already made friends request, return the request user made before
                    return Response(FriendRequestSerializers(requestMade[0]).data, status=status.HTTP_400_BAD_REQUEST)
                requestCreated = FriendRequest.objects.create(toUser=toUser, fromUser=user, message=message)
                serializer = FriendRequestSerializers(requestCreated)
                return Response(serializer.data, status=status.HTTP_201_CREATED)


# admin and the user who is being requested have permission to reply
# admin and the user who create request have permission to DELETE
# both user can GET the friend request
class AdminOrBeingRequestedOrOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS and (
                request.user == obj.toUser or not request.query_params and request.user == obj.fromUser)) or (
                       request.method == 'DELETE' and request.user == obj.fromUser) or request.user.is_superuser


class FriendRequestReplyOrCancel(APIView):
    queryset = FriendRequest.objects.all()
    permission_classes = [AdminOrBeingRequestedOrOwnerPermission]

    def get(self, request, pk=None):
        friendRequest = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(self.request, friendRequest)
        # try to get reply
        try:
            reply = request.query_params['reply']
            if reply == 'accept':
                fromUser = friendRequest.fromUser
                toUser = friendRequest.toUser
                toUser.friends.add(fromUser)
                fromUser.friends.add(toUser)
            elif reply != 'decline':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            friendRequest.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except KeyError:
            # if there are not query params return the request
            serializer = FriendRequestSerializers(friendRequest)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        friendRequest = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(self.request, friendRequest)
        friendRequest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockOrUnBlockUser(APIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        blockedUser = get_object_or_404(self.queryset, pk=pk)
        user.friends.remove(blockedUser)
        blockedUser.friends.remove(user)
        user.blocked.add(blockedUser)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        user = request.user
        blockedUser = get_object_or_404(user.blocked.all(), pk=pk)
        user.blocked.remove(blockedUser)
        return Response(status=status.HTTP_200_OK)


class CreateUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        try:
            username = request.data['username']
            email = request.data['email']
            password = request.data['password']
            if not (username and email and password):
                return Response({'error': 'Username, password or email can\'t be empty'},
                                status=status.HTTP_400_BAD_REQUEST)
            password_check_result = password_check(password)
            # check username and email is not registered
            try:
                User.objects.get(username=username)
                return Response({'error': 'This username was took by other user'},
                                status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                try:
                    User.objects.get(email=email)
                    return Response({'error': 'This email was took by other user'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    if not password_check_result[0]:
                        return Response({'error': password_check_result[1]}, status=status.HTTP_400_BAD_REQUEST)
                    elif not email_check(email):
                        return Response({'error': 'This email is invalid'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        user = User.objects.create_user(username, email, password)
                        return Response(UserSerializers(user).data, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response({'error': 'Missing username, password or email'}, status=status.HTTP_400_BAD_REQUEST)
