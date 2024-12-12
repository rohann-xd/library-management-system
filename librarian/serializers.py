from rest_framework import serializers
from librarian.models import Book, BorrowRequest, BorrowHistory


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class GetBookSerializer(serializers.ModelSerializer):
    borrowed_books = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "total_copies",
            "current_copies",
            "borrowed_books",
        ]

    def get_borrowed_books(self, obj):
        return obj.total_copies - obj.current_copies


class GetBorrowRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BorrowRequest
        fields = [
            "id",
            "request_date",
            "start_date",
            "end_date",
            "status",
            "user",
            "user_name",
            "book",
            "book_title",
        ]


class BorrowRequestPermissionSerializer(serializers.Serializer):
    STATUS_CHOICES = [("Approved", "Approved"), ("Denied", "Denied")]

    request_id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=True)

    class Meta:
        fields = ["request_id", "status"]


class BorrowHistorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_name = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = BorrowHistory
        fields = ["id", "user_name", "book_title", "borrow_date", "return_date"]
