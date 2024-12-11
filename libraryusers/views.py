from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from librarian.models import Book
from libraryusers.serializers import BookSerializer


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(
            {
                "status": True,
                "message": "Books Fetched Successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
