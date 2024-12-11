from django.contrib import admin
from librarian.models import Book


@admin.register(Book)
class LibraryBooks(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "isbn",
        "copies",
    )