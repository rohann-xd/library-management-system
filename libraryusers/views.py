import csv
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from librarian.models import Book, BorrowRequest, BorrowHistory
from libraryusers.serializers import (
    BookSerializer,
    SendBorrowRequestSerializer,
    BorrowHistorySerializer,
)
from django.utils import timezone


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # Get list of all the book available in the library
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


class SendBorrowRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = SendBorrowRequestSerializer(data=request.data)
        # Check all the required inputs are entered or not
        if serializer.is_valid():
            book_isbn = serializer.validated_data.get("book_isbn")
            # If enetered book isbn is not available or not exist
            if not Book.objects.filter(isbn=book_isbn).exists():
                return Response(
                    {
                        "status": False,
                        "errors": "No book available with this isbn.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            book = Book.objects.get(isbn=book_isbn)
            # If no copies of the books are left, do not allow to request
            if book.current_copies < 1:
                return Response(
                    {
                        "status": False,
                        "errors": "Currently this book is not available in the library, please try again later.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = request.user
            approved_request = BorrowRequest.objects.filter(
                user=user, status="Approved"
            ).last()
            # If the user has already one book borrowed, user can't borrow two books at the same time
            if approved_request and timezone.now().date() <= approved_request.end_date:
                return Response(
                    {
                        "status": False,
                        "errors": "User can borrow only one book at a time.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # If the borrow request for that book is already denied
            elif BorrowRequest.objects.filter(
                user=user,
                book=book,
                status="Denied",
            ).exists():
                return Response(
                    {
                        "status": False,
                        "errors": "Request denied. You can try again after 24 hours.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # If the borrow request is still in pending state
            elif BorrowRequest.objects.filter(
                user=user, book=book, status="Pending"
            ).exists():
                return Response(
                    {
                        "status": False,
                        "errors": "Request is still pending, please check later.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If everything is correct, send new borrow request
            BorrowRequest.objects.create(
                user=user,
                book=book,
                start_date=serializer.validated_data.get("start_date"),
                end_date=serializer.validated_data.get("end_date"),
            )
            return Response(
                {
                    "status": True,
                    "message": "Borrow request sent successfully.",
                    "data": None,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "errors": serializer.errors, "data": None},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    # Get request to view borrow history of logged in user
    def get(self, request, format=None):
        user = request.user
        # If user want to download borrow history in .csv
        download = request.query_params.get("download", None)

        if download:
            return self.download_csv(user)

        borrow_history = BorrowHistory.objects.filter(user=user)
        serializer = BorrowHistorySerializer(borrow_history, many=True)
        return Response(
            {
                "status": True,
                "message": "Borrow history fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # Function to download borrow history in form of .csv file
    def download_csv(self, user):
        borrow_history = BorrowHistory.objects.filter(user=user)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="borrow_history.csv"'

        writer = csv.writer(response)
        writer.writerow(["Book Title", "Borrow Date", "Return Date"])

        for record in borrow_history:
            writer.writerow([record.book.title, record.borrow_date, record.return_date])

        return response
