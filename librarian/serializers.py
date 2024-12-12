from rest_framework import serializers
from librarian.models import Book, BorrowRequest


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

class GetBookSerializer(serializers.ModelSerializer):
    borrowed_books = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'total_copies', 'current_copies', 'borrowed_books']

    def get_borrowed_books(self, obj):
        return obj.total_copies - obj.current_copies

class BorrowRequestPermissionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = BorrowRequest
        fields = ["id", "request_date", "start_date", "end_date", "status", "user", "user_name", "book", "book_title"]