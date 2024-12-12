from django.urls import path
from libraryusers.views import (
    BookListCreateView,
    SendBorrowRequestView,
    BorrowHistoryView,
)

urlpatterns = [
    path("books/", BookListCreateView.as_view(), name="booksuser"),
    path(
        "send-borrow-request/",
        SendBorrowRequestView.as_view(),
        name="send-borrow-request",
    ),
    path(
        "borrow-history/",
        BorrowHistoryView.as_view(),
        name="borrow_history",
    ),
]
