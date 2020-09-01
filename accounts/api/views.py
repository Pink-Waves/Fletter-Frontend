from rest_framework import generics, permissions
from rest_framework.response import Response

from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from django.core.mail import send_mail

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ConfirmEmailSerializer, ForgotPasswordSerializer,ResetPasswordSerializer,ChangePasswordSerializer
from accounts.models import ExtendedUser

class UserAPIView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        })

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        userData = serializer.data
        userData['username'] = user.username
        userData['address'] = user.number + ' ' + user.address + ', ' + user.state
        userData['date_joined'] = user.date_joined
        userData['bird_color'] = user.bird_color
        return Response({
            "user": userData,
            "token": AuthToken.objects.create(user)[1]
        })

class ConfirmEmailAPIView(generics.GenericAPIView):
    serializer_class = ConfirmEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        try:
            user.confirm_email(request.data['key'])
            if user.is_confirmed == True:
                user.is_active = True
                user.save()
                return Response({
                    "email confirmed"
                })
        except:
            if user.is_active == True:
                return Response({
                    "login": "This account is already activated. \nPlease login to continue."
                })
            else:
                return Response({
                    "non_field_errors": "You have entered the wrong code. \nPlease refer back to our email with your unique code."
                })


class CustomizeBirdAPIView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        user = request.user
        user.bird_color = request.data['color']
        user.save()
        return Response({
            "user": user.username,
            "color": user.bird_color
        })


class CustomizeAddressGeneratorAPIView(generics.GenericAPIView):
    queryset = ''
    def post(self, request, *args, **kwargs):
        user = request.user
        user.address = request.data['streetname1'] + ' ' + request.data['streetname2'] + ' ' + request.data['streetsuffix'] 
        user.state = request.data['stateadd']
        self.queryset = ExtendedUser.objects.filter(address = user.address, state = user.state).order_by('-number')
        num = 1
        if len(self.queryset) > 0:
            num = int(self.queryset[0].number) + 1
        user.number = str(num).zfill(4)
        user.save()
        return Response({
            "user": user.username,
            "address": user.number + ' ' + user.address + ', ' + user.state,
        })


class ForgotPasswordAPIView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        print('forgot pswd')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        send_mail(
            'Fletter: Resetting Your Password',
            'Hi %s, your confirmation code is %s. Please reset your Fletter password with the confirmation code.' % (user.nickname, user.confirmation_key),
            'noreply@fletter.com',
            [request.data['email']],
            fail_silently=False,
        )
        return Response({
            "email sent"
        })


class ResetPasswordAPIView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if request.data['key'] == user.confirmation_key:
            user.set_password(request.data['password'])
            user.save()
            return Response({
                "password confirmed"
            })
        else:
            return Response({
                "non_field_errors": "You have entered the wrong code. \nPlease refer back to our email with your unique code."
            })


class ChangePasswordAPIView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer 

    def post(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        user = serializer.validate(data=request.data)
        print(user)
        user.set_password(request.data["newPassword"])
        user.save() 
        return Response({
            "message": "Password updated successfully.",
            "token": AuthToken.objects.create(user)[1]
        })

