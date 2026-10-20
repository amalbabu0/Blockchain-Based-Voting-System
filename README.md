
Blockchain-Based Voting System
===============================

A secure and transparent voting system built using blockchain technology to ensure the integrity, security, and immutability of votes.

Setup Instructions
------------------
   Create a virtual environment.
   Activate the virtual environment.

Django & Requirement
-------------------
        pip install Django
        pip install requirement.txt 

Database Migrations
-------------------
    python manage.py makemigrations
    python manage.py migrate

Create a Superuser
------------------
Create an admin account to access the Django Admin Panel:

    python manage.py createsuperuser

Run the Development Server
---------------------------
    python manage.py runserver

The server will start at http://127.0.0.1:8000/.

Features
--------
- Blockchain-backed voting ledger
- Voter registration and authentication
- Real-time vote tallying
- Admin dashboard for managing elections
- Secure and immutable voting transactions
