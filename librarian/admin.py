from django.contrib import admin
from librarian.models import Book, BorrowRequest, BorrowHistory


@admin.register(Book)
class LibraryBooks(admin.ModelAdmin):
    list_display = ("id", "title", "author", "isbn", "total_copies", "current_copies")


@admin.register(BorrowRequest)
class BorrowBooks(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "book",
        "request_date",
        "start_date",
        "end_date",
        "status",
    )


@admin.register(BorrowHistory)
class BorrowHistory(admin.ModelAdmin):
    list_display = ("id", "user", "book", "borrow_date", "return_date")
