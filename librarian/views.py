from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from librarian.models import Book, BorrowRequest
from librarian.serializers import (
    BookSerializer,
    GetBookSerializer,
    BorrowRequestPermissionSerializer,
)


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        books = Book.objects.all()
        serializer = GetBookSerializer(books, many=True)
        return Response(
            {
                "status": True,
                "message": "Books Fetched Successfully",
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
            book.current_copies = book.total_copies
            book.save()
            return Response(
                {
                    "status": True,
                    "message": "Books Added Successfull",
                    "data": {
                        "book-id": book.id,
                        "book-total-copies": book.total_copies,
                        "book-current-copies": book.current_copies,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BorrowRequestPermissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if request.user.is_admin == False:
            return Response(
                {
                    "status": False,
                    "errors": "Only Admin can get list of pending request.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        requests = BorrowRequest.objects.filter(status="Pending")
        if not requests.exists():
            return Response(
                {
                    "status": True,
                    "message": "No pending borrow requests.",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )
        serializer = BorrowRequestPermissionSerializer(requests, many=True)
        return Response(
            {
                "status": True,
                "message": "Borrow request fetched Successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
