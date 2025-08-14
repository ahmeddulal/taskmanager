# Django Task Manager API

A robust and secure **Task Manager API** built with **Django** and **Django REST Framework**. This API allows users to register, login, manage tasks, and ensures all responses follow a **consistent success/error response structure**. JWT authentication is used for secure access and refresh token handling.

## Features

- **User Authentication**
  - Register new users
  - Login to receive JWT access & refresh tokens
  - Refresh access token
  - Logout by blacklisting refresh tokens

- **Task Management**
  - Create, read, update, delete tasks
  - Each task belongs to the authenticated user
  - Only owners or admins can modify tasks

- **Standardized API Responses**
  - All responses follow a common structure:
    ```json
    {
      "status": "success|error",
      "message": "Descriptive message",
      "data": {}
    }
    ```

- **Testing**
  - Comprehensive test coverage for all authentication and task endpoints

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/ahmeddulal/taskmanager.git
cd django-taskmanager
python3 -m venv venv
source venv/bin/activate       # Linux / Mac
venv\Scripts\activate          # Windows
python manage.py runserver

## Running Test Cases
python manage.py test tasks.tests.test_tasks_api

