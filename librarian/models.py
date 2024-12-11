from django.db import models
from authentication.models import User


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.IntegerField(default=1)
    current_copies = models.IntegerField(default=1)

    def __str__(self):
        return self.title


class BorrowRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Denied", "Denied"),
        ],
        default="Pending",
    )

    def __str__(self):
        return str(self.user)


class BorrowHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField()
