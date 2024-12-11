from django.contrib import admin
from librarian.models import Book, BorrowRequest


@admin.register(Book)
class LibraryBooks(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "isbn",
        "total_copies",
        "current_copies"
    )


@admin.register(BorrowRequest)
class BorrowBooks(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "book",
        "request_date",
        "start_date",
        "end_date",
        "status"
    )