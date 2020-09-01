from django.urls import path, include

from .views import RelationshipAPIView, FriendRequestAPIView, AcceptAPIView, DeleteAPIView, ContactAPIView

urlpatterns = [
    path('relationship', RelationshipAPIView.as_view()),
    path('friendRequest/<str:addressee>/', FriendRequestAPIView.as_view()),
    path('acceptRequest/', AcceptAPIView.as_view()),
    path('deleteRequest/', DeleteAPIView.as_view()),
    path('contact/<str:addressee>/', ContactAPIView.as_view()),
]

