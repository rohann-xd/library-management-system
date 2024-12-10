from django.urls import path
from authentication.views import UserRegistrationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register")
]
