from rest_framework import serializers
from librarian.models import Book


class BookSerializer(serializers.ModelSerializer):
    available_copies = serializers.IntegerField(source="current_copies")

    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "available_copies"]
