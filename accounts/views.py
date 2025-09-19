from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from accounts.models import CustomUser
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserPasswordChangeSerializer,
    UserPasswordResetSerializer,
    UserPasswordResetConfirmSerializer,
    UserActivateSerializer,
    UserLogoutSerializer
    )



class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(email=serializer.data['email'])
            user.send_mail(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        serializer = UserActivateSerializer(data={'token': token})
        serializer.is_valid(raise_exception=True)
        return Response(data={'message': 'Account activated successfully'}, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = user.get_token()
            return Response(tokens, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserLogoutSerializer(data=request.data)
            if serializer.is_valid():
                refresh_token = serializer.validated_data['refresh_token']
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            raise InvalidToken('Token is invalid or expired')


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserPasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(data={'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserPasswordResetSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(data={'message': 'Password reset email sent'}, status=status.HTTP_200_OK)


class UserPasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        try:
            CustomUser.objects.get(token=token)
        except CustomUser.DoesNotExist:
            return Response(data={'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        new_password = request.data.get('new_password')
        if new_password is None:
            return Response(data={'new_password': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserPasswordResetConfirmSerializer(data={'new_password':new_password, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response(data={'message': 'Password reset successfully'}, status=status.HTTP_200_OK)