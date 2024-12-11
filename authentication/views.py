from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from authentication.serializers import (
    UserRegisterationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if request.user.is_admin == False:
            return Response(
                {
                    "status": False,
                    "errors": "Only Admin can register a new user",
                    "data": "",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {
                    "status": True,
                    "message": "User Registration Successfull",
                    "data": token,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response(
                    {
                        "status": True,
                        "message": "User Login Successfull",
                        "data": token,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": False,
                        "errors": "Email or Password is not valid.",
                        "data": "",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(
            {
                "status": True,
                "message": "Profile Fetched Successfull",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid():
            return Response(
                {
                    "status": True,
                    "message": "Profile Changed Successfull",
                    "data": "",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )
