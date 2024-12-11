from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from librarian.models import Book
from librarian.serializers import BookSerializer


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(
            {
                "status": True,
                "message": "Books Fetched Successfull",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, format=None):
        if request.user.is_admin == False:
            return Response(
                {
                    "status": False,
                    "errors": "Only Admin can add a new book",
                    "data": "",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Books Added Successfull",
                    "data": {"book-id": book.id},
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )
