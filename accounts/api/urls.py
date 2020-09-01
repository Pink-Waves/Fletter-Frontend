from django.urls import path, include

from knox.views import LogoutView

from .views import UserAPIView, RegisterAPIView, LoginAPIView, ConfirmEmailAPIView, CustomizeBirdAPIView, CustomizeAddressGeneratorAPIView, ForgotPasswordAPIView, ResetPasswordAPIView, ChangePasswordAPIView

urlpatterns = [
    path('', include('knox.urls')),
    path('user', UserAPIView.as_view()),
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view(), name='knox_login'),
    path('logout', LogoutView.as_view(), name='knox_logout'),
    path('confirmEmail', ConfirmEmailAPIView.as_view()),
    path('customizeBird', CustomizeBirdAPIView.as_view()),
    path('address', CustomizeAddressGeneratorAPIView.as_view()),
    path('forgotPassword', ForgotPasswordAPIView.as_view()),
    path('resetPassword', ResetPasswordAPIView.as_view()),
    path('changePassword', ChangePasswordAPIView.as_view())
]

