from rest_framework import routers
from django.urls import path, include
from .views import UserViewSet, MyInfo, CreateUser, FriendsViewSet, CreateFriendsRequest, FriendRequestReplyOrCancel

router = routers.DefaultRouter()
router.register(r'info', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', CreateUser.as_view()),
    path('me/', MyInfo.as_view()),
    path('me/friends/', FriendsViewSet.as_view({'get': 'list'})),
    path('me/friends/<int:pk>/', FriendsViewSet.as_view({'get': 'retrieve'})),
    path('<int:pk>/create-friend-request/', CreateFriendsRequest.as_view()),
    path('friend-request/<int:pk>/', FriendRequestReplyOrCancel.as_view()),
]
