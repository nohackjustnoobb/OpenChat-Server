from django.urls import path
from .views import GroupViewSets, CreateGroup

urlpatterns = [
    path('', GroupViewSets.as_view({'get': 'list'})),
    path('<int:pk>/', GroupViewSets.as_view({'get': 'retrieve'})),
    path('create/', CreateGroup.as_view())
]
