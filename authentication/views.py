from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from authentication.models import User
from authentication.serializers import UserRegisterationSerializer
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
            return Response(
                {
                    "status": True,
                    "msg": "User Registration Successfull",
                    "data": str(user),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "msg": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )
