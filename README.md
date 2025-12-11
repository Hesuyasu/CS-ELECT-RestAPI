# Heroes REST API with JWT Authentication

A full-featured REST API built with Flask for managing Mobile Legends heroes. The API supports JWT authentication, search functionality, and both JSON and XML response formats. It also includes a web interface for easy hero management.

## Features

- **JWT Authentication**: Secure API endpoints with JSON Web Tokens
- **CRUD Operations**: Create, Read, Update, and Delete heroes
- **Search Functionality**: Search heroes by name or role
- **Multiple Response Formats**: Supports both JSON and XML responses
- **Web Interface**: User-friendly web pages for hero management
- **MySQL Database**: Persistent data storage
- **Environment Variables**: Secure configuration management

## Technologies Used

- **Flask**: Python web framework
- **MySQL**: Database management
- **JWT (PyJWT)**: Authentication tokens
- **DictToXML**: XML response formatting
- **Python-Dotenv**: Environment variable management
- **MySQL Connector**: Database connectivity

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Hesuyasu/CS-ELECT-RestAPI.git
cd CS-ELECT-RestAPI
```

### 2. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install flask mysql-connector-python dicttoxml pyjwt python-dotenv
```

### 3. Set Up MySQL Database

Create a database and table in MySQL:

```sql
CREATE DATABASE another_heroes;

USE another_heroes;

CREATE TABLE heroes (
    hero_id INT PRIMARY KEY,
    hero_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL
);

INSERT INTO heroes (hero_id, hero_name, role) VALUES
(1, 'Layla', 'Marksman'),
(2, 'Balmond', 'Fighter'),
(3, 'Miya', 'Marksman'),
(4, 'Tigreal', 'Tank'),
(5, 'Alucard', 'Fighter');
```

### 4. Configure Database Connection

Update the database configuration in `app.py`:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'another_heroes',
    'port': 3306
}
```

### 5. Set Up Environment Variables (Optional)

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
```

### 6. Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Documentation

### Base URL

```
http://localhost:5000
```

### Authentication Endpoints

#### Register a New User

```http
POST /api/register
Content-Type: application/json

{
    "username": "john_doe",
    "password": "password123"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "username": "john_doe"
}
```

#### Login and Get JWT Token

```http
POST /api/login
Content-Type: application/json

{
    "username": "john_doe",
    "password": "password123"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "john_doe"
}
```

### Hero Management Endpoints

#### Get All Heroes

**No authentication required**

```http
GET /api/heroes
```

**Response:**
```json
{
    "heroes": [
        {
            "hero_id": 1,
            "hero_name": "Layla",
            "role": "Marksman"
        },
        {
            "hero_id": 2,
            "hero_name": "Balmond",
            "role": "Fighter"
        }
    ],
    "count": 2
}
```

#### Get Hero by ID

**No authentication required**

```http
GET /api/heroes/1
```

**Response:**
```json
{
    "hero": {
        "hero_id": 1,
        "hero_name": "Layla",
        "role": "Marksman"
    }
}
```

#### Search Heroes

**No authentication required**

```http
GET /api/heroes/search?name=Layla&role=Marksman
```

**Query Parameters:**
- `name` (optional): Search by hero name (partial match)
- `role` (optional): Filter by exact role

**Response:**
```json
{
    "heroes": [
        {
            "hero_id": 1,
            "hero_name": "Layla",
            "role": "Marksman"
        }
    ],
    "count": 1,
    "search_criteria": {
        "name": "Layla",
        "role": "Marksman"
    }
}
```

#### Create a New Hero

**Authentication required** (JWT token)

```http
POST /api/heroes
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
    "hero_id": 21,
    "hero_name": "Fanny",
    "role": "Assassin"
}
```

**Response:**
```json
{
    "message": "Hero created successfully",
    "hero": {
        "hero_id": 21,
        "hero_name": "Fanny",
        "role": "Assassin"
    },
    "created_by": "john_doe"
}
```

#### Update a Hero

**Authentication required** (JWT token)

```http
PUT /api/heroes/21
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
    "hero_name": "Fanny Updated",
    "role": "Assassin"
}
```

**Response:**
```json
{
    "message": "Hero updated successfully",
    "hero_id": 21,
    "updated_by": "john_doe"
}
```

#### Delete a Hero

**Authentication required** (JWT token)

```http
DELETE /api/heroes/21
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
    "message": "Hero deleted successfully",
    "hero_id": 21,
    "deleted_by": "john_doe"
}
```

### XML Response Format

To receive responses in XML format, include the `Accept` header:

```http
GET /api/heroes
Accept: application/xml
```

**Response:**
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<response>
    <heroes>
        <item>
            <hero_id>1</hero_id>
            <hero_name>Layla</hero_name>
            <role>Marksman</role>
        </item>
    </heroes>
    <count>1</count>
</response>
```

## Web Interface

Access the web interface through your browser:

- **Home Page**: `http://localhost:5000/`
- **View All Heroes**: `http://localhost:5000/web/heroes`
- **Create Hero**: `http://localhost:5000/web/heroes/create`
- **Update Hero**: `http://localhost:5000/web/heroes/update/<hero_id>`

The web interface includes:
- Search functionality by name and role
- Create new heroes
- Update existing heroes
- Delete heroes

## Usage Examples

### Using cURL

#### Register and Login

```bash
# Register
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

#### Get All Heroes

```bash
curl http://localhost:5000/api/heroes
```

#### Create a Hero (with JWT)

```bash
curl -X POST http://localhost:5000/api/heroes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"hero_id":30,"hero_name":"Gusion","role":"Assassin"}'
```

#### Search Heroes

```bash
curl "http://localhost:5000/api/heroes/search?name=Layla"
curl "http://localhost:5000/api/heroes/search?role=Marksman"
```

### Using Python Requests

```python
import requests

BASE_URL = 'http://localhost:5000'

# Login
response = requests.post(f'{BASE_URL}/api/login', json={
    'username': 'testuser',
    'password': 'testpass'
})
token = response.json()['token']

# Get all heroes
response = requests.get(f'{BASE_URL}/api/heroes')
heroes = response.json()

# Create a hero
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(f'{BASE_URL}/api/heroes', 
    json={'hero_id': 50, 'hero_name': 'Lancelot', 'role': 'Assassin'},
    headers=headers)

# Search heroes
response = requests.get(f'{BASE_URL}/api/heroes/search?role=Fighter')
```

### Using Postman

1. **Set up environment variables** in Postman:
   - `base_url`: `http://localhost:5000`
   - `token`: (will be set after login)

2. **Login Request**:
   - Method: POST
   - URL: `{{base_url}}/api/login`
   - Body (JSON): `{"username":"testuser","password":"testpass"}`
   - Save the token from response to environment variable

3. **Protected Requests**:
   - Add header: `Authorization: Bearer {{token}}`

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **200**: Success
- **201**: Created
- **400**: Bad Request (invalid data)
- **401**: Unauthorized (missing or invalid token)
- **404**: Not Found
- **500**: Internal Server Error

**Error Response Example:**
```json
{
    "error": "Token is missing!"
}
```

## Project Structure

```
CS-ELECT-RestAPI/
│
├── app.py                 # Main application file
├── test_api.py           # API testing script
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
│
├── templates/           # HTML templates
│   ├── index.html      # Home page
│   ├── heroes.html     # Heroes list with search
│   ├── create.html     # Create hero form
│   └── update.html     # Update hero form
│
└── .env                 # Environment variables (create this)
```

## Security Notes

⚠️ **Important for Production:**

1. **Password Hashing**: The current implementation stores passwords in plain text. Use `bcrypt` or `werkzeug.security` to hash passwords:
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   ```

2. **Secret Key**: Always use a strong, randomly generated secret key in production:
   ```python
   import secrets
   secrets.token_hex(32)
   ```

3. **Environment Variables**: Never commit `.env` files or hardcode sensitive information

4. **HTTPS**: Use HTTPS in production to encrypt data in transit

5. **Token Expiration**: Current token expiration is set to 24 hours. Adjust as needed.

## Testing

Run the test script to verify API functionality:

```bash
python test_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is created for educational purposes as part of CS Elective coursework.

## Author

**Hesuyasu**

## Acknowledgments

- Flask documentation
- Mobile Legends: Bang Bang for hero data inspiration
- CS Elective course instructors

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.