from rest_framework import serializers
from librarian.models import Book, BorrowRequest
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
