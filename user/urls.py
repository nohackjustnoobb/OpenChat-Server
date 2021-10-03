from django.urls import path
from .views import UserViewSet, MyInfo, CreateUser, FriendsAndBlockedViewSet, CreateFriendsRequest, \
    FriendRequestViewSets, BlockOrUnBlockUser

urlpatterns = [
    path('', UserViewSet.as_view({'get': 'list'})),
    path('<int:pk>/', UserViewSet.as_view({'get': 'retrieve'})),
    path('create/', CreateUser.as_view()),
    path('me/', MyInfo.as_view()),
    path('me/friends/', FriendsAndBlockedViewSet.as_view({'get': 'list'})),
    path('<int:pk>/remove-friend/', FriendsAndBlockedViewSet.as_view({'delete': 'destroy'})),
    path('<int:pk>/create-friend-request/', CreateFriendsRequest.as_view()),
    path('<int:pk>/block/', BlockOrUnBlockUser.as_view()),
    path('friend-request/', FriendRequestViewSets.as_view({'get': 'list'})),
    path('friend-request/<int:pk>/', FriendRequestViewSets.as_view({'get': 'retrieve', 'delete': 'destroy'})),
]
