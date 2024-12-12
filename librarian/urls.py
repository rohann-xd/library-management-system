from django.urls import path
from librarian.views import BookListCreateView, BorrowRequestPermissionView

urlpatterns = [
    path("books/", BookListCreateView.as_view(), name="books"),
    path("pending-request/", BorrowRequestPermissionView.as_view(), name="get-pending-request"),
]
