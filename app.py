from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
import dicttoxml
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'edrian',
    'database': 'another_heroes',
    'port': 3306
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def format_response(data, status_code=200):
    accept_header = request.headers.get('Accept', 'application/json')
    
    if 'application/xml' in accept_header:
        xml_data = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
        response = make_response(xml_data, status_code)
        response.headers['Content-Type'] = 'application/xml'
        return response
    else:
        return jsonify(data), status_code

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return format_response({'error': 'Token is missing!'}, 401)
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return format_response({'error': 'Token has expired!'}, 401)
        except jwt.InvalidTokenError:
            return format_response({'error': 'Token is invalid!'}, 401)
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return format_response({'error': 'Missing username or password'}, 400)
    
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (data['username'], data['password']))
        connection.commit()
        cursor.close()
        connection.close()
        
        return format_response({
            'message': 'User registered successfully',
            'username': data['username']
        }, 201)
    except mysql.connector.IntegrityError:
        return format_response({'error': 'Username already exists'}, 400)
    except Error as e:
        return format_response({'error': str(e)}, 400)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return format_response({'error': 'Missing username or password'}, 400)
    
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (data['username'], data['password']))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not user:
            return format_response({'error': 'Invalid username or password'}, 401)
        
        token = jwt.encode({
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return format_response({
            'message': 'Login successful',
            'token': token,
            'username': user['username']
        })
    except Error as e:
        return format_response({'error': str(e)}, 500)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/web/heroes')
def web_heroes():
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    
    search_name = request.args.get('search_name', '').strip()
    search_role = request.args.get('search_role', '').strip()
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM heroes WHERE 1=1"
        params = []
        
        if search_name:
            query += " AND hero_name LIKE %s"
            params.append(f"%{search_name}%")
        
        if search_role:
            query += " AND role = %s"
            params.append(search_role)
        
        query += " ORDER BY hero_id"
        
        cursor.execute(query, params)
        heroes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        connection2 = get_db_connection()
        cursor2 = connection2.cursor()
        cursor2.execute("SELECT DISTINCT role FROM heroes ORDER BY role")
        roles = [row[0] for row in cursor2.fetchall()]
        cursor2.close()
        connection2.close()
        
        return render_template('heroes.html', heroes=heroes, roles=roles, 
                             search_name=search_name, search_role=search_role)
    except Error as e:
        return f"Error: {str(e)}", 500

@app.route('/web/heroes/create', methods=['GET', 'POST'])
def web_create_hero():
    if request.method == 'POST':
        hero_id = request.form.get('hero_id')
        hero_name = request.form.get('hero_name')
        role = request.form.get('role')
        
        connection = get_db_connection()
        if not connection:
            return "Database connection failed", 500
        
        try:
            cursor = connection.cursor()
            query = "INSERT INTO heroes (hero_id, hero_name, role) VALUES (%s, %s, %s)"
            cursor.execute(query, (hero_id, hero_name, role))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('web_heroes'))
        except Error as e:
            return f"Error: {str(e)}", 400
    
    return render_template('create.html')

@app.route('/web/heroes/update/<int:hero_id>', methods=['GET', 'POST'])
def web_update_hero(hero_id):
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    
    if request.method == 'POST':
        hero_name = request.form.get('hero_name')
        role = request.form.get('role')
        
        try:
            cursor = connection.cursor()
            query = "UPDATE heroes SET hero_name = %s, role = %s WHERE hero_id = %s"
            cursor.execute(query, (hero_name, role, hero_id))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('web_heroes'))
        except Error as e:
            return f"Error: {str(e)}", 400
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM heroes WHERE hero_id = %s", (hero_id,))
        hero = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not hero:
            return "Hero not found", 404
        
        return render_template('update.html', hero=hero)
    except Error as e:
        return f"Error: {str(e)}", 500

@app.route('/web/heroes/delete/<int:hero_id>', methods=['POST'])
def web_delete_hero(hero_id):
    connection = get_db_connection()
    if not connection:
        return "Database connection failed", 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM heroes WHERE hero_id = %s", (hero_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('web_heroes'))
    except Error as e:
        return f"Error: {str(e)}", 500

@app.route('/api')
def api_home():
    return format_response({
        'message': 'Heroes REST API with JWT Authentication',
        'version': '2.0',
        'authentication': {
            'POST /api/register': 'Register new user',
            'POST /api/login': 'Login and get JWT token'
        },
        'endpoints': {
            'GET /api/heroes': 'Get all heroes (supports search with ?name= and ?role=)',
            'GET /api/heroes/<id>': 'Get hero by ID',
            'POST /api/heroes': 'Create new hero (JWT required)',
            'PUT /api/heroes/<id>': 'Update hero (JWT required)',
            'DELETE /api/heroes/<id>': 'Delete hero (JWT required)'
        }
    })

@app.route('/api/heroes/search', methods=['GET'])
def search_heroes():
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    search_name = request.args.get('name', '').strip()
    search_role = request.args.get('role', '').strip()
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM heroes WHERE 1=1"
        params = []
        
        if search_name:
            query += " AND hero_name LIKE %s"
            params.append(f"%{search_name}%")
        
        if search_role:
            query += " AND role = %s"
            params.append(search_role)
        
        query += " ORDER BY hero_id"
        
        cursor.execute(query, params)
        heroes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return format_response({
            'heroes': heroes, 
            'count': len(heroes),
            'search_criteria': {
                'name': search_name if search_name else None,
                'role': search_role if search_role else None
            }
        })
    except Error as e:
        return format_response({'error': str(e)}, 500)

@app.route('/api/heroes', methods=['POST'])
@token_required
def create_hero(current_user):
    data = request.get_json()
    
    if not data or not all(k in data for k in ('hero_id', 'hero_name', 'role')):
        return format_response({'error': 'Missing required fields: hero_id, hero_name, role'}, 400)
    
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor()
        query = "INSERT INTO heroes (hero_id, hero_name, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (data['hero_id'], data['hero_name'], data['role']))
        connection.commit()
        cursor.close()
        connection.close()
        
        return format_response({
            'message': 'Hero created successfully',
            'hero': data,
            'created_by': current_user
        }, 201)
    except Error as e:
        return format_response({'error': str(e)}, 400)

@app.route('/api/heroes', methods=['GET'])
def get_all_heroes():
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM heroes ORDER BY hero_id")
        heroes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return format_response({'heroes': heroes, 'count': len(heroes)})
    except Error as e:
        return format_response({'error': str(e)}, 500)

@app.route('/api/heroes/<int:hero_id>', methods=['GET'])
def get_hero(hero_id):
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM heroes WHERE hero_id = %s", (hero_id,))
        hero = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if hero:
            return format_response({'hero': hero})
        else:
            return format_response({'error': 'Hero not found'}, 404)
    except Error as e:
        return format_response({'error': str(e)}, 500)

@app.route('/api/heroes/<int:hero_id>', methods=['PUT'])
@token_required
def update_hero(current_user, hero_id):
    data = request.get_json()
    
    if not data:
        return format_response({'error': 'No data provided'}, 400)
    
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor()
        
        update_fields = []
        values = []
        
        if 'hero_name' in data:
            update_fields.append("hero_name = %s")
            values.append(data['hero_name'])
        if 'role' in data:
            update_fields.append("role = %s")
            values.append(data['role'])
        
        if not update_fields:
            return format_response({'error': 'No valid fields to update'}, 400)
        
        values.append(hero_id)
        query = f"UPDATE heroes SET {', '.join(update_fields)} WHERE hero_id = %s"
        
        cursor.execute(query, values)
        connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return format_response({'error': 'Hero not found'}, 404)
        
        cursor.close()
        connection.close()
        
        return format_response({
            'message': 'Hero updated successfully',
            'hero_id': hero_id,
            'updated_by': current_user
        })
    except Error as e:
        return format_response({'error': str(e)}, 400)

@app.route('/api/heroes/<int:hero_id>', methods=['DELETE'])
@token_required
def delete_hero(current_user, hero_id):
    connection = get_db_connection()
    if not connection:
        return format_response({'error': 'Database connection failed'}, 500)
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM heroes WHERE hero_id = %s", (hero_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return format_response({'error': 'Hero not found'}, 404)
        
        cursor.close()
        connection.close()
        
        return format_response({
            'message': 'Hero deleted successfully',
            'hero_id': hero_id,
            'deleted_by': current_user
        })
    except Error as e:
        return format_response({'error': str(e)}, 500)

@app.errorhandler(404)
def not_found(error):
    return format_response({'error': 'Endpoint not found'}, 404)

@app.errorhandler(500)
def internal_error(error):
    return format_response({'error': 'Internal server error'}, 500)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
