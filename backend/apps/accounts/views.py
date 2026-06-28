from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, OTPSendSerializer, OTPVerifySerializer
)
from .permissions import IsSuperAdminOrOwner, IsManagerOrAbove


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPSendView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            user = User.objects.get(phone_number=phone)
            otp = user.generate_otp()
            
            # Print to log
            print(f"====================================\n[OTP DEBUG] OTP for {phone}: {otp}\n====================================")
            
            response_data = {"message": "OTP sent successfully."}
            if settings.DEBUG:
                response_data["otp_debug"] = otp  # Facilitate simple local testing and app debugging
                
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsManagerOrAbove()]
        return [IsSuperAdminOrOwner()]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
