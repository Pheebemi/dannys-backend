# Dannys Wellness Clinic - Django Backend

Django REST API backend for Dannys Wellness Clinic management system.

## Setup Instructions

1. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create .env file:**
```bash
cp .env.example .env
# Edit .env and update SECRET_KEY and other settings
```

4. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser:**
```bash
python manage.py createsuperuser
```

6. **Run the development server:**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/auth/login/` - Login with email, password, and role
- `POST /api/auth/logout/` - Logout (requires authentication)
- `GET /api/auth/profile/` - Get current user profile (requires authentication)
- `PUT/PATCH /api/auth/profile/` - Update current user profile (requires authentication)
- `POST /api/auth/refresh/` - Refresh access token

### Example Login Request

```json
POST /api/auth/login/
{
  "email": "doctor@dannyswellness.com",
  "password": "password123",
  "role": "doctor"
}
```

### Example Response

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "doctor1",
    "email": "doctor@dannyswellness.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "doctor",
    "phone_number": "+1234567890",
    "is_active": true
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

## User Roles

- `doctor` - Doctor
- `nurse` - Nurse
- `admin` - Administrator
- `receptionist` - Receptionist
- `pharmacist` - Pharmacist
- `lab_technician` - Lab Technician

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of CORS allowed origins

