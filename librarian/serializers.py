from rest_framework import serializers
from librarian.models import Book


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