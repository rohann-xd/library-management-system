from django.urls import path
from librarian.views import (
    BookListCreateView,
    BorrowRequestPermissionView,
    BorrowHistoryView,
    CronJobView,
)

urlpatterns = [
    path("books/", BookListCreateView.as_view(), name="books"),
    path(
        "pending-request/",
        BorrowRequestPermissionView.as_view(),
        name="get-pending-request",
    ),
    path(
        "borrow-history/",
        BorrowHistoryView.as_view(),
        name="borrow_history",
    ),
    path(
        "borrow-history/<str:user_id>/",
        BorrowHistoryView.as_view(),
        name="borrow_history",
    ),
    path("cronjob/", CronJobView.as_view(), name="cronjob"),
]
