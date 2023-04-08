#  Library Service API
This API provides an online management system for book borrowings in a library. With this API, users can browse the available books, borrow books, and return books when they are done reading. 
## Features
- JWT authentication
- Admin panel /admin/
- Documentation /api/doc/swagger/
- Add new books to the inventory
- Remove books from the inventory
- Update book information
- Browse available books
- Borrow books
- Return books
- Filter active book borrowings
- Filter book borrowings by user
- Notifications when borrow/return book (Telegram)
- Manage user information

## Installation
```
git clone https://github.com/ansicat/library-api.git
cd library-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Use `.env_sample` file as a template and create `.env` file with your settings
```
python manage.py migrate --with_test_data
python manage.py runserver
```

Use credentials for login:
  - email: admin@example.com
  - password: asdf7890
