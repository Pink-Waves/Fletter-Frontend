from django.contrib.auth import authenticate

from rest_framework import serializers

from django.core.mail import EmailMultiAlternatives
from accounts.models import ExtendedUser

from knox.models import AuthToken

ExtendedUser._meta.get_field('email')._unique = True

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ('id', 'nickname', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ('id', 'nickname', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = ExtendedUser.objects.create_user(
            self.validated_data['username'],
            nickname = self.validated_data['nickname'],
            email = self.validated_data['email'],
            password = self.validated_data['password']
        )

        user.is_active = False
        user.save()

        subject, from_email, to = 'Fletter: Activate Your Account', 'fletter.pw@gmail.com', validated_data['email'],
        text_content = 'Hi %s, \nYour confirmation code is %s. Please activate your Fletter account with the confirmation code.' % (user.nickname, user.confirmation_key)
        html_content = '<p>Hi %s,<br/>Your confirmation code is <strong>%s</strong>.<br/>Please activate your Fletter account with the confirmation code <a href = "http://localhost:3000/emailConfirmation">here</a>.</p>' % (user.nickname, user.confirmation_key)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = ExtendedUser.objects.get(username = data['username'])
        except:
            raise serializers.ValidationError("Sorry! The username you've entered doesn't match any account! \n Please try again or sign up for an account!")
        user = authenticate(**data)
        if user:
            if user.is_active:
                return user
            raise serializers.ValidationError("Your account has not been activated yet! \n Please check your email!")
        else:
            raise serializers.ValidationError("Incorrect Password! \n Please try again or click Forgot Password to reset it.")

class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    key = serializers.CharField()

    def validate(self, data):
        try:
            user = ExtendedUser.objects.get(email = data['email'])
            return user
        except:
            raise serializers.ValidationError("Sorry! We cannot find any account associated with this email!")


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = ExtendedUser.objects.get(email = data['email'])
            return user
        except:
            raise serializers.ValidationError("Sorry! We cannot find any account associated with this email!")
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    key = serializers.CharField()

    def validate(self, data):
        try:
            user = ExtendedUser.objects.get(email = data['email'])
            return user
        except:
            raise serializers.ValidationError("Sorry! We cannot find any account associated with this email!")


class ChangePasswordSerializer(serializers.Serializer):
    def validate(self, data):
        try:
            user = ExtendedUser.objects.get(username = data['username'])
        except:
            raise serializers.ValidationError("Sorry! We cannot find any account associated with this username!")   
        
        if not (user.check_password(data["currentPassword"])):
            raise serializers.ValidationError("Sorry! Incorrect old password!")
        return user