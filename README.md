# Library Management System

A simple and efficient library management system API with Django. This application allows users to view available books, send borrow requests, and track their borrow history. It also includes an admin functionality to manage users and their borrow requests.

---

## Features

### User Features
- View a list of available books in the library
- Send borrow requests for books with a specified start and end date
- Track borrow history, including book titles, borrow dates, and return dates
- Download borrow history in CSV format

### Admin Features
- Admins can view borrow histories of all users
- Admins can delete expired borrow requests
- Admins can manage books, borrow requests, and users

---

## Tech Stack

- **Backend**: Django, Django REST Framework (DRF)
- **Database**: SQLite (default), can be switched to PostgreSQL or MySQL
- **Deployment**: AWS EC2 or any other server

---

## Installation

### Backend

1. Clone the repository:
    ```bash 
    git clone https://github.com/rohann-xd/library-management-system.git
    cd library-management-system
    ```

2. Set up a virtual environment and install dependencies:
    ```
    python -m venv venv
    source venv/bin/activate  # For macOS/Linux
    .venv\Scripts\activate     # For Windows
    pip install -r requirements.txt
    ```

3. Set up your database:
    ```
    python manage.py migrate
    ```

4. Create a superuser to access the admin panel:
    ```
    python manage.py createsuperuser
    ```

5. Run the development server:
    ```
    python manage.py runserver
    ```


### Environment Variables

Create a `.env` file in the root directory for sensitive data (e.g., `SECRET_KEY`, `DEBUG`,  etc.).

Example `.env` file:

```
SECRET_KEY=your_secret_key 
DEBUG=True
```

---

## API Endpoints

### User Endpoints

- **GET /api/libraryusers/books/**: Get the list of all books in the library
- **POST /api/libraryusers/send-borrow-request/**: Send a borrow request for a book with a start and end date
- **GET /api/libraryusers/borrow-history/**: Get the borrow history for the logged-in user
- **GET /api/libraryusers/borrow-history/?download=True**: Download the borrow history as a CSV file

### Admin Endpoints

- **GET /api/librarian/books/**: Get the list of all books in the library
- **POST /api/librarian/books/**: Add a new book in the library
- **GET /api/librarian/pending-request/**: Get all the pending borrow request
- **POST /api/librarian/pending-request/**: Approve or Deny borrow request for the user
- **GET /api/librarian/borrow-history/{user_id}/**: View borrow history of a specific user (Admin only)
- **GET /api/librarian/cronjob/**: Cron job for cleaning up expired borrow requests

---

## License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.


