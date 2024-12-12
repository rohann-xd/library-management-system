from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from librarian.models import Book, BorrowRequest, BorrowHistory
from librarian.serializers import (
    BookSerializer,
    GetBookSerializer,
    GetBorrowRequestSerializer,
    BorrowRequestPermissionSerializer,
)
from django.utils import timezone


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
        serializer = GetBorrowRequestSerializer(requests, many=True)
        return Response(
            {
                "status": True,
                "message": "Borrow request fetched Successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, format=None):
        if request.user.is_admin == False:
            return Response(
                {
                    "status": False,
                    "errors": "Only Admin can update borrow request.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BorrowRequestPermissionSerializer(data=request.data)
        if serializer.is_valid():
            if not BorrowRequest.objects.filter(
                id=serializer.data.get("request_id")
            ).exists():
                return Response(
                    {
                        "status": False,
                        "errors": "No borrow request exist of this id.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            borrow_obj = BorrowRequest.objects.get(id=serializer.data.get("request_id"))
            user = borrow_obj.user
            book = borrow_obj.book

            if borrow_obj.status == "Approved":
                return Response(
                    {
                        "status": False,
                        "errors": "This request was already approved. Don't send request again",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if borrow_obj.status == "Denied":
                return Response(
                    {
                        "status": False,
                        "errors": "This request is already denied by the admin. The user can send new reqeust after 24 hours.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            approved_request = BorrowRequest.objects.filter(
                user=user, status="Approved"
            ).last()
            if approved_request and timezone.now().date() <= approved_request.end_date:
                borrow_obj.status = "Denied"
                borrow_obj.save()
                return Response(
                    {
                        "status": False,
                        "errors": "User can borrow only one book at a time. Permission Denied",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if book.current_copies < 1:
                borrow_obj.status = "Denied"
                borrow_obj.save()
                return Response(
                    {
                        "status": False,
                        "errors": "Currently this book is not available in the library , Permission Denied.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if serializer.data.get("status") == "Denied":
                borrow_obj.status = "Denied"
                borrow_obj.save()
                return Response(
                    {
                        "status": False,
                        "errors": "Permission Denied by Admin. Please try again.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (timezone.now().date() >= borrow_obj.end_date) or (
                timezone.now().date() > borrow_obj.start_date
            ):
                borrow_obj.status = "Denied"
                borrow_obj.save()
                return Response(
                    {
                        "status": False,
                        "errors": "The requested date is already gone. Permission denied.",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            borrow_obj.status = "Approved"
            borrow_obj.save()

            book.current_copies -= 1
            book.save()

            borrow_history_data = {
                "user": user,
                "book": book,
                "borrow_date": borrow_obj.start_date,
                "return_date": borrow_obj.end_date,
            }

            BorrowHistory.objects.create(**borrow_history_data)

            return Response(
                {
                    "status": True,
                    "message": f"Borrow request decision : {serializer.data.get("status")}",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )
