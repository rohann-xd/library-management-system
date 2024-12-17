from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from authentication.models import User
from librarian.models import Book, BorrowRequest, BorrowHistory
from librarian.serializers import (
    BookSerializer,
    GetBookSerializer,
    GetBorrowRequestSerializer,
    BorrowRequestPermissionSerializer,
    BorrowHistorySerializer,
)
from django.utils import timezone


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # To get list of all the books available in library
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

    # post method to add new books
    def post(self, request, format=None):
        # Only admin can add new books
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
            # Save new book in the database and returns obj to book variable
            book = serializer.save()
            # At the time of initiallizing new books, total number and available books will be same
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

    # Get request to see all the borrow request for the books
    def get(self, request, format=None):
        # Only admin can access this API
        if request.user.is_admin == False:
            return Response(
                {
                    "status": False,
                    "errors": "Only Admin can get list of pending request.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Returning all the pending request
        requests = BorrowRequest.objects.filter(status="Pending")
        # If no pending request is available
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

    # Post request, to approve or deny the borrow request
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
            # Checking if the entered borrow request exist or not
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
            # user and book objects are already stored in Borrow request
            user = borrow_obj.user
            book = borrow_obj.book

            # If the request is already approved, return error message.
            if borrow_obj.status == "Approved":
                return Response(
                    {
                        "status": False,
                        "errors": "This request was already approved. Don't send request again",
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # If the borrow request is already denied by the admin previosly.
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
            # Checking if the last approve request is expired / user has returned the borrowed book on end date
            # if the last borrowed book is not returned, return error
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
            # Before approving request, if there are available copies of that book in library
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

            # If the permission is explicitly denied by admin
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

            # While approving the request,if the start date is already gone
            # Or the end date is gone, return permission deny
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

            # If everything is good, approve permission
            borrow_obj.status = "Approved"
            borrow_obj.save()
            # On approval, give one copy to user
            book.current_copies -= 1
            book.save()

            borrow_history_data = {
                "user": user,
                "book": book,
                "borrow_date": borrow_obj.start_date,
                "return_date": borrow_obj.end_date,
            }

            # On approval, log the borrow history of the user
            BorrowHistory.objects.create(**borrow_history_data)

            return Response(
                {
                    "status": True,
                    "message": f"Borrow request decision : {serializer.data.get('status')}",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"status": False, "errors": serializer.errors, "data": ""},
            status=status.HTTP_400_BAD_REQUEST,
        )


class BorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None, format=None):
        # Only admin can view every user history
        if not request.user.is_admin:
            return Response(
                {
                    "status": False,
                    "errors": "Only Admin can view borrow histories.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # If no user id is passed in the query params
        if user_id is None:
            return Response(
                {
                    "status": False,
                    "errors": "User ID is required.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Checking if the entered input id in interger/number
            user_id = int(user_id)
        except ValueError:
            return Response(
                {
                    "status": False,
                    "errors": "User ID must be an integer.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # If no user exist of that id, return error
        if not User.objects.filter(id=user_id).exists():
            return Response(
                {
                    "status": False,
                    "errors": "No User found with this ID.",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        user = User.objects.get(id=user_id)
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


class CronJobView(APIView):
    """
    CronJob view will run eveyday at a specific time.
    To remove or delete expired information from database.
    So the user can request a new borrow request.
    """

    def get(self, request, format=None):
        # All the request which are still pending and request start date is gone
        pending_start_date_passed = BorrowRequest.objects.filter(
            status="Pending", start_date__lt=timezone.now().date()
        )
        pending_start_date_passed_count = pending_start_date_passed.count()
        pending_start_date_passed.delete()

        # All the request which are pending and request end date is gone
        pending_end_date_passed = BorrowRequest.objects.filter(
            status="Pending", end_date__lt=timezone.now().date()
        )
        pending_end_date_passed_count = pending_end_date_passed.count()
        pending_end_date_passed.delete()

        # All the request which are denied by the admin
        denied_requests = BorrowRequest.objects.filter(status="Denied")
        denied_requests_count = denied_requests.count()
        denied_requests.delete()

        # All the request which were approved and the end date is gone
        approved_end_date_passed = BorrowRequest.objects.filter(
            status="Approved", end_date__lt=timezone.now().date()
        )
        approved_end_date_passed_count = approved_end_date_passed.count()
        # On the end date, return the borrowed book to the library
        for request in approved_end_date_passed:
            request.book.current_copies += 1
            request.book.save()
            request.delete()

        return Response(
            {
                "status": True,
                "message": "Cronjob executed successfully.",
                "data": {
                    "deleted_pending_start_date_passed": pending_start_date_passed_count,
                    "deleted_pending_end_date_passed": pending_end_date_passed_count,
                    "deleted_denied_requests": denied_requests_count,
                    "deleted_approved_end_date_passed": approved_end_date_passed_count,
                },
            },
            status=status.HTTP_200_OK,
        )
