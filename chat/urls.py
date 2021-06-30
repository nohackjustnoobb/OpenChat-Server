from django.urls import path
from .views import GroupViewSets, CreateGroup, GroupMembersViewSets, GroupAdminsViewSets, LeaveGroup

urlpatterns = [
    path('', GroupViewSets.as_view({'get': 'list'})),
    path('<int:pk>/', GroupViewSets.as_view({'get': 'retrieve', 'delete': 'destroy'})),
    path('<int:pk>/members/', GroupMembersViewSets.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/members/<int:userPK>/', GroupMembersViewSets.as_view({'delete': 'destroy'})),
    path('<int:pk>/members/leave/', LeaveGroup.as_view()),
    path('<int:pk>/admins/', GroupAdminsViewSets.as_view({'get': 'list', 'post': 'create'})),
    path('create/', CreateGroup.as_view())
]
