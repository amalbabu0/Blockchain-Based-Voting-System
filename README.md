
Blockchain-Based Voting System
===============================

A secure and transparent voting system built using blockchain technology to ensure the integrity, security, and immutability of votes.

Requirements
------------
- Python 3.10+
- Django 4.x
- pip
- Virtualenv (recommended)

Setup Instructions
------------------

For Windows:

   Open Command Prompt.
   Navigate to your project directory.
   Create a virtual environment:
   
         python -m venv venv
         
   Activate the virtual environment:

      venv\Scripts\activate

For Linux:

   Open Terminal.
   Navigate to your project directory.
   Create a virtual environment:
      
      python3 -m venv venv

   
   Activate the virtual environment:

      source venv/bin/activate
      
   
Install Django:
   
        pip install Django    

Database Migrations
-------------------

5. Make Migrations:

    python manage.py makemigrations

6. Migrate Database:

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

Contribution
------------

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
