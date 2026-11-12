
# Shrinsta – Social Media Website

Shrinsta is a social media website I developed using Python and Django. The idea was to build a platform where users can create posts, share photos and videos, follow other users and communicate with each other.

I built this project to improve my practical knowledge of web development and understand how a social media application works.

## Features

- User registration and login
- Create, edit and delete posts
- Upload photos and multiple images
- Like and comment on posts
- Follow and unfollow users
- User profiles with profile pictures and bio
- Share stories with automatic progression
- Upload and watch reels
- Explore posts from other users
- Save posts for later
- Direct messaging between users
- Notifications for likes, comments and follows

## Technologies Used

- Python
- Django
- HTML
- CSS
- JavaScript
- SQLite
- Git and GitHub

## How to Run the Project

Follow these steps to run Shrinsta on your computer.

### 1. Clone the repository

```bash
git clone https://github.com/shrishailsc/Shrinsta.git
```

### 2. Open the project folder

```bash
cd Shrinsta
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install the required packages

```bash
pip install django pillow python-dotenv
```

### 6. Create a .env file

Create a file named `.env` in the same folder as `manage.py`.

Add your own Django secret key:

```text
SECRET_KEY=your-secret-key
```

Keep this file private. Do not upload it to GitHub.

### 7. Run database migrations

```bash
python manage.py migrate
```

### 8. Start the server

```bash
python manage.py runserver
```

Now open this address in your browser:

http://127.0.0.1:8000/

## Project Structure

```text
Shrinsta/
│
├── config/
├── social/
├── manage.py
├── .gitignore
└── README.md
```

## What I Learned

While developing Shrinsta, I got practical experience with Django, database models, user authentication, file uploads, templates, and connecting frontend pages with backend functionality.

I also learned how to use Git and GitHub to manage and share my project.

## Future Improvements

I would like to improve the mobile experience, add more security features and work on real-time messaging in future updates.

## Developer

**Shrishail S C**

GitHub: [shrishailsc](https://github.com/shrishailsc)

Project: [Shrinsta](https://github.com/shrishailsc/Shrinsta)
