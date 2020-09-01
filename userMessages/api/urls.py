from django.urls import path, include

from .views import MessageAPIView, InboxAPIView, DraftsAPIView, SendingAPIView, FavoriteAPIView, DeleteAPIView, RestoreAPIView, EditMessageAPIView

urlpatterns = [
    path('message', MessageAPIView.as_view()),
    path('inbox/<str:recipient>/', InboxAPIView.as_view()),
    path('drafts/<str:sender>/', DraftsAPIView.as_view()),
    path('sending/<str:sender>/', SendingAPIView.as_view()),
    path('favorite/<str:recipient>/', FavoriteAPIView.as_view()),
    path('favorite', FavoriteAPIView.as_view()),
    path('delete/<str:recipient>/', DeleteAPIView.as_view()),
    path('delete', DeleteAPIView.as_view()),
    path('restore', RestoreAPIView.as_view()),
    path('edit', EditMessageAPIView.as_view()),
]
