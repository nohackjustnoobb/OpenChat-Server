from django.urls import path, include
from .views import GroupViewSets, CreateGroup, GroupMembersViewSets, GroupAdminsViewSets, LeaveGroup, CreateDM, \
    DMViewSets, MessageViewSets, GroupLogs, PinnedMessageViewSet

MessageUrlPatterns = [
    path('<int:pk>/messages/', MessageViewSets.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/messages/<int:messagePK>/', MessageViewSets.as_view({'get': 'retrieve', 'delete': 'destroy'})),
    path('<int:pk>/messages/<int:messagePK>/pin/',
         PinnedMessageViewSet.as_view({'post': 'create', 'delete': 'destroy'})),
    path('<int:pk>/messages/pinned/', PinnedMessageViewSet.as_view({'get': 'list'})),
]

GroupUrlPatterns = [
    path('', GroupViewSets.as_view({'get': 'list'})),
    path('', include(MessageUrlPatterns)),
    path('<int:pk>/', GroupViewSets.as_view({'get': 'retrieve', 'delete': 'destroy', 'patch': 'partial_update'})),
    path('<int:pk>/logs/', GroupLogs.as_view()),
    path('<int:pk>/members/', GroupMembersViewSets.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/members/<int:userPK>/', GroupMembersViewSets.as_view({'delete': 'destroy'})),
    path('<int:pk>/leave/', LeaveGroup.as_view()),
    path('<int:pk>/admins/', GroupAdminsViewSets.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/admins/<int:userPK>/', GroupAdminsViewSets.as_view({'delete': 'destroy'})),
    path('create/', CreateGroup.as_view())
]

DMUrlPatterns = [
    path('', DMViewSets.as_view({'get': 'list'})),
    path('', include(MessageUrlPatterns)),
    path('<int:pk>/', DMViewSets.as_view({'get': 'retrieve'})),
    path('create/', CreateDM.as_view())
]

urlpatterns = [
    path('group/', include(GroupUrlPatterns)),
    path('dm/', include(DMUrlPatterns)),
]
