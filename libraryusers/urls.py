from django.urls import path
from libraryusers.views import BookListCreateView

urlpatterns = [
    path("books/", BookListCreateView.as_view(), name="booksuser"),
]
