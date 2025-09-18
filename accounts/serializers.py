from django.conf import settings
from django.urls import reverse
from rest_framework import serializers
from .models import CustomUser
from django.contrib.sites.shortcuts import get_current_site
from rest_framework_simplejwt.tokens import RefreshToken





class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )
        user = CustomUser.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )
        return user


class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255, write_only=True)
    
    def validate(self, data):
        refresh_token = data.get('refresh_token', None)

        if refresh_token is None:
            raise serializers.ValidationError(
                'A refresh token is required to log out.'
            )
        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh['user_id']
            user = CustomUser.objects.filter(id=user_id).first()
            if user is None:
                raise serializers.ValidationError(
                    'A user with this refresh token was not found.'
                )
        except:
            raise serializers.ValidationError(
                'A user with this refresh token was not found.'
            )
        return user

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = [
            'id',
            'is_active',
            'last_login',
            'date_joined',
            'is_superuser',
            'is_staff',
            'email',
            'phone_number'
            ]
    

class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        old_password = data.get('old_password', None)
        new_password = data.get('new_password', None)

        if old_password is None:
            raise serializers.ValidationError(
                'An old password is required to change password.'
            )
        if new_password is None:
            raise serializers.ValidationError(
                'A new password is required to change password.'
            )
        user = self.context['request'].user
        if user is None or not user.check_password(old_password):
            raise serializers.ValidationError(
                'A user with this old password was not found.'
            )
        user.set_password(new_password)
        user.save()
        return user


class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)

    def validate(self, data):
        email = data.get('email', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to reset password.'
            )
        user = CustomUser.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError(
                'A user with this email was not found.'
            )
        token = user.make_token()
        current_site = get_current_site(request=None)
        activate_url = f"http://{current_site.domain}{reverse('accounts:password_reset_confirm', kwargs={'token': token})}"
        
        # Email content
        subject = 'Reset your Password'
        message = f'Hi {self.first_name},\n\nClick on link to reset your password:\n\n{activate_url}'
        html_message = f"""
        <html>
            <body>
                <h2>Welcome to our platform, {self.first_name}!</h2>
                <p>Reset your password by clicking the button below:</p>
                <p>
                    <a href="{activate_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px;">
                        Reset Your Password
                    </a>
                </p>
                <p>If you didn't ask for this, please ignore this email.</p>
            </body>
        </html>
        """
        user.email_user(
            subject=subject,
            message= message,
            html_message=html_message,
            from_email= settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
        )
        return user


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100, write_only=True)
    new_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        token = data.get('token', None)
        new_password = data.get('new_password', None)

        if token is None:
            raise serializers.ValidationError(
                'A token is required to reset password.'
            )
        if new_password is None:
            raise serializers.ValidationError(
                'A new password is required to reset password.'
            )
        user = CustomUser.objects.filter(activation_token=token).first()
        if user is None:
            raise serializers.ValidationError(
                'A user with this token was not found.'
            )
        user.set_password(new_password)
        user.token = None
        user.save()
        return user


class UserActivateSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100, write_only=True)

    def validate(self, data):
        token = data.get('token', None)

        if token is None:
            raise serializers.ValidationError(
                'A token is required to activate account.'
            )
        user = CustomUser.objects.filter(activation_token=token).first()
        if user is None:
            raise serializers.ValidationError(
                'A user with this token was not found.'
            )
        user.is_active = True
        user.activation_token = None
        user.save()
        return user