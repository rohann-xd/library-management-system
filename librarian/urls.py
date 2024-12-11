from django.urls import path
from librarian.views import BookListCreateView

urlpatterns = [
    path("books/", BookListCreateView.as_view(), name="books"),
]
