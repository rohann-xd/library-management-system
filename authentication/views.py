from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from authentication.models import User
from django.contrib.auth import authenticate
from authentication.serializers import UserRegisterationSerializer, UserLoginSerializer
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
    def post(self, request, format=None):
        serializer = UserRegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {
                    "status": True,
                    "msg": "User Registration Successfull",
                    "data": token,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "msg": serializer.errors, "data": ""},
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
                        "msg": "User Login Successfull",
                        "data": token,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": False,
                        "msg": "Email or Password is not valid.",
                        "data": "",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(
            {"status": False, "msg": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )
