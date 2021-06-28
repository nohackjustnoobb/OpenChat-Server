from rest_framework import routers
from django.urls import path, include
from .views import UserViewSet, MyInfo, CreateUser, FriendsAndBlockedViewSet, CreateFriendsRequest, FriendRequestReplyOrCancel, \
    BlockOrUnBlockUser

router = routers.DefaultRouter()
router.register(r'info', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create/', CreateUser.as_view()),
    path('me/', MyInfo.as_view()),
    path('me/friends/', FriendsAndBlockedViewSet.as_view({'get': 'list'})),
    path('<int:pk>/remove-friend/', FriendsAndBlockedViewSet.as_view({'delete': 'destroy'})),
    path('<int:pk>/create-friend-request/', CreateFriendsRequest.as_view()),
    path('<int:pk>/block/', BlockOrUnBlockUser.as_view()),
    path('friend-request/<int:pk>/', FriendRequestReplyOrCancel.as_view()),
]
