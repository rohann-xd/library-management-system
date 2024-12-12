from rest_framework import serializers
from librarian.models import Book, BorrowRequest, BorrowHistory
from django.utils import timezone


class BookSerializer(serializers.ModelSerializer):
    available_copies = serializers.IntegerField(source="current_copies")

    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "available_copies"]


class SendBorrowRequestSerializer(serializers.ModelSerializer):
    book_isbn = serializers.CharField(max_length=13, required=True)

    class Meta:
        model = BorrowRequest
        fields = ["book_isbn", "start_date", "end_date"]

    def validate_start_date(self, value):
        request_date = timezone.now().date()
        if value < request_date:
            raise serializers.ValidationError("The start date cannot be in the past.")
        return value


class BorrowHistorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_name = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = BorrowHistory
        fields = ["id", "user_name", "book_title", "borrow_date", "return_date"]
