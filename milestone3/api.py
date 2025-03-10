from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from statements import statements
from dummy_data_insertion import *
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Initialize Flask application
app = Flask(__name__)
# Secret key used for JWT token encoding/decoding - should be stored securely in production
app.config['JWT_SECRET_KEY'] = '123'
# Initialize JWT manager for authentication
jwt = JWTManager(app)

# Initialize API with Swagger documentation
api = Api(app, 
          title="SUPERTIFY Music Streaming API", 
          version="1.0", 
          description="The ultimate music streaming experience API - connect, play, and enjoy! This API allows you to manage users, songs, playlists, albums, and more for a complete music streaming platform.")

# SQLite database file path
DATABASE = 'supertify.db'

@app.before_request
def force_json():
    """
    Middleware to ensure POST, PUT, and PATCH requests are processed as JSON.
    
    This ensures API consistency by defaulting to JSON for data-modifying requests
    when no content type is specified.
    """
    if request.method in ['POST', 'PUT', 'PATCH'] and not request.content_type:
        # If no content type is specified, let's assume it's JSON
        request.content_type = 'application/json'

# Set up our database with all the tables we need
def init_db():
    """
    Initialize the database with all required tables and indexes.
    
    This function:
    1. Creates tables from statements.py
    2. Enables foreign key constraints
    3. Creates the Authentication table for user login
    4. Handles any database errors gracefully
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    try:
        # First things first, let's make sure foreign keys work
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Create all our tables from the statements list
        for statement in statements:
            cursor.execute(statement)
            
        # We also need a table for user authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Authentication (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        connection.commit()
        print("Database all set up and ready to go!")
    except sqlite3.Error as e:
        print(f"Oops! Something went wrong with the database: {str(e)}")
    finally:
        connection.close()

def check_db_schema():
    """
    Check the database schema to identify any issues with table structure.
    This is useful for debugging issues with table creation and data insertion.
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    print("\n--------- Database Schema Check ---------")
    
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:")
    for table in tables:
        table_name = table[0]
        print(f"\n-- Table: {table_name} --")
        
        # Get schema for this table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, name, type_name, notnull, default_val, pk = col
            constraints = []
            if pk:
                constraints.append("PRIMARY KEY")
            if notnull:
                constraints.append("NOT NULL")
            if default_val:
                constraints.append(f"DEFAULT {default_val}")
            
            constraints_str = ", ".join(constraints)
            print(f"  {name} ({type_name}) {constraints_str}")
        
        # Check for foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            print("  Foreign Keys:")
            for fk in foreign_keys:
                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                print(f"    {from_col} -> {table}({to_col})")
    
    # Check if there's any data in the tables
    print("\n--------- Data Check ---------")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count} records")
    
    print("\n--------- End of Schema Check ---------\n")
    connection.close()

# Call the schema check function after db initialization
# Note: before_first_request is deprecated in newer Flask, using alternative approach
@app.before_request
def setup_before_request():
    """
    Initializes the database before handling any requests.
    Uses a global variable to ensure initialization happens only once.
    """
    global _initialization_done
    
    if not getattr(app, '_initialization_done', False):
        init_db()
        check_db_schema()  # Check the schema after initialization
        
        # Migrate genre data if needed
        migrate_genre_data()
        
        # Migrate genre structure to new format
        migrate_genre_structure()
        
        # Try to insert dummy data after initialization
        try:
            insert_dummy_data(DATABASE)
        except Exception as e:
            print(f"Notice: Could not insert dummy data: {str(e)}")
            
        app._initialization_done = True

def migrate_genre_data():
    """
    Migrate data from the old Genre table structure to the new many-to-many structure.
    This function should be called after init_db() to ensure data consistency.
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    try:
        # Check if old genre table exists by looking for a song_id column in Genre table
        cursor.execute("PRAGMA table_info(Genre)")
        columns = cursor.fetchall()
        has_old_structure = any(column[1] == 'song_id' for column in columns)
        
        if has_old_structure:
            print("Detected old Genre table structure. Migrating data...")
            
            # Check if SongGenre table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SongGenre'")
            has_songgenre_table = cursor.fetchone() is not None
            
            if not has_songgenre_table:
                print("SongGenre table not found. Migration cannot proceed.")
                return
            
            # Get existing genre data
            cursor.execute("SELECT song_id, genre FROM Genre")
            old_genres = cursor.fetchall()
            
            for song_id, genre_name in old_genres:
                # Create or get genre_id for this genre name
                cursor.execute("SELECT genre_id FROM Genre WHERE genre_name = ?", (genre_name,))
                genre_row = cursor.fetchone()
                
                if genre_row:
                    genre_id = genre_row[0]
                else:
                    # Create new genre
                    genre_id = str(uuid.uuid4())
                    cursor.execute("INSERT INTO Genre (genre_id, genre_name) VALUES (?, ?)", 
                                   (genre_id, genre_name))
                
                # Create song-genre relationship
                try:
                    cursor.execute("INSERT INTO SongGenre (song_id, genre_id) VALUES (?, ?)",
                                   (song_id, genre_id))
                except sqlite3.IntegrityError:
                    # Relationship might already exist - ignore
                    pass
            
            # Rename old Genre table to backup
            cursor.execute("ALTER TABLE Genre RENAME TO Genre_Old")
            
            # Create new Genre table with updated schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Genre (
                    genre_id CHAR(36) PRIMARY KEY,
                    genre_name VARCHAR(50) NOT NULL UNIQUE CHECK (length(genre_name) > 0)
                )
            """)
            
            # Populate new Genre table with unique genres
            cursor.execute("""
                INSERT INTO Genre (genre_id, genre_name)
                SELECT DISTINCT genre_id, genre_name FROM Genre_Old
            """)
            
            connection.commit()
            print("Genre data migration completed successfully.")
            
    except sqlite3.Error as e:
        connection.rollback()
        print(f"Error during genre data migration: {str(e)}")
    finally:
        connection.close()

# Helper function to get database connection
def get_db_connection(timeout=30.0):
    """
    Create and return a new database connection with row factory enabled.
    
    Args:
        timeout (float): Timeout in seconds for the database connection
        
    Returns:
        sqlite3.Connection: An active connection to the SQLite database with row_factory
                           enabled for dict-like access to rows.
    """
    connection = sqlite3.connect(DATABASE, timeout=timeout)
    connection.row_factory = sqlite3.Row
    return connection

# Context manager for database connection to ensure proper closing
class DBConnection:
    """
    Context manager for database connections to ensure proper closing
    even when exceptions occur.
    
    Usage:
        with DBConnection() as conn:
            # use conn for database operations
    """
    def __init__(self, timeout=30.0):
        self.timeout = timeout
        self.conn = None
        
    def __enter__(self):
        self.conn = get_db_connection(self.timeout)
        return self.conn
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                # If there was an exception, roll back
                self.conn.rollback()
            else:
                # Otherwise, commit any pending transaction
                self.conn.commit()
            self.conn.close()
            
# Helper function to generate a UUID
def generate_uuid():
    """
    Generate a unique UUID string for database primary keys.
    
    Returns:
        str: A string representation of a UUID4 (random UUID).
    """
    return str(uuid.uuid4())

# ---------------------------- Authentication ----------------------------
auth_ns = Namespace('auth', 
                   description="Authentication operations for user login and registration")

# Model definitions for request validation and Swagger documentation
register_model = api.model('Register', {
    'username': fields.String(required=True, description="Username for login (must be unique)"),
    'password': fields.String(required=True, description="User's password (will be hashed)")
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description="Username for login"),
    'password': fields.String(required=True, description="User's password")
})

@auth_ns.route('/register')
class Register(Resource):
    """User registration resource for creating new authentication credentials"""
    
    @auth_ns.expect(register_model)
    @auth_ns.doc(responses={
        201: 'User registered successfully',
        400: 'Username already exists or invalid data'
    })
    def post(self):
        """
        Register a new user account
        
        Creates a new user in the Authentication table with a hashed password.
        Returns an error if the username already exists.
        """
        data = request.json
        username = data['username']
        password = generate_password_hash(data['password'])
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO Authentication (username, password) VALUES (?, ?)", (username, password))
            connection.commit()
            return {"message": "User registered successfully"}, 201
        except sqlite3.IntegrityError:
            return {"message": "Username already exists"}, 400
        finally:
            connection.close()

@auth_ns.route('/login')
class Login(Resource):
    """User login resource for obtaining JWT tokens"""
    
    @auth_ns.expect(login_model)
    @auth_ns.doc(responses={
        200: 'Login successful, returns access token',
        401: 'Invalid credentials'
    })
    def post(self):
        """
        Login and get an access token
        
        Authenticates user credentials and issues a JWT token for API access.
        The token should be included in the Authorization header for subsequent requests.
        """
        data = request.json
        username = data['username']
        password = data['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        user = cursor.execute("SELECT * FROM Authentication WHERE username = ?", (username,)).fetchone()
        connection.close()
        if user and check_password_hash(user['password'], password):
            # Create an access token with the username as the identity
            token = create_access_token(identity=username)
            return {"access_token": token}, 200
        return {"message": "Invalid credentials"}, 401

# Add authentication namespace
api.add_namespace(auth_ns)

# ---------------------------- Account ----------------------------

account_ns = Namespace('accounts', description="Manage accounts")
account_model = api.model('Account', {
    'account_id': fields.String(description="Unique identifier (UUID) for the account"),
    'mail': fields.String(required=True, description="The email address"),
    'password_hash': fields.String(required=True, description="Password hash"),
    'password_salt': fields.String(required=True, description="Password salt"),
    'full_name': fields.String(description="The full name"),
    'is_subscriber': fields.Boolean(description="Subscription status"),
    'registration_date': fields.DateTime(dt_format='iso8601', description="Registration timestamp"),
    'country': fields.String(description="Country"),
    'sex': fields.String(description="Gender", enum=['Male', 'Female', 'Other', 'Prefer not to say']),
    'language': fields.String(required=True, description="Preferred language"),
    'birth_date': fields.Date(description="Date of birth (YYYY-MM-DD)"),
    'last_login': fields.DateTime(dt_format='iso8601', description="Last login timestamp")
})

@account_ns.route('/')
class AccountList(Resource):
    @jwt_required()
    @account_ns.marshal_list_with(account_model)
    def get(self):
        """Get all accounts"""
        try:
            with DBConnection() as connection:
                accounts = connection.execute('SELECT * FROM Account').fetchall()
                return [dict(account) for account in accounts]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    @account_ns.expect(account_model)
    def post(self):
        """Create a new account"""
        data = request.json
        
        # Validate sex field if provided
        if 'sex' in data and data['sex'] not in ['Male', 'Female', 'Other', 'Prefer not to say']:
            return {"message": "Invalid value for sex. Must be one of: Male, Female, Other, Prefer not to say"}, 400
            
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if account exists
        account = cursor.execute('SELECT * FROM Account WHERE account_id = ?', (data['account_id'],)).fetchone()
        if not account:
            connection.close()
            return {"message": "Account not found. Create an account first."}, 404
            
        try:
            cursor.execute('''
                INSERT INTO Account (
                    account_id, mail, password_hash, password_salt, 
                    full_name, is_subscriber, registration_date,
                    country, sex, language, birth_date, last_login
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                data['account_id'], 
                data['mail'], 
                data['password_hash'],
                data['password_salt'],
                data.get('full_name'), 
                data.get('is_subscriber', 0),
                data.get('country'), 
                data.get('sex'), 
                data['language'], 
                data.get('birth_date')
            ))
            connection.commit()
            connection.close()
            return {"message": "Account created successfully"}, 201
        except sqlite3.IntegrityError as e:
            connection.close()
            return {"message": f"Error creating account: {str(e)}"}, 400

@account_ns.route('/<string:account_id>')
class Account(Resource):
    @jwt_required()
    @account_ns.marshal_with(account_model)
    def get(self, account_id):
        """Get an account by ID"""
        connection = get_db_connection()
        account = connection.execute('SELECT * FROM Account WHERE account_id = ?', (account_id,)).fetchone()
        connection.close()
        if account is None:
            return {"message": "Account not found"}, 404
        return dict(account)

    @jwt_required()
    @account_ns.expect(account_model)
    def put(self, account_id):
        """Update an account"""
        data = request.json
        
        # Validate sex field if provided
        if 'sex' in data and data['sex'] not in ['Male', 'Female', 'Other', 'Prefer not to say']:
            return {"message": "Invalid value for sex. Must be one of: Male, Female, Other, Prefer not to say"}, 400
            
        connection = get_db_connection()
        
        try:
            connection.execute('''
                UPDATE Account SET 
                    mail = ?, 
                    full_name = ?, 
                    is_subscriber = ?, 
                    country = ?, 
                    sex = ?, 
                    language = ?, 
                    birth_date = ?,
                    last_login = CURRENT_TIMESTAMP
                WHERE account_id = ?
            ''', (
                data['mail'], 
                data.get('full_name'), 
                data.get('is_subscriber', 0), 
                data.get('country'),
                data.get('sex'), 
                data['language'], 
                data.get('birth_date'), 
                account_id
            ))
            connection.commit()
            connection.close()
            return {"message": "Account updated successfully"}, 200
        except sqlite3.IntegrityError as e:
            connection.close()
            return {"message": f"Error updating account: {str(e)}"}, 400

    @jwt_required()
    def delete(self, account_id):
        """Delete an account"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Account WHERE account_id = ?', (account_id,))
        connection.commit()
        connection.close()
        return {"message": "Account deleted successfully"}, 200

api.add_namespace(account_ns)

# ---------------------------- User ----------------------------

user_ns = Namespace('users', 
                   description="Manage user profiles and basic user information")

user_model = api.model('User', {
    'user_id': fields.String(description="Unique identifier (UUID) for the user"),
    'nickname': fields.String(required=True, description="User's public display name (min 3 characters)"),
    'favorite_genre': fields.String(description="User's preferred music genre"),
    'user_image': fields.String(description="Profile image encoded in base64 format")
})

@user_ns.route('/')
class UserList(Resource):
    """Resource for managing the collection of users"""
    
    @jwt_required()
    @user_ns.marshal_list_with(user_model)
    @user_ns.doc(responses={
        200: 'Success - Returns list of users',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self):
        """
        Get all registered users
        
        Returns a list of all users in the system with their basic profile information.
        Requires authentication.
        """
        connection = get_db_connection()
        users = connection.execute('SELECT * FROM User').fetchall()
        connection.close()
        return [dict(user) for user in users]

    @jwt_required()
    @user_ns.expect(user_model)
    @user_ns.doc(responses={
        201: 'User created successfully',
        400: 'Bad request - Invalid data or nickname already exists',
        401: 'Unauthorized - Invalid or missing token'
    })
    def post(self):
        """Create a new user"""
        data = request.json
        
        # Check nickname length constraint
        if len(data.get('nickname', '')) < 3:
            return {"message": "Nickname must be at least 3 characters long."}, 400
            
        try:
            # Generate a UUID if not provided
            if 'user_id' not in data:
                data['user_id'] = generate_uuid()
                
            with DBConnection() as connection:
                cursor = connection.cursor()
                # Insert the user with the UUID
                cursor.execute(
                    'INSERT INTO User (user_id, nickname, favorite_genre, user_image) VALUES (?, ?, ?, ?)',
                    (data['user_id'], data['nickname'], data.get('favorite_genre'), data.get('user_image'))
                )
            
            return {"message": "User created successfully", "user_id": data['user_id']}, 201
        except sqlite3.IntegrityError:
            return {"message": "A user with this nickname already exists"}, 409
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_ns.route('/<string:user_id>')
class User(Resource):
    """Resource for managing individual user profiles"""
    
    @jwt_required()
    @user_ns.marshal_with(user_model)
    @user_ns.doc(responses={
        200: 'Success - Returns user details',
        404: 'User not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self, user_id):
        """
        Get a specific user's profile by ID
        
        Returns the profile information for the user with the specified ID.
        """
        connection = get_db_connection()
        user = connection.execute('SELECT * FROM User WHERE user_id = ?', (user_id,)).fetchone()
        connection.close()
        if user is None:
            return {"message": "User not found"}, 404
        return dict(user)

    @jwt_required()
    @user_ns.expect(user_model)
    def put(self, user_id):
        """Update a user"""
        data = request.json
        connection = get_db_connection()
        connection.execute('UPDATE User SET nickname = ?, favorite_genre = ?, user_image = ? WHERE user_id = ?',
                           (data['nickname'], data.get('favorite_genre'), data.get('user_image'), user_id))
        connection.commit()
        connection.close()
        return {"message": "User updated successfully"}, 200

    @jwt_required()
    def delete(self, user_id):
        """Delete a user"""
        connection = get_db_connection()
        connection.execute('DELETE FROM User WHERE user_id = ?', (user_id,))
        connection.commit()
        connection.close()
        return {"message": "User deleted successfully"}, 200

# get the user with nickname
@user_ns.route('/nickname/<string:nickname>')
class UserByNickname(Resource):
    @jwt_required()
    @user_ns.marshal_with(user_model)
    def get(self, nickname):
        """Get a user by nickname"""
        connection = get_db_connection()
        users = connection.execute('SELECT * FROM User WHERE nickname = ?', (nickname,)).fetchall()
        connection.close()
        if not users:
            return {"message": "User not found"}, 404
        return [dict(user) for user in users]

# a complex query to get all users with their follower counts
@user_ns.route('/follower-counts')
class UserFollowerCounts(Resource):
    @jwt_required()
    def get(self):
        """Get all users with their follower counts"""
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
        SELECT User.user_id, User.nickname, COALESCE(f.follower_count, 0) as follower_count
        FROM User
        LEFT JOIN (
            SELECT user_id_2, COUNT(*) AS follower_count
            FROM Follower
            GROUP BY user_id_2
        ) AS f
        ON User.user_id = f.user_id_2
        """

        try:
            results = cursor.execute(query).fetchall()
            follower_counts = [
                {
                    'user_id': row['user_id'],
                    'nickname': row['nickname'],
                    'follower_count': row['follower_count']
                }
                for row in results
            ]
            return follower_counts, 200
        except sqlite3.Error as e:
            return {'message': f'Database error: {str(e)}'}, 500
        finally:
            connection.close()

api.add_namespace(user_ns)

# ---------------------------- Follower ----------------------------

follower_ns = Namespace('followers', description="Manage follower relationships")
follower_model = api.model('Follower', {
    'user_id_1': fields.String(required=True, description="The ID of the user who is following"),
    'user_id_2': fields.String(required=True, description="The ID of the user being followed")
})

@follower_ns.route('/')
class followerList(Resource):
    @jwt_required()
    @follower_ns.marshal_list_with(follower_model)
    def get(self):
        """Get all follower relationships"""
        try:
            with DBConnection() as connection:
                followers = connection.execute('SELECT * FROM Follower').fetchall()
                return [dict(follower) for follower in followers]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    @follower_ns.expect(follower_model)
    def post(self):
        """Create a new follower relationship"""
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Check if the follower user exists
                follower = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (data['user_id_1'],)).fetchone()
                if not follower:
                    return {"message": "Follower user not found"}, 404
                
                # Check if the followed user exists
                followed = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (data['user_id_2'],)).fetchone()
                if not followed:
                    return {"message": "Followed user not found"}, 404
                
                # Check if the relationship already exists
                existing = cursor.execute(
                    'SELECT 1 FROM Follower WHERE user_id_1 = ? AND user_id_2 = ?',
                    (data['user_id_1'], data['user_id_2'])
                ).fetchone()
                
                if existing:
                    return {"message": "This follower relationship already exists"}, 409
                
                cursor.execute(
                    'INSERT INTO Follower (user_id_1, user_id_2) VALUES (?, ?)',
                    (data['user_id_1'], data['user_id_2'])
                )
                
            return {"message": "Follower relationship created successfully"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@follower_ns.route('/<string:user_id_1>/followers/<string:user_id_2>')
class follower(Resource):
    @jwt_required()
    @follower_ns.marshal_with(follower_model)
    def get(self, user_id_1, user_id_2):
        """Get a specific follower relationship"""
        try:
            with DBConnection() as connection:
                follower = connection.execute(
                    'SELECT * FROM Follower WHERE user_id_1 = ? AND user_id_2 = ?',
                    (user_id_1, user_id_2)
                ).fetchone()
                
                if follower is None:
                    return {"message": "Follower relationship not found"}, 404
                return dict(follower)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    def delete(self, user_id_1, user_id_2):
        """Delete a follower relationship"""
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Check if both users exist before attempting to delete the relationship
                follower = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (user_id_1,)).fetchone()
                if not follower:
                    return {"message": "Follower user not found"}, 404
                
                followed = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (user_id_2,)).fetchone()
                if not followed:
                    return {"message": "Followed user not found"}, 404
                
                cursor.execute('DELETE FROM Follower WHERE user_id_1 = ? AND user_id_2 = ?', (user_id_1, user_id_2))
                if cursor.rowcount == 0:
                    return {"message": "Follower relationship not found"}, 404
                
                return {"message": "Follower relationship deleted successfully"}, 200
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

api.add_namespace(follower_ns)

# ---------------------------- Playlist ----------------------------
playlist_ns = Namespace('playlists', description="Create and manage your playlists")
playlist_model = api.model('Playlist', {
    'playlist_id': fields.String(description="Unique playlist identifier (auto-generated)"),
    'playlist_name': fields.String(required=True, description="What to call your playlist"),
    'playlist_description': fields.String(description="A few words about your playlist"),
    'playlist_image': fields.String(description="Cover image (base64 encoded)"),
    'creator_id': fields.String(required=True, description="Who created this playlist")
})

@playlist_ns.route('/')
class PlaylistList(Resource):
    @jwt_required()
    @playlist_ns.marshal_list_with(playlist_model)
    def get(self):
        """Get all available playlists"""
        connection = get_db_connection()
        playlists = connection.execute('SELECT * FROM Playlist').fetchall()
        connection.close()
        return [dict(playlist) for playlist in playlists]

    @jwt_required()
    @playlist_ns.expect(playlist_model)
    def post(self):
        """Create a new playlist"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if user exists
        user = cursor.execute('SELECT user_id FROM User WHERE user_id = ?', 
                             (data['creator_id'],)).fetchone()
        if not user:
            connection.close() 
            return {"message": "Cannot create playlist: user doesn't exist"}, 404
            
        # Create the playlist with UUID
        playlist_id = generate_uuid()
        cursor.execute('''
            INSERT INTO Playlist 
            (playlist_id, playlist_name, playlist_description, playlist_image, creator_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (
            playlist_id,
            data['playlist_name'], 
            data.get('playlist_description'), 
            data.get('playlist_image'), 
            data['creator_id']
        ))
        
        connection.commit()
        connection.close()
        return {"message": "Playlist created successfully", "playlist_id": playlist_id}, 201

@playlist_ns.route('/<string:playlist_id>')
class Playlist(Resource):
    @jwt_required()
    @playlist_ns.marshal_with(playlist_model)
    def get(self, playlist_id):
        """Get details about a specific playlist"""
        connection = get_db_connection()
        playlist = connection.execute('SELECT * FROM Playlist WHERE playlist_id = ?', (playlist_id,)).fetchone()
        connection.close()
        if playlist is None:
            return {"message": "Playlist not found"}, 404
        return dict(playlist)

    @jwt_required()
    @playlist_ns.expect(playlist_model)
    def put(self, playlist_id):
        """Update a playlist's details"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First check if playlist exists
        playlist = cursor.execute('SELECT playlist_id FROM Playlist WHERE playlist_id = ?', 
                                 (playlist_id,)).fetchone()
        if not playlist:
            connection.close()
            return {"message": "Cannot update: playlist doesn't exist"}, 404
            
        # Update the playlist
        cursor.execute('''
            UPDATE Playlist 
            SET playlist_name = ?, playlist_description = ?, playlist_image = ?, creator_id = ? 
            WHERE playlist_id = ?
        ''', (
            data['playlist_name'], 
            data.get('playlist_description'), 
            data.get('playlist_image'), 
            data['creator_id'], 
            playlist_id
        ))
        
        connection.commit()
        connection.close()
        return {"message": "Playlist updated successfully"}, 200

    @jwt_required()
    def delete(self, playlist_id):
        """Delete a playlist"""
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if playlist exists first
        playlist = cursor.execute('SELECT 1 FROM Playlist WHERE playlist_id = ?', 
                                 (playlist_id,)).fetchone()
        if not playlist:
            connection.close()
            return {"message": "Cannot delete: playlist doesn't exist"}, 404
            
        cursor.execute('DELETE FROM Playlist WHERE playlist_id = ?', (playlist_id,))
        connection.commit()
        connection.close()
        return {"message": "Playlist deleted successfully"}, 200

api.add_namespace(playlist_ns)

# ---------------------------- Playlist_User ----------------------------

playlist_user_ns = Namespace('playlist_users', description="Manage playlist-user relationships")
playlist_user_model = api.model('PlaylistUser', {
    'user_id': fields.String(required=True, description="The user ID"),
    'playlist_id': fields.String(required=True, description="The playlist ID")
})

@playlist_user_ns.route('/')
class PlaylistUserList(Resource):
    @jwt_required()
    @playlist_user_ns.marshal_list_with(playlist_user_model)
    def get(self):
        """Get all playlist-user relationships"""
        try:
            with DBConnection() as connection:
                playlist_users = connection.execute('SELECT * FROM Playlist_User').fetchall()
                return [dict(playlist_user) for playlist_user in playlist_users]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    @playlist_user_ns.expect(playlist_user_model)
    def post(self):
        """Create a new playlist-user relationship"""
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # First, verify the playlist exists
                playlist = cursor.execute('SELECT playlist_id FROM Playlist WHERE playlist_id = ?', 
                                        (data['playlist_id'],)).fetchone()
                if not playlist:
                    return {"message": "Cannot add user to a playlist that doesn't exist"}, 404
                    
                # Then verify the user exists
                user = cursor.execute('SELECT user_id FROM User WHERE user_id = ?', 
                                    (data['user_id'],)).fetchone()
                if not user:
                    return {"message": "Cannot add non-existent user to playlist"}, 404
                
                # Check if the relationship already exists
                existing = cursor.execute(
                    'SELECT 1 FROM Playlist_User WHERE user_id = ? AND playlist_id = ?',
                    (data['user_id'], data['playlist_id'])
                ).fetchone()
                
                if existing:
                    return {"message": "This user is already associated with this playlist"}, 409
                
                # If both exist, create the relationship
                cursor.execute('INSERT INTO Playlist_User (user_id, playlist_id) VALUES (?, ?)',
                            (data['user_id'], data['playlist_id']))
                
                return {"message": "User added to playlist successfully"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@playlist_user_ns.route('/<string:user_id>/<string:playlist_id>')
class PlaylistUser(Resource):
    @jwt_required()
    @playlist_user_ns.marshal_with(playlist_user_model)
    def get(self, user_id, playlist_id):
        """Get a specific playlist-user relationship"""
        try:
            with DBConnection() as connection:
                playlist_user = connection.execute('SELECT * FROM Playlist_User WHERE user_id = ? AND playlist_id = ?', 
                                                (user_id, playlist_id)).fetchone()
                
                if playlist_user is None:
                    return {"message": "This user isn't associated with that playlist"}, 404
                return dict(playlist_user)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    def delete(self, user_id, playlist_id):
        """Remove a user from a playlist"""
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Verify the playlist exists
                playlist = cursor.execute('SELECT playlist_id FROM Playlist WHERE playlist_id = ?', 
                                        (playlist_id,)).fetchone()
                if not playlist:
                    return {"message": "Playlist not found"}, 404
                    
                # Verify the user exists
                user = cursor.execute('SELECT user_id FROM User WHERE user_id = ?', 
                                    (user_id,)).fetchone()
                if not user:
                    return {"message": "User not found"}, 404
                
                # Verify the relationship exists before deletion
                relationship = cursor.execute(
                    'SELECT 1 FROM Playlist_User WHERE user_id = ? AND playlist_id = ?',
                    (user_id, playlist_id)
                ).fetchone()
                
                if not relationship:
                    return {"message": "This user isn't associated with that playlist"}, 404
                
                cursor.execute('DELETE FROM Playlist_User WHERE user_id = ? AND playlist_id = ?', 
                            (user_id, playlist_id))
                
                return {"message": "User removed from playlist successfully"}, 200
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

api.add_namespace(playlist_user_ns)

# ---------------------------- Playlist_Song ----------------------------

playlist_song_ns = Namespace('playlist_songs', description="Manage songs in playlists")
playlist_song_model = api.model('PlaylistSong', {
    'playlist_id': fields.String(required=True, description="The playlist ID"),
    'song_id': fields.String(required=True, description="The song ID")
})

@playlist_song_ns.route('/')
class PlaylistSongList(Resource):
    @playlist_song_ns.marshal_list_with(playlist_song_model)
    @jwt_required()
    def get(self):
        """See all songs in all playlists"""
        connection = get_db_connection()
        playlist_songs = connection.execute('SELECT * FROM Playlist_Song').fetchall()
        connection.close()
        return [dict(playlist_song) for playlist_song in playlist_songs]

    @jwt_required()
    @playlist_song_ns.expect(playlist_song_model)
    def post(self):
        """Add a song to a playlist"""
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # First, verify the playlist exists
                playlist = cursor.execute('SELECT playlist_id FROM Playlist WHERE playlist_id = ?', 
                                       (data['playlist_id'],)).fetchone()
                if not playlist:
                    return {"message": "Cannot add songs to a playlist that doesn't exist"}, 404
                    
                # Then verify the song exists
                song = cursor.execute('SELECT song_id FROM Song WHERE song_id = ?', 
                                   (data['song_id'],)).fetchone()
                if not song:
                    return {"message": "Cannot add a non-existent song to a playlist"}, 404
                    
                # Check if the song is already in the playlist
                existing = cursor.execute('SELECT 1 FROM Playlist_Song WHERE playlist_id = ? AND song_id = ?',
                                       (data['playlist_id'], data['song_id'])).fetchone()
                if existing:
                    return {"message": "This song is already in the playlist"}, 409  # Conflict
                
                # If both exist and no duplicate, add the song to the playlist
                cursor.execute('INSERT INTO Playlist_Song (playlist_id, song_id) VALUES (?, ?)',
                            (data['playlist_id'], data['song_id']))
                
                return {"message": "Song added to playlist successfully"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@playlist_song_ns.route('/<string:playlist_id>/songs/<string:song_id>')
class PlaylistSong(Resource):
    @jwt_required()
    @playlist_song_ns.marshal_with(playlist_song_model)
    def get(self, playlist_id, song_id):
        """Get a specific playlist-song relationship"""
        connection = get_db_connection()
        playlist_song = connection.execute('SELECT * FROM Playlist_Song WHERE playlist_id = ? AND song_id = ?', 
                                          (playlist_id, song_id)).fetchone()
        connection.close()
        if playlist_song is None:
            return {"message": "Song not found in playlist"}, 404
        return dict(playlist_song)

    @jwt_required()
    def delete(self, playlist_id, song_id):
        """Remove a song from a playlist"""
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First check if the playlist exists
        playlist = cursor.execute('SELECT 1 FROM Playlist WHERE playlist_id = ?', 
                                 (playlist_id,)).fetchone()
        if not playlist:
            connection.close()
            return {"message": "That playlist doesn't exist"}, 404
        
        # Delete the relationship
        cursor.execute('DELETE FROM Playlist_Song WHERE playlist_id = ? AND song_id = ?', 
                      (playlist_id, song_id))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "This song isn't in that playlist"}, 404
        
        connection.commit()
        connection.close()
        return {"message": "Song removed from playlist successfully"}, 200

api.add_namespace(playlist_song_ns)

# ---------------------------- Like ----------------------------

like_ns = Namespace('likes', description="Manage likes for songs")
like_model = api.model('Like', {
    'user_id': fields.String(required=True, description="The ID of the user liking the song"),
    'song_id': fields.String(required=True, description="The ID of the liked song")
})

@like_ns.route('/')
class LikeList(Resource):
    @jwt_required()
    @like_ns.marshal_list_with(like_model)
    def get(self):
        """Get all likes"""
        connection = get_db_connection()
        likes = connection.execute('SELECT * FROM UserLikes').fetchall()
        connection.close()
        return [dict(like) for like in likes]

    @jwt_required()
    @like_ns.expect(like_model)
    def post(self):
        """Create a new like"""
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Verify the user exists
                user = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (data['user_id'],)).fetchone()
                if not user:
                    return {"message": "Cannot create like for non-existent user"}, 404
                    
                # Verify the song exists
                song = cursor.execute('SELECT 1 FROM Song WHERE song_id = ?', (data['song_id'],)).fetchone()
                if not song:
                    return {"message": "Cannot like a non-existent song"}, 404
                
                # Check if this like already exists
                existing = cursor.execute(
                    'SELECT 1 FROM UserLikes WHERE user_id = ? AND song_id = ?',
                    (data['user_id'], data['song_id'])
                ).fetchone()
                
                if existing:
                    return {"message": "This song is already liked by this user"}, 409  # Conflict
                
                cursor.execute('INSERT INTO UserLikes (user_id, song_id) VALUES (?, ?)',
                           (data['user_id'], data['song_id']))
                
                return {"message": "Like created successfully"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@like_ns.route('/<string:user_id>/songs/<string:song_id>')
class Like(Resource):
    @jwt_required()
    @like_ns.marshal_with(like_model)
    def get(self, user_id, song_id):
        """Get a specific like"""
        connection = get_db_connection()
        like = connection.execute(
            'SELECT * FROM UserLikes WHERE user_id = ? AND song_id = ?',
            (user_id, song_id)
        ).fetchone()
        connection.close()
        if like is None:
            return {"message": "Like not found"}, 404
        return dict(like)

    @jwt_required()
    def delete(self, user_id, song_id):
        """Delete a like"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM UserLikes WHERE user_id = ? AND song_id = ?', (user_id, song_id))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "Like not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "Like deleted successfully"}, 200

api.add_namespace(like_ns)

# ---------------------------- Song ----------------------------

song_ns = Namespace('songs', 
                   description="Manage songs and their metadata")

song_model = api.model('Song', {
    'song_id': fields.String(description="The ID of the song (auto-generated)"),
    'song_name': fields.String(required=True, description="The title of the song"),
    'song_time': fields.Integer(required=True, description="The duration of the song in seconds"),
    'song_image': fields.String(description="Song artwork image encoded in base64 format"),
    'audio': fields.String(description="The audio file encoded in base64 format (for small audio files)")
})

@song_ns.route('/')
class SongList(Resource):
    """Resource for managing the collection of songs"""
    
    @jwt_required()
    @song_ns.marshal_list_with(song_model)
    @song_ns.doc(responses={
        200: 'Success - Returns list of songs',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self):
        """
        Get all songs
        
        Returns a list of all songs in the library with their metadata.
        """
        connection = get_db_connection()
        songs = connection.execute('SELECT * FROM Song').fetchall()
        connection.close()
        return [dict(song) for song in songs]

    @jwt_required()
    @song_ns.expect(song_model)
    @song_ns.doc(responses={
        201: 'Song created successfully',
        400: 'Bad request - Invalid data',
        401: 'Unauthorized - Invalid or missing token'
    })
    def post(self):
        """
        Create a new song
        
        Creates a new song in the library with the provided information.
        The song_id will be auto-generated as a UUID.
        
        Required fields:
        - song_name: The title of the song
        - song_time: Duration in seconds (must be positive)
        
        Optional fields:
        - song_image: Base64-encoded image for the song artwork
        - audio: Base64-encoded audio data (for small audio files)
        """
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Generate a UUID for the song
        song_id = generate_uuid()
        
        cursor.execute('INSERT INTO Song (song_id, song_name, song_time, song_image, audio) VALUES (?, ?, ?, ?, ?)',
                      (song_id, data['song_name'], data['song_time'], data.get('song_image'), data.get('audio')))
        connection.commit()
        connection.close()
        return {"message": "Song created successfully", "song_id": song_id}, 201

@song_ns.route('/<string:song_id>')
class Song(Resource):
    """Resource for managing individual songs"""
    
    @jwt_required()
    @song_ns.marshal_with(song_model)
    @song_ns.doc(responses={
        200: 'Success - Returns song details',
        404: 'Song not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self, song_id):
        """
        Get a specific song by ID
        
        Returns the details of the song with the specified ID.
        """
        connection = get_db_connection()
        song = connection.execute('SELECT * FROM Song WHERE song_id = ?', (song_id,)).fetchone()
        connection.close()
        if song is None:
            return {"message": "Song not found"}, 404
        return dict(song)

    @jwt_required()
    @song_ns.expect(song_model)
    def put(self, song_id):
        """Update a song"""
        data = request.json
        connection = get_db_connection()
        connection.execute('UPDATE Song SET song_name = ?, song_time = ?, song_image = ?, audio = ? WHERE song_id = ?',
                           (data['song_name'], data['song_time'], data.get('song_image'), data.get('audio'), song_id))
        connection.commit()
        connection.close()
        return {"message": "Song updated successfully"}, 200

    @jwt_required()
    def delete(self, song_id):
        """Delete a song"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Song WHERE song_id = ?', (song_id,))
        connection.commit()
        connection.close()
        return {"message": "Song deleted successfully"}, 200
    
# get the song with song_name
@song_ns.route('/name/<string:song_name>')
class SongByName(Resource):
    @jwt_required()
    @song_ns.marshal_with(song_model)
    def get(self, song_name):
        """Get a song by name"""
        connection = get_db_connection()
        songs = connection.execute('SELECT * FROM Song WHERE song_name LIKE ?', (f'%{song_name}%',)).fetchall()
        connection.close()
        if not songs:
            return {"message": "No songs found with that name"}, 404
        return [dict(song) for song in songs]

api.add_namespace(song_ns)

# ---------------------------- Genre ----------------------------

genre_ns = Namespace('genres', description="Manage genres")
genre_model = api.model('Genre', {
    'genre_id': fields.String(description="The ID of the genre (auto-generated)"),
    'song_id': fields.String(required=True, description="The ID of the song this genre is associated with"),
    'genre_name': fields.String(required=True, description="The name of the genre")
})

# Migration function to update the Genre table structure
def migrate_genre_structure():
    """Migrate from the old SongGenre and Genre tables to the new Genre structure"""
    try:
        # First check if the SongGenre table exists
        with DBConnection() as connection:
            cursor = connection.cursor()
            
            # Check if SongGenre table exists
            table_exists = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='SongGenre'"
            ).fetchone()
            
            if not table_exists:
                # Already migrated or fresh install
                return
            
            # Check if Genre table has song_id column
            has_song_id = False
            try:
                cursor.execute("SELECT song_id FROM Genre LIMIT 1")
                has_song_id = True
            except sqlite3.OperationalError:
                # song_id column doesn't exist yet
                pass
                
            if not has_song_id:
                # Add the song_id column to Genre table
                cursor.execute("ALTER TABLE Genre ADD COLUMN song_id CHAR(36)")
                
                # Create a new index for song_id
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_genre_song_id ON Genre(song_id)")
                
                # Drop the UNIQUE constraint on genre_name
                # SQLite doesn't support dropping constraints, so we need to recreate the table
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS Genre_new (
                        genre_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
                        genre_name VARCHAR(50) NOT NULL CHECK (length(genre_name) > 0),
                        song_id CHAR(36),
                        FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
                """)
                
                # Copy data from old table to new table
                cursor.execute("INSERT INTO Genre_new (genre_id, genre_name) SELECT genre_id, genre_name FROM Genre")
                
                # Drop the old table
                cursor.execute("DROP TABLE Genre")
                
                # Rename the new table
                cursor.execute("ALTER TABLE Genre_new RENAME TO Genre")
                
                # Recreate the index on genre_name
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_genre_name ON Genre(genre_name)")
            
            # Now migrate data from SongGenre to Genre
            # For each song-genre pair in SongGenre, create a new Genre entry
            rows = cursor.execute("""
                SELECT sg.song_id, g.genre_id, g.genre_name
                FROM SongGenre sg
                JOIN Genre g ON sg.genre_id = g.genre_id
            """).fetchall()
            
            # If we have data to migrate
            if rows:
                # For each song-genre relationship
                for row in rows:
                    song_id, genre_id, genre_name = row
                    
                    # Generate a new UUID for each genre entry
                    new_genre_id = generate_uuid()
                    
                    # Insert a new row into Genre with the song_id
                    cursor.execute("""
                        INSERT INTO Genre (genre_id, genre_name, song_id)
                        VALUES (?, ?, ?)
                    """, (new_genre_id, genre_name, song_id))
                
                # After migration is done, drop the SongGenre table
                cursor.execute("DROP TABLE IF EXISTS SongGenre")
    
    except Exception as e:
        print(f"Error migrating genre structure: {str(e)}")
        
# Register the migration function to run at app startup
# app.before_first_request(migrate_genre_structure)

@genre_ns.route('/')
class GenreList(Resource):
    @jwt_required()
    @genre_ns.marshal_list_with(genre_model)
    def get(self):
        """Get all genres"""
        try:
            with DBConnection() as connection:
                genres = connection.execute('SELECT * FROM Genre').fetchall()
                return [dict(genre) for genre in genres]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    @genre_ns.expect(genre_model)
    def post(self):
        """Create a new genre"""
        data = request.json
        
        try:
            # Generate a UUID if not provided
            if 'genre_id' not in data:
                data['genre_id'] = generate_uuid()
                
            with DBConnection() as connection:
                cursor = connection.cursor()
                cursor.execute('INSERT INTO Genre (genre_id, genre_name, song_id) VALUES (?, ?, ?)',
                              (data['genre_id'], data['genre_name'], data['song_id']))
                
            return {"message": "Genre created successfully", "genre_id": data['genre_id']}, 201
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"message": "A genre with this name already exists"}, 409
            return {"message": f"Database integrity error: {str(e)}"}, 400
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@genre_ns.route('/<string:genre_id>')
class Genre(Resource):
    @jwt_required()
    @genre_ns.expect(genre_model)
    def put(self, genre_id):
        """Update a genre"""
        data = request.json
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                # Check if genre exists
                genre = cursor.execute('SELECT 1 FROM Genre WHERE genre_id = ?', (genre_id,)).fetchone()
                if not genre:
                    return {"message": "Genre not found"}, 404
                # Check if song exists
                song = cursor.execute('SELECT 1 FROM Song WHERE song_id = ?', (data['song_id'],)).fetchone()
                if not song:
                    return {"message": "Song not found"}, 404
                # Check if genre field exists
                genre_field = cursor.execute('SELECT 1 FROM GenreFields WHERE genre_id = ?', (data['genre_id'],)).fetchone()
                if not genre_field:
                    return {"message": "Genre field not found"}, 404
                cursor.execute('UPDATE Genre SET genre_name = ?, song_id = ? WHERE genre_id = ?',
                              (data['genre_name'], data['song_id'], genre_id))
            return {"message": "Genre updated successfully"}, 200
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"message": "A genre with this name already exists"}, 409
            return {"message": f"Database integrity error: {str(e)}"}, 400
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    def delete(self, genre_id):
        """Delete a genre"""
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                # Check if genre exists
                genre = cursor.execute('SELECT 1 FROM Genre WHERE genre_id = ?', (genre_id,)).fetchone()
                if not genre:
                    return {"message": "Genre not found"}, 404
                
                connection.execute('DELETE FROM Genre WHERE genre_id = ?', (genre_id,))
                return {"message": "Genre deleted successfully"}, 200
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

# Add endpoints for the many-to-many relationship
@genre_ns.route('/songs')
class SongGenreList(Resource):
    @jwt_required()
    @genre_ns.marshal_list_with(genre_model)
    def get(self):
        """Get all song-genre relationships"""
        try:
            with DBConnection() as connection:
                genres = connection.execute('SELECT * FROM Genre').fetchall()
                return [dict(genre) for genre in genres]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    @jwt_required()
    @genre_ns.expect(genre_model)
    def post(self):
        """Associate a song with a genre"""
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Check if the song exists
                song = cursor.execute('SELECT 1 FROM Song WHERE song_id = ?', (data['song_id'],)).fetchone()
                if not song:
                    return {"message": "Song not found"}, 404
                
                # Generate a UUID if not provided
                if 'genre_id' not in data:
                    data['genre_id'] = generate_uuid()
                
                # Check if this exact genre already exists for this song
                existing = cursor.execute(
                    'SELECT 1 FROM Genre WHERE song_id = ? AND genre_name = ?',
                    (data['song_id'], data['genre_name'])
                ).fetchone()
                
                if existing:
                    return {"message": "This song is already associated with this genre"}, 409
                
                cursor.execute(
                    'INSERT INTO Genre (genre_id, song_id, genre_name) VALUES (?, ?, ?)',
                    (data['genre_id'], data['song_id'], data['genre_name'])
                )
                
            return {"message": "Song associated with genre successfully", "genre_id": data['genre_id']}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@genre_ns.route('/songs/<string:song_id>/genres/<string:genre_id>')
class SongGenre(Resource):
    @jwt_required()
    @genre_ns.marshal_with(genre_model)
    def get(self, song_id, genre_id):
        """Get a specific song-genre relationship"""
        try:
            with DBConnection() as connection:
                genre = connection.execute(
                    'SELECT * FROM Genre WHERE genre_id = ? AND song_id = ?',
                    (genre_id, song_id)
                ).fetchone()
                
                if genre is None:
                    return {"message": "Song-genre relationship not found"}, 404
                    
                return dict(genre)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    def delete(self, song_id, genre_id):
        """Delete a song-genre relationship"""
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Check if the relationship exists
                genre = cursor.execute(
                    'SELECT 1 FROM Genre WHERE genre_id = ? AND song_id = ?',
                    (genre_id, song_id)
                ).fetchone()
                
                if not genre:
                    return {"message": "Song-genre relationship not found"}, 404
                
                cursor.execute(
                    'DELETE FROM Genre WHERE genre_id = ? AND song_id = ?',
                    (genre_id, song_id)
                )
                
            return {"message": "Song-genre relationship deleted successfully"}, 200
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

# a complex query to get the most listened genre in the last month
@genre_ns.route('/most-listened-last-month')
class MostListenedGenre(Resource):
    @jwt_required()
    def get(self):
        """Get the most listened to genres in the past month"""
        try:
            with DBConnection() as connection:
                # This query counts listens by genre over the last month
                genres = connection.execute("""
                    SELECT g.genre_name, COUNT(*) as listen_count
                    FROM History h
                    JOIN Genre g ON h.song_id = g.song_id
                    WHERE h.start_time >= datetime('now', '-1 month')
                    GROUP BY g.genre_name
                    ORDER BY listen_count DESC
                    LIMIT 10
                """).fetchall()
                
                result = [{'genre': genre['genre_name'], 'listens': genre['listen_count']} for genre in genres]
                return result, 200
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

api.add_namespace(genre_ns)

# ---------------------------- Album ----------------------------

album_ns = Namespace('albums', 
                    description="Manage music albums, their metadata, and track listings")

album_model = api.model('Album', {
    'album_id': fields.String(description="The ID of the album (auto-generated)"),
    'album_name': fields.String(required=True, description="The name of the album"),
    'about': fields.String(description="Information about the album"),
    'album_image': fields.String(description="Album cover image encoded in base64 format"),
    'release_date': fields.Date(description="Album release date (YYYY-MM-DD)")
})

@album_ns.route('/')
class AlbumList(Resource):
    """Resource for managing the collection of albums"""
    
    @jwt_required()
    @album_ns.marshal_list_with(album_model)
    @album_ns.doc(responses={
        200: 'Success - Returns list of albums',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self):
        """
        Get all albums
        
        Returns a list of all albums in the system with their metadata.
        """
        connection = get_db_connection()
        albums = connection.execute('SELECT * FROM Album').fetchall()
        connection.close()
        return [dict(album) for album in albums]

    @jwt_required()
    @album_ns.expect(album_model)
    @album_ns.doc(responses={
        201: 'Album created successfully',
        400: 'Bad request - Invalid data',
        401: 'Unauthorized - Invalid or missing token'
    })
    def post(self):
        """
        Create a new album
        
        Creates a new album with the provided information.
        The album_id will be auto-generated as a UUID.
        """
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Generate a UUID for the album
        album_id = generate_uuid()
        
        cursor.execute('INSERT INTO Album (album_id, album_name, about, album_image, release_date) VALUES (?, ?, ?, ?, ?)',
                      (album_id, data['album_name'], data.get('about'), data.get('album_image'), data.get('release_date')))
        connection.commit()
        connection.close()
        return {"message": "Album created successfully", "album_id": album_id}, 201

@album_ns.route('/<string:album_id>')
class Album(Resource):
    """Resource for managing individual albums"""
    
    @jwt_required()
    @album_ns.marshal_with(album_model)
    @album_ns.doc(responses={
        200: 'Success - Returns album details',
        404: 'Album not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self, album_id):
        """
        Get a specific album by ID
        
        Returns the details of the album with the specified ID.
        """
        connection = get_db_connection()
        album = connection.execute('SELECT * FROM Album WHERE album_id = ?', (album_id,)).fetchone()
        connection.close()
        if album is None:
            return {"message": "Album not found"}, 404
        return dict(album)

    @jwt_required()
    @album_ns.expect(album_model)
    @album_ns.doc(responses={
        200: 'Album updated successfully',
        404: 'Album not found',
        400: 'Bad request - Invalid data',
        401: 'Unauthorized - Invalid or missing token'
    })
    def put(self, album_id):
        """
        Update an album's information
        
        Updates the album with the specified ID with the provided information.
        All fields in the request will overwrite existing values.
        """
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if album exists first
        album = cursor.execute('SELECT 1 FROM Album WHERE album_id = ?', (album_id,)).fetchone()
        if not album:
            connection.close()
            return {"message": "Album not found"}, 404
            
        cursor.execute('UPDATE Album SET album_name = ?, about = ?, album_image = ?, release_date = ? WHERE album_id = ?',
                      (data['album_name'], data.get('about'), data.get('album_image'), data.get('release_date'), album_id))
        connection.commit()
        connection.close()
        return {"message": "Album updated successfully"}, 200

    @jwt_required()
    @album_ns.doc(responses={
        200: 'Album deleted successfully',
        404: 'Album not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def delete(self, album_id):
        """
        Delete an album
        
        Removes the album with the specified ID from the database.
        This will also remove all album-song relationships due to cascade constraints.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if album exists first
        album = cursor.execute('SELECT 1 FROM Album WHERE album_id = ?', (album_id,)).fetchone()
        if not album:
            connection.close()
            return {"message": "Album not found"}, 404
            
        cursor.execute('DELETE FROM Album WHERE album_id = ?', (album_id,))
        connection.commit()
        connection.close()
        return {"message": "Album deleted successfully"}, 200

# a complex query to get detailed listening stats for each album
@album_ns.route('/streaming-stats')
class AlbumStreamingStats(Resource):
    """Resource for album streaming analytics and statistics"""
    
    @jwt_required()
    @album_ns.doc(responses={
        200: 'Success - Returns streaming statistics',
        500: 'Server error while processing query',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self):
        """
        Get detailed listening statistics for each album
        
        Returns aggregated listening time data for each album based on user history.
        Albums are sorted by total listening time in descending order (most popular first).
        
        The calculation joins Album, Album_Info, Song, and History tables to track
        how much time users have spent listening to songs from each album.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
        SELECT albums.album_name AS album_name,
            COALESCE(SUM(stream.total_listen_time), 0) AS total_listen_time
        FROM (
            SELECT Album.album_id, Album.album_name, Album_Info.song_id
            FROM Album
            LEFT JOIN Album_Info
            ON Album.album_id = Album_Info.album_id
        ) AS albums
        LEFT JOIN (
            SELECT Song.song_id, Song.song_name,
                SUM(History.duration) AS total_listen_time
            FROM History
            JOIN Song ON History.song_id = Song.song_id
            GROUP BY Song.song_id
        ) AS stream
        ON albums.song_id = stream.song_id
        GROUP BY albums.album_id, albums.album_name
        ORDER BY total_listen_time DESC
        """
        
        try:
            results = cursor.execute(query).fetchall()
            connection.close()
            
            # Format the results as a list of dictionaries
            formatted_results = [
                {
                    'album_name': row['album_name'],
                    'total_listen_time': row['total_listen_time']
                }
                for row in results
            ]
            
            return formatted_results, 200
        except sqlite3.Error as e:
            connection.close()
            return {"message": f"Error retrieving streaming stats: {str(e)}"}, 500

api.add_namespace(album_ns)

# ---------------------------- Album_Info ----------------------------

album_info_ns = Namespace('album_infos', 
                         description="Manage the relationships between albums and songs (track listings)")

album_info_model = api.model('AlbumInfo', {
    'album_id': fields.String(required=True, description="Album ID - must reference an existing album"),
    'song_id': fields.String(required=True, description="Song ID - must reference an existing song"),
    'track_number': fields.Integer(description="Position of the song in the album (track number)")
})

@album_info_ns.route('/')
class AlbumInfoList(Resource):
    """Resource for managing album track listings"""
    
    @jwt_required()
    @album_info_ns.marshal_list_with(album_info_model)
    @album_info_ns.doc(responses={
        200: 'Success - Returns list of album-song relationships',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self):
        """
        Get all album-song connections
        
        Returns a list of all album-song relationships (track listings) in the system.
        """
        connection = get_db_connection()
        album_infos = connection.execute('SELECT * FROM Album_Info').fetchall()
        connection.close()
        return [dict(album_info) for album_info in album_infos]

    @jwt_required()
    @album_info_ns.expect(album_info_model)
    @album_info_ns.doc(responses={
        201: 'Song added to album successfully',
        404: 'Album or song not found',
        409: 'This song is already in this album',
        401: 'Unauthorized - Invalid or missing token'
    })
    def post(self):
        """
        Add a song to an album
        
        Creates a relationship between an album and a song, effectively adding
        the song to the album's track listing with an optional track number.
        """
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Verify the album exists
                album = cursor.execute('SELECT 1 FROM Album WHERE album_id = ?', (data['album_id'],)).fetchone()
                if not album:
                    return {"message": "Cannot add song to a non-existent album"}, 404
                    
                # Verify the song exists
                song = cursor.execute('SELECT 1 FROM Song WHERE song_id = ?', (data['song_id'],)).fetchone()
                if not song:
                    return {"message": "Cannot add a non-existent song to an album"}, 404
                    
                # Check if this album-song relationship already exists
                existing = cursor.execute(
                    'SELECT 1 FROM Album_Info WHERE album_id = ? AND song_id = ?', 
                    (data['album_id'], data['song_id'])
                ).fetchone()
                
                if existing:
                    return {"message": "This song is already in this album"}, 409  # Conflict
                    
                # Default track number to 1 if not provided
                track_number = data.get('track_number', 1)
                
                cursor.execute('INSERT INTO Album_Info (album_id, song_id, track_number) VALUES (?, ?, ?)',
                           (data['album_id'], data['song_id'], track_number))
                
                return {"message": "Song added to album successfully"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@album_info_ns.route('/<string:album_id>/songs/<string:song_id>')
class AlbumInfo(Resource):
    """Resource for managing specific album-song relationships"""
    
    @jwt_required()
    @album_info_ns.marshal_with(album_info_model)
    @album_info_ns.doc(responses={
        200: 'Success - Returns album-song relationship details',
        404: 'Relationship not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self, album_id, song_id):
        """
        Get details about a specific song in an album
        
        Returns information about a particular song within an album,
        including its track number.
        """
        connection = get_db_connection()
        album_info = connection.execute('SELECT * FROM Album_Info WHERE album_id = ? AND song_id = ?',
                                        (album_id, song_id)).fetchone()
        connection.close()
        if album_info is None:
            return {"message": "This song isn't in that album"}, 404
        return dict(album_info)

    @jwt_required()
    @album_info_ns.doc(responses={
        200: 'Song removed from album successfully',
        404: 'Relationship not found or album not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def delete(self, album_id, song_id):
        """
        Remove a song from an album
        
        Deletes the relationship between an album and a song,
        effectively removing the song from the album's track listing.
        """
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if the album exists
        album = cursor.execute('SELECT 1 FROM Album WHERE album_id = ?', (album_id,)).fetchone()
        if not album:
            connection.close()
            return {"message": "Album not found"}, 404
            
        # Delete the relationship
        cursor.execute('DELETE FROM Album_Info WHERE album_id = ? AND song_id = ?', (album_id, song_id))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "This song isn't in that album"}, 404
        
        connection.commit()
        connection.close()
        return {"message": "Song removed from album successfully"}, 200

api.add_namespace(album_info_ns)

# ---------------------------- Group ----------------------------

group_ns = Namespace('groups', description="Manage groups")
group_model = api.model('Group', {
    'group_id': fields.String(description="The ID of the group (auto-generated)"),
    'group_name': fields.String(required=True, description="The name of the group"),
    'number_of_members': fields.Integer(description="The number of members in the group"),
    'creation_date': fields.Date(description="The creation date of the group (YYYY-MM-DD)"),
    'group_image': fields.String(description="Group image encoded in base64 format")
})

@group_ns.route('/')
class GroupList(Resource):
    @jwt_required()
    @group_ns.marshal_list_with(group_model)
    def get(self):
        """Get all groups"""
        connection = get_db_connection()
        groups = connection.execute('SELECT * FROM MusicGroup').fetchall()
        connection.close()
        return [dict(group) for group in groups]

    @jwt_required()
    @group_ns.expect(group_model)
    def post(self):
        """Create a new group"""
        data = request.json
        
        try:
            # Generate a UUID for the group if not provided
            if 'group_id' not in data:
                data['group_id'] = generate_uuid()
                
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                cursor.execute('INSERT INTO MusicGroup (group_id, group_name, number_of_members, creation_date, group_image) VALUES (?, ?, ?, ?, ?)',
                              (data['group_id'], data['group_name'], data.get('number_of_members'),
                               data.get('creation_date'), data.get('group_image')))
                
            return {"message": "Group created successfully", "group_id": data['group_id']}, 201
        except sqlite3.IntegrityError:
            return {"message": "A group with this name already exists"}, 409
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@group_ns.route('/<string:group_id>')
class Group(Resource):
    @jwt_required()
    @group_ns.marshal_with(group_model)
    def get(self, group_id):
        """Get a group by ID"""
        connection = get_db_connection()
        group = connection.execute('SELECT * FROM MusicGroup WHERE group_id = ?', (group_id,)).fetchone()
        connection.close()
        if group is None:
            return {"message": "Group not found"}, 404
        return dict(group)

    @jwt_required()
    @group_ns.expect(group_model)
    def put(self, group_id):
        """Update a group"""
        data = request.json
        connection = get_db_connection()
        connection.execute('UPDATE MusicGroup SET group_name = ?, number_of_members = ?, creation_date = ?, group_image = ? WHERE group_id = ?',
                           (data['group_name'], data.get('number_of_members'), data.get('creation_date'), data.get('group_image'), group_id))
        connection.commit()
        connection.close()
        return {"message": "Group updated successfully"}, 200

    @jwt_required()
    def delete(self, group_id):
        """Delete a group"""
        connection = get_db_connection()
        connection.execute('DELETE FROM MusicGroup WHERE group_id = ?', (group_id,))
        connection.commit()
        connection.close()
        return {"message": "Group deleted successfully"}, 200

api.add_namespace(group_ns)

# ---------------------------- Album_Group ----------------------------

album_group_ns = Namespace('album_groups', description="Manage relationships between albums and groups")
album_group_model = api.model('AlbumGroup', {
    'album_id': fields.String(required=True, description="The ID of the album"),
    'group_id': fields.String(required=True, description="The ID of the group")
})

@album_group_ns.route('/')
class AlbumGroupList(Resource):
    @jwt_required()
    @album_group_ns.marshal_list_with(album_group_model)
    def get(self):
        """Get all album-group relationships"""
        connection = get_db_connection()
        album_groups = connection.execute('SELECT * FROM Album_Group').fetchall()
        connection.close()
        return [dict(album_group) for album_group in album_groups]

    @jwt_required()
    @album_group_ns.expect(album_group_model)
    def post(self):
        """Create a new album-group relationship"""
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Verify the album exists
                album = cursor.execute('SELECT 1 FROM Album WHERE album_id = ?', (data['album_id'],)).fetchone()
                if not album:
                    return {"message": "Cannot associate a non-existent album with a group"}, 404
                    
                # Verify the group exists
                group = cursor.execute('SELECT 1 FROM MusicGroup WHERE group_id = ?', (data['group_id'],)).fetchone()
                if not group:
                    return {"message": "Cannot associate an album with a non-existent group"}, 404
                
                # Check if this relationship already exists
                existing = cursor.execute(
                    'SELECT 1 FROM Album_Group WHERE album_id = ? AND group_id = ?',
                    (data['album_id'], data['group_id'])
                ).fetchone()
                
                if existing:
                    return {"message": "This album is already associated with this group"}, 409  # Conflict
                
                cursor.execute('INSERT INTO Album_Group (album_id, group_id) VALUES (?, ?)',
                           (data['album_id'], data['group_id']))
                
                return {"message": "Album-Group relationship created successfully"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@album_group_ns.route('/<string:album_id>/groups/<string:group_id>')
class AlbumGroup(Resource):
    @jwt_required()
    @album_group_ns.marshal_with(album_group_model)
    def get(self, album_id, group_id):
        """Get a specific album-group relationship"""
        connection = get_db_connection()
        album_group = connection.execute('SELECT * FROM Album_Group WHERE album_id = ? AND group_id = ?',
                                         (album_id, group_id)).fetchone()
        connection.close()
        if album_group is None:
            return {"message": "Album-Group relationship not found"}, 404
        return dict(album_group)

    @jwt_required()
    def delete(self, album_id, group_id):
        """Delete an album-group relationship"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Album_Group WHERE album_id = ? AND group_id = ?', (album_id, group_id))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "Album-Group relationship not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "Album-Group relationship deleted successfully"}, 200

api.add_namespace(album_group_ns)

# ---------------------------- Artist ----------------------------

artist_ns = Namespace('artists', description="Manage artists")
artist_model = api.model('Artist', {
    'artist_id': fields.String(description="Unique artist identifier (auto-generated)"),
    'full_name': fields.String(required=True, description="The full name of the artist"),
    'origin_country': fields.String(description="Country of origin for the artist"),
    'instrument': fields.String(description="Primary instrument played by the artist")
})

@artist_ns.route('/')
class ArtistList(Resource):
    @jwt_required()
    @artist_ns.marshal_list_with(artist_model)
    def get(self):
        """Get all artists"""
        connection = get_db_connection()
        artists = connection.execute('SELECT * FROM Artist').fetchall()
        return [dict(artist) for artist in artists]

    @jwt_required()
    @artist_ns.expect(artist_model)
    def post(self):
        """Create a new artist"""
        data = request.json
        cursor.execute('INSERT INTO Artist (artist_id, full_name, origin_country, instrument) VALUES (?, ?, ?, ?)',
                       (data['artist_id'], data['full_name'], data['origin_country'], data['instrument']))
        return {"message": "Artist created successfully"}, 201

@artist_ns.route('/<string:artist_id>')
class ArtistById(Resource):
    @jwt_required()
    @artist_ns.marshal_with(artist_model)
    def get(self, artist_id):
        """Get artist by ID"""
        connection = get_db_connection()
        artist = connection.execute('SELECT * FROM Artist WHERE artist_id = ?', (artist_id,)).fetchone()
        if artist is None:
            return {"message": "Artist not found"}, 404
        return dict(artist)

    @jwt_required()
    def delete(self, artist_id):
        """Remove an artist by ID"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Artist WHERE artist_id = ?', (artist_id,))
        if cursor.rowcount == 0:
            return {"message": "Artist not found"}, 404
        cursor.execute('DELETE FROM Artist WHERE artist_id = ?', (artist_id,))
        if cursor.rowcount == 0:
            return {"message": "Artist not found"}, 404
        return {"message": "Artist deleted successfully"}, 200

api.add_namespace(artist_ns)

# ---------------------------- History ----------------------------

history_ns = Namespace('histories', 
                      description="Track and analyze user listening history")

history_model = api.model('History', {
    'user_id': fields.String(required=True, description="ID of the user who listened to the song"),
    'start_time': fields.DateTime(required=True, description="When the listening session started", dt_format='iso8601'),
    'duration': fields.Integer(description="Length of the listening session in seconds"),
    'song_id': fields.String(required=True, description="ID of the song that was played")
})

@history_ns.route('/')
class HistoryList(Resource):
    """Resource for managing the collection of listening history records"""
    
    @jwt_required()
    @history_ns.marshal_list_with(history_model)
    @history_ns.doc(responses={
        200: 'Success - Returns list of history records',
        401: 'Unauthorized - Invalid or missing token',
        503: 'Service unavailable - Database is locked'
    })
    def get(self):
        """
        Get all listening history
        
        Returns a complete list of all user listening activity.
        This can be used for analytics and recommendation systems.
        """
        try:
            with DBConnection() as connection:
                history_records = connection.execute('SELECT * FROM History').fetchall()
                return [dict(history) for history in history_records]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    @history_ns.expect(history_model)
    @history_ns.doc(responses={
        201: 'History record created successfully',
        400: 'Bad request - Invalid data',
        401: 'Unauthorized - Invalid or missing token',
        404: 'User or song not found',
        503: 'Service unavailable - Database is locked'
    })
    def post(self):
        """
        Record a new listening session
        
        Logs when a user listens to a song, including how long they listened.
        The start_time will default to the current server time if not specified.
        """
        data = request.json
        
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                
                # Verify the user exists
                user = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (data['user_id'],)).fetchone()
                if not user:
                    return {"message": "Cannot log history for non-existent user"}, 404
                    
                # Verify the song exists
                song = cursor.execute('SELECT 1 FROM Song WHERE song_id = ?', (data['song_id'],)).fetchone()
                if not song:
                    return {"message": "Cannot log history for non-existent song"}, 404
                    
                # Use explicit start_time if provided, otherwise use CURRENT_TIMESTAMP
                if 'start_time' in data:
                    cursor.execute('INSERT INTO History (user_id, start_time, duration, song_id) VALUES (?, ?, ?, ?)',
                                  (data['user_id'], data['start_time'], data['duration'], data['song_id']))
                else:
                    cursor.execute('INSERT INTO History (user_id, duration, song_id) VALUES (?, ?, ?)',
                                  (data['user_id'], data['duration'], data['song_id']))
                    
            return {"message": "Listening session recorded!"}, 201
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@history_ns.route('/<string:user_id>')
class UserHistory(Resource):
    """Resource for managing a specific user's listening history"""
    
    @jwt_required()
    @history_ns.marshal_list_with(history_model)
    @history_ns.doc(responses={
        200: 'Success - Returns user history records or specific record',
        404: 'User or listening session not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def get(self, user_id):
        """
        Get listening history for a specific user
        
        Returns a user's listening history, sorted by time.
        Can filter for a specific listening session if start_time is provided as a query parameter.
        """
        # Get the start_time from query parameters if provided
        start_time = request.args.get('start_time')
        
        connection = get_db_connection()
        # First verify the user exists
        user = connection.execute('SELECT 1 FROM User WHERE user_id = ?', (user_id,)).fetchone()
        if not user:
            connection.close()
            return {"message": "User not found"}, 404
            
        if start_time:
            # If start_time is provided, get that specific record
            history = connection.execute(
                'SELECT * FROM History WHERE user_id = ? AND start_time = ?',
                (user_id, start_time)
            ).fetchone()
            connection.close()
            
            if history is None:
                return {"message": "Couldn't find that listening session"}, 404
            return dict(history)
        else:
            # If no start_time, get all history for the user
            history_records = connection.execute(
                'SELECT * FROM History WHERE user_id = ? ORDER BY start_time DESC',
                (user_id,)
            ).fetchall()
            connection.close()
            return [dict(record) for record in history_records]

    @jwt_required()
    @history_ns.doc(responses={
        200: 'Listening session(s) deleted successfully',
        400: 'Bad request - Missing required parameter',
        404: 'User or listening session not found',
        401: 'Unauthorized - Invalid or missing token'
    })
    def delete(self, user_id):
        """
        Delete listening history
        
        Removes one or all listening history records for a user.
        If start_time query parameter is provided, only that specific record is deleted.
        If no start_time is provided, all history for the user is cleared.
        """
        # Get the start_time from query parameters
        start_time = request.args.get('start_time')
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # First verify the user exists
        user = cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (user_id,)).fetchone()
        if not user:
            connection.close()
            return {"message": "User not found"}, 404
            
        if start_time:
            # Delete a specific history record
            cursor.execute('DELETE FROM History WHERE user_id = ? AND start_time = ?', (user_id, start_time))
            if cursor.rowcount == 0:
                connection.close()
                return {"message": "Couldn't find that listening session"}, 404
            connection.commit()
            connection.close()
            return {"message": "Listening session removed from history"}, 200
        else:
            # Delete all history for the user
            cursor.execute('DELETE FROM History WHERE user_id = ?', (user_id,))
            count = cursor.rowcount
            connection.commit()
            connection.close()
            return {"message": f"Removed {count} listening sessions from history"}, 200

api.add_namespace(history_ns)

# ---------------------------- GenreFields ----------------------------
genrefields_ns = Namespace('genrefields', description="Manage genre fields")
genrefields_model = api.model('GenreFields', {
    'genre_id': fields.Integer(description="The ID of the genre (auto-generated)"),
    'genre_name': fields.String(required=True, description="The name of the genre")
})

@genrefields_ns.route('/')
class GenreFieldsList(Resource):
    @jwt_required()
    @genrefields_ns.marshal_list_with(genrefields_model)
    def get(self):
        """Get all genre fields"""
        try:
            with DBConnection() as connection:
                genres = connection.execute('SELECT * FROM GenreFields').fetchall()
                return [dict(genre) for genre in genres]
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @jwt_required()
    @genrefields_ns.expect(genrefields_model)
    def post(self):
        """Create a new genre field"""
        data = request.json
        try:
            with DBConnection() as connection:
                cursor = connection.cursor()
                cursor.execute('INSERT INTO GenreFields (genre_name) VALUES (?)',
                              (data['genre_name'],))
            return {"message": "Genre field created successfully"}, 201
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return {"message": "A genre with this name already exists"}, 409
            return {"message": f"Database integrity error: {str(e)}"}, 400
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                return {"message": "Database is currently busy, please try again"}, 503
            return {"message": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

group_artist_ns = Namespace('group_artists', description="Manage group-artist relationships")

group_artist_model = api.model('GroupArtist', {
    'group_id': fields.String(required=True, description="ID of the group"),
    'artist_id': fields.String(required=True, description="ID of the artist")
})

@group_artist_ns.route('/')
class GroupArtistList(Resource):
    @jwt_required()
    @group_artist_ns.marshal_list_with(group_artist_model)
    def get(self):
        """Get all group-artist relationships"""
        with DBConnection() as connection:
            relationships = connection.execute('SELECT * FROM GroupArtist').fetchall()
            return [dict(rel) for rel in relationships]

    @jwt_required()
    @group_artist_ns.expect(group_artist_model)
    def post(self):
        """Create a new group-artist relationship"""
        data = request.json
        with DBConnection() as connection:
            cursor = connection.cursor()
            # Check if the group exists
            group = cursor.execute('SELECT 1 FROM MusicGroup WHERE group_id = ?', (data['group_id'],)).fetchone()
            if not group:
                return {"message": "Group not found"}, 404
            # Check if the artist exists
            artist = cursor.execute('SELECT 1 FROM Artist WHERE artist_id = ?', (data['artist_id'],)).fetchone()
            if not artist:
                return {"message": "Artist not found"}, 404
            cursor.execute('INSERT INTO GroupArtist (group_id, artist_id) VALUES (?, ?)',
                           (data['group_id'], data['artist_id']))
            return {"message": "Group-artist relationship created successfully"}, 201

api.add_namespace(group_artist_ns)

if __name__ == '__main__':
    init_db()
    insert_dummy_data(DATABASE)
    app.run(debug=True)