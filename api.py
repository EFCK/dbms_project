from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from statements import statements
from dummy_data_insertion import *
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '123'
jwt = JWTManager(app)

api = Api(app, title="SUPERFITY Database API", version="1.0", description="API documentation for the SUPERTIFY database")
DATABASE = 'supertify.db'

@app.before_request
def force_json():
    if request.method in ['POST', 'PUT', 'PATCH'] and not request.content_type:
        # Assume the request is JSON if there's no content-type specified
        request.content_type = 'application/json'

# Initialize database
def init_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for statement in statements:
        cursor.execute(statement)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Authentication (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


# Helper function to get database connection
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

# ---------------------------- Authentication ----------------------------
auth_ns = Namespace('auth', description="Authentication operations")

register_model = api.model('Register', {
    'username': fields.String(required=True, description="The username"),
    'password': fields.String(required=True, description="The password")
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description="The username"),
    'password': fields.String(required=True, description="The password")
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    def post(self):
        """Register a new user"""
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
    @auth_ns.expect(login_model)
    def post(self):
        """Login and get a token"""
        data = request.json
        username = data['username']
        password = data['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        user = cursor.execute("SELECT * FROM Authentication WHERE username = ?", (username,)).fetchone()
        connection.close()
        if user and check_password_hash(user['password'], password):
            token = create_access_token(identity=username)
            return {"access_token": token}, 200
        return {"message": "Invalid credentials"}, 401

# ---------------------------- Example Protected Route ----------------------------
protected_ns = Namespace('protected', description="Protected routes for authenticated users")

@protected_ns.route('/data')
class ProtectedData(Resource):
    @jwt_required()
    def get(self):
        """Example protected data endpoint"""
        current_user = get_jwt_identity()
        return {"message": f"Welcome, {current_user}! This is protected data."}, 200

# Add authentication namespace
api.add_namespace(auth_ns)
api.add_namespace(protected_ns)

# ---------------------------- Account ----------------------------

account_ns = Namespace('accounts', description="Manage accounts")
account_model = api.model('Account', {
    'account_id': fields.String(required=True, description="The account ID"),
    'mail': fields.String(required=True, description="The email address"),
    'full_name': fields.String(description="The full name"),
    'is_subscriber': fields.Boolean(description="Subscription status"),
    'country': fields.String(description="Country"),
    'sex': fields.String(description="Gender"),
    'language': fields.String(required=True, description="Preferred language"),
    'birth_date': fields.String(description="Date of birth (YYYY-MM-DD)")
})

@account_ns.route('/')
class AccountList(Resource):
    @jwt_required()
    @account_ns.marshal_list_with(account_model)
    def get(self):
        """Get all accounts"""
        connection = get_db_connection()
        accounts = connection.execute('SELECT * FROM Account').fetchall()
        connection.close()
        return [dict(account) for account in accounts], 200

    @jwt_required()
    @account_ns.expect(account_model)
    def post(self):
        """Create a new account"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('''INSERT INTO Account (account_id, mail, full_name, is_subscriber, country, sex, language, birth_date)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (data['account_id'], data['mail'], data['full_name'], data.get('is_subscriber', False),
                        data.get('country'), data.get('sex'), data['language'], data.get('birth_date')))
        connection.commit()
        connection.close()
        return {"message": "Account created successfully"}, 201

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
        return dict(account), 200

    @jwt_required()
    @account_ns.expect(account_model)
    def put(self, account_id):
        """Update an account"""
        data = request.json
        connection = get_db_connection()
        connection.execute('''UPDATE Account SET mail = ?, full_name = ?, is_subscriber = ?, country = ?, 
                              sex = ?, language = ?, birth_date = ? WHERE account_id = ?''',
                           (data['mail'], data['full_name'], data.get('is_subscriber', 0), data.get('country'),
                            data['sex'], data['language'], data['birth_date'], account_id))
        connection.commit()
        connection.close()
        return {"message": "Account updated successfully"}, 200

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

user_ns = Namespace('users', description="Manage users")
user_model = api.model('User', {
    'user_id': fields.String(required=True, description="The user ID"),
    'nickname': fields.String(required=True, description="The nickname"),
    'favorite_genre': fields.String(description="Favorite genre"),
    'user_image': fields.String(description="User image encoded in base64 format")
})

@user_ns.route('/')
class UserList(Resource):
    @jwt_required()
    @user_ns.marshal_list_with(user_model)
    def get(self):
        """Get all users"""
        connection = get_db_connection()
        users = connection.execute('SELECT * FROM User').fetchall()
        connection.close()
        return [dict(user) for user in users], 200

    @jwt_required()
    @user_ns.expect(user_model)
    def post(self):
        """Create a new user"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO User (user_id, nickname, favorite_genre, user_image) VALUES (?, ?, ?, ?)',
                       (data['user_id'], data['nickname'], data.get('favorite_genre'), data.get('user_image')))
        connection.commit()
        connection.close()
        return {"message": "User created successfully"}, 201

@user_ns.route('/<string:user_id>')
class User(Resource):
    @jwt_required()
    @user_ns.marshal_with(user_model)
    def get(self, user_id):
        """Get a user by ID"""
        connection = get_db_connection()
        user = connection.execute('SELECT * FROM User WHERE user_id = ?', (user_id,)).fetchone()
        connection.close()
        if user is None:
            return {"message": "User not found"}, 404
        return dict(user), 200

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

api.add_namespace(user_ns)

# ---------------------------- Fallower ----------------------------

fallower_ns = Namespace('followers', description="Manage follower relationships")
fallower_model = api.model('Follower', {
    'user_id_1': fields.String(required=True, description="The ID of the user who is following"),
    'user_id_2': fields.String(required=True, description="The ID of the user being followed")
})

@fallower_ns.route('/')
class FollowerList(Resource):
    @jwt_required()
    @fallower_ns.marshal_list_with(fallower_model)
    def get(self):
        """Get all follower relationships"""
        connection = get_db_connection()
        followers = connection.execute('SELECT * FROM Fallower').fetchall()
        connection.close()
        return [dict(follower) for follower in followers], 200

    @jwt_required()
    @fallower_ns.expect(fallower_model)
    def post(self):
        """Create a new follower relationship"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Fallower (user_id_1, user_id_2) VALUES (?, ?)',
                       (data['user_id_1'], data['user_id_2']))
        connection.commit()
        connection.close()
        return {"message": "Follower relationship created successfully"}, 201

@fallower_ns.route('/<string:user_id_1>/followers/<string:user_id_2>')
class Follower(Resource):
    @jwt_required()
    @fallower_ns.marshal_with(fallower_model)
    def get(self, user_id_1, user_id_2):
        """Get a specific follower relationship"""
        connection = get_db_connection()
        follower = connection.execute(
            'SELECT * FROM Fallower WHERE user_id_1 = ? AND user_id_2 = ?',
            (user_id_1, user_id_2)
        ).fetchone()
        connection.close()
        if follower is None:
            return {"message": "Follower relationship not found"}, 404
        return dict(follower), 200

    @jwt_required()
    def delete(self, user_id_1, user_id_2):
        """Delete a follower relationship"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Fallower WHERE user_id_1 = ? AND user_id_2 = ?', (user_id_1, user_id_2))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "Follower relationship not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "Follower relationship deleted successfully"}, 200

api.add_namespace(fallower_ns)

# ---------------------------- Playlist ----------------------------
playlist_ns = Namespace('playlists', description="Manage playlists")
playlist_model = api.model('Playlist', {
    'playlist_id': fields.Integer(description="The ID of the playlist (autogenerated)"),
    'playlist_name': fields.String(required=True, description="The name of the playlist"),
    'playlist_description': fields.String(description="The description of the playlist"),
    'playlist_image': fields.String(description="Playlist image encoded in base64 format"),
    'creator': fields.String(required=True, description="The user ID of the playlist creator")
})

@playlist_ns.route('/')
class PlaylistList(Resource):
    @jwt_required()
    @playlist_ns.marshal_list_with(playlist_model)
    def get(self):
        """Get all playlists"""
        connection = get_db_connection()
        playlists = connection.execute('SELECT * FROM Playlist').fetchall()
        connection.close()
        return [dict(playlist) for playlist in playlists], 200

    @jwt_required()
    @playlist_ns.expect(playlist_model)
    def post(self):
        """Create a new playlist"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Playlist (playlist_name, playlist_description, playlist_image, creator) VALUES (?, ?, ?, ?)',
                       (data['playlist_name'], data.get('playlist_description'), data.get('playlist_image'), data['creator']))
        connection.commit()
        connection.close()
        return {"message": "Playlist created successfully"}, 201

@playlist_ns.route('/<int:playlist_id>')
class Playlist(Resource):
    @jwt_required()
    @playlist_ns.marshal_with(playlist_model)
    def get(self, playlist_id):
        """Get a playlist by ID"""
        connection = get_db_connection()
        playlist = connection.execute('SELECT * FROM Playlist WHERE playlist_id = ?', (playlist_id,)).fetchone()
        connection.close()
        if playlist is None:
            return {"message": "Playlist not found"}, 404
        return dict(playlist), 200

    @jwt_required()
    @playlist_ns.expect(playlist_model)
    def put(self, playlist_id):
        """Update a playlist"""
        data = request.json
        connection = get_db_connection()
        connection.execute('UPDATE Playlist SET playlist_name = ?, playlist_description = ?, playlist_image = ?, creator = ? WHERE playlist_id = ?',
                           (data['playlist_name'], data.get('playlist_description'), data.get('playlist_image'), data['creator'], playlist_id))
        connection.commit()
        connection.close()
        return {"message": "Playlist updated successfully"}, 200

    @jwt_required()
    def delete(self, playlist_id):
        """Delete a playlist"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Playlist WHERE playlist_id = ?', (playlist_id,))
        connection.commit()
        connection.close()
        return {"message": "Playlist deleted successfully"}, 200

api.add_namespace(playlist_ns)

# ---------------------------- Playlist_User ----------------------------

playlist_user_ns = Namespace('playlist_users', description="Manage playlist-user relationships")
playlist_user_model = api.model('PlaylistUser', {
    'user': fields.String(required=True, description="The user ID"),
    'fallows': fields.Integer(required=True, description="The playlist ID")
})

@playlist_user_ns.route('/')
class PlaylistUserList(Resource):
    @jwt_required()
    @playlist_user_ns.marshal_list_with(playlist_user_model)
    def get(self):
        """Get all playlist-user relationships"""
        connection = get_db_connection()
        playlist_users = connection.execute('SELECT * FROM Playlist_User').fetchall()
        connection.close()
        return [dict(playlist_user) for playlist_user in playlist_users], 200

    @jwt_required()
    @playlist_user_ns.expect(playlist_user_model)
    def post(self):
        """Create a new playlist-user relationship"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Playlist_User (user, fallows) VALUES (?, ?)',
                       (data['user'], data['fallows']))
        connection.commit()
        connection.close()
        return {"message": "Playlist-User relationship created successfully"}, 201

@playlist_user_ns.route('/<string:user>/<int:fallows>')
class PlaylistUser(Resource):
    @jwt_required()
    @playlist_user_ns.marshal_with(playlist_user_model)
    def get(self, user, fallows):
        """Get a specific playlist-user relationship"""
        connection = get_db_connection()
        playlist_user = connection.execute('SELECT * FROM Playlist_User WHERE user = ? AND fallows = ?', (user, fallows)).fetchone()
        connection.close()
        if playlist_user is None:
            return {"message": "Playlist-User relationship not found"}, 404
        return dict(playlist_user), 200

    @jwt_required()
    def delete(self, user, fallows):
        """Delete a playlist-user relationship"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Playlist_User WHERE user = ? AND fallows = ?', (user, fallows))
        connection.commit()
        connection.close()
        return {"message": "Playlist-User relationship deleted successfully"}, 200

api.add_namespace(playlist_user_ns)

# ---------------------------- Playlist_Song ----------------------------

playlist_song_ns = Namespace('playlist_songs', description="Manage playlist-song relationships")
playlist_song_model = api.model('PlaylistSong', {
    'playlist_id': fields.Integer(required=True, description="The playlist ID"),
    'song_id': fields.String(required=True, description="The song ID")
})

@playlist_song_ns.route('/')
class PlaylistSongList(Resource):
    @playlist_song_ns.marshal_list_with(playlist_song_model)
    @jwt_required()
    def get(self):
        """Get all playlist-song relationships"""
        connection = get_db_connection()
        playlist_songs = connection.execute('SELECT * FROM Playlist_Song').fetchall()
        connection.close()
        return [dict(playlist_song) for playlist_song in playlist_songs], 200

    @jwt_required()
    @playlist_song_ns.expect(playlist_song_model)
    def post(self):
        """Create a new playlist-song relationship"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Playlist_Song (playlist_id, song_id) VALUES (?, ?)',
                       (data['playlist_id'], data['song_id']))
        connection.commit()
        connection.close()
        return {"message": "Playlist-Song relationship created successfully"}, 201

@playlist_song_ns.route('/<int:playlist_id>/songs/<string:song_id>')
class PlaylistSong(Resource):
    @playlist_song_ns.marshal_with(playlist_song_model)
    def get(self, playlist_id, song_id):
        """Get a specific playlist-song relationship"""
        connection = get_db_connection()
        playlist_song = connection.execute('SELECT * FROM Playlist_Song WHERE playlist_id = ? AND song_id = ?', (playlist_id, song_id)).fetchone()
        connection.close()
        if playlist_song is None:
            return {"message": "Playlist-Song relationship not found"}, 404
        return dict(playlist_song), 200

    def delete(self, playlist_id, song_id):
        """Delete a playlist-song relationship"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Playlist_Song WHERE playlist_id = ? AND song_id = ?', (playlist_id, song_id))
        connection.commit()
        connection.close()
        return {"message": "Playlist-Song relationship deleted successfully"}, 200

api.add_namespace(playlist_song_ns)

# ---------------------------- Like ----------------------------

like_ns = Namespace('likes', description="Manage likes for songs")
like_model = api.model('Like', {
    'user_id': fields.String(required=True, description="The ID of the user liking the song"),
    'song_id': fields.String(required=True, description="The ID of the liked song")
})

@like_ns.route('/')
class LikeList(Resource):
    @like_ns.marshal_list_with(like_model)
    def get(self):
        """Get all likes"""
        connection = get_db_connection()
        likes = connection.execute('SELECT * FROM Like').fetchall()
        connection.close()
        return [dict(like) for like in likes], 200

    @like_ns.expect(like_model)
    def post(self):
        """Create a new like"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Like (user_id, song_id) VALUES (?, ?)',
                       (data['user_id'], data['song_id']))
        connection.commit()
        connection.close()
        return {"message": "Like created successfully"}, 201

@like_ns.route('/<string:user_id>/songs/<string:song_id>')
class Like(Resource):
    @like_ns.marshal_with(like_model)
    def get(self, user_id, song_id):
        """Get a specific like"""
        connection = get_db_connection()
        like = connection.execute(
            'SELECT * FROM Like WHERE user_id = ? AND song_id = ?',
            (user_id, song_id)
        ).fetchone()
        connection.close()
        if like is None:
            return {"message": "Like not found"}, 404
        return dict(like), 200

    def delete(self, user_id, song_id):
        """Delete a like"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Like WHERE user_id = ? AND song_id = ?', (user_id, song_id))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "Like not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "Like deleted successfully"}, 200

api.add_namespace(like_ns)

# ---------------------------- Song ----------------------------

song_ns = Namespace('songs', description="Manage songs")
song_model = api.model('Song', {
    'song_id': fields.String(required=True, description="The ID of the song"),
    'song_name': fields.String(required=True, description="The name of the song"),
    'song_time': fields.String(required=True, description="The duration of the song"),
    'song_image': fields.String(description="Song image encoded in base64 format"),
    'audio': fields.String(description="Audio file encoded in base64 format")
})

@song_ns.route('/')
class SongList(Resource):
    @song_ns.marshal_list_with(song_model)
    def get(self):
        """Get all songs"""
        connection = get_db_connection()
        songs = connection.execute('SELECT * FROM Song').fetchall()
        connection.close()
        return [dict(song) for song in songs], 200

    @song_ns.expect(song_model)
    def post(self):
        """Create a new song"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Song (song_id, song_name, song_time, song_image, audio) VALUES (?, ?, ?, ?, ?)',
                       (data['song_id'], data['song_name'], data['song_time'], data.get('song_image'), data.get('audio')))
        connection.commit()
        connection.close()
        return {"message": "Song created successfully"}, 201

@song_ns.route('/<string:song_id>')
class Song(Resource):
    @song_ns.marshal_with(song_model)
    def get(self, song_id):
        """Get a song by ID"""
        connection = get_db_connection()
        song = connection.execute('SELECT * FROM Song WHERE song_id = ?', (song_id,)).fetchone()
        connection.close()
        if song is None:
            return {"message": "Song not found"}, 404
        return dict(song), 200

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

    def delete(self, song_id):
        """Delete a song"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Song WHERE song_id = ?', (song_id,))
        connection.commit()
        connection.close()
        return {"message": "Song deleted successfully"}, 200

api.add_namespace(song_ns)

# ---------------------------- Genre ----------------------------

genre_ns = Namespace('genres', description="Manage genres")
genre_model = api.model('Genre', {
    'song_id': fields.String(required=True, description="The ID of the song"),
    'genre': fields.String(required=True, description="The genre of the song")
})

@genre_ns.route('/')
class GenreList(Resource):
    @genre_ns.marshal_list_with(genre_model)
    def get(self):
        """Get all genres"""
        connection = get_db_connection()
        genres = connection.execute('SELECT * FROM Genre').fetchall()
        connection.close()
        return [dict(genre) for genre in genres], 200

    @genre_ns.expect(genre_model)
    def post(self):
        """Create a new genre"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Genre (song_id, genre) VALUES (?, ?)',
                       (data['song_id'], data['genre']))
        connection.commit()
        connection.close()
        return {"message": "Genre created successfully"}, 201

@genre_ns.route('/<string:song_id>')
class Genre(Resource):
    @genre_ns.marshal_with(genre_model)
    def get(self, song_id):
        """Get a genre by song ID"""
        connection = get_db_connection()
        genre = connection.execute('SELECT * FROM Genre WHERE song_id = ?', (song_id,)).fetchone()
        connection.close()
        if genre is None:
            return {"message": "Genre not found"}, 404
        return dict(genre), 200

    def delete(self, song_id):
        """Delete a genre"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Genre WHERE song_id = ?', (song_id,))
        connection.commit()
        connection.close()
        return {"message": "Genre deleted successfully"}, 200

api.add_namespace(genre_ns)

# ---------------------------- Album ----------------------------

album_ns = Namespace('albums', description="Manage albums")
album_model = api.model('Album', {
    'album_id': fields.String(required=True, description="The ID of the album"),
    'album_name': fields.String(required=True, description="The name of the album"),
    'about': fields.String(description="Details about the album"),
    'album_image': fields.String(description="Album image encoded in base64 format")
})

@album_ns.route('/')
class AlbumList(Resource):
    @album_ns.marshal_list_with(album_model)
    def get(self):
        """Get all albums"""
        connection = get_db_connection()
        albums = connection.execute('SELECT * FROM Album').fetchall()
        connection.close()
        return [dict(album) for album in albums], 200

    @album_ns.expect(album_model)
    def post(self):
        """Create a new album"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Album (album_id, album_name, about, album_image) VALUES (?, ?, ?, ?)',
                       (data['album_id'], data['album_name'], data.get('about'), data.get('album_image')))
        connection.commit()
        connection.close()
        return {"message": "Album created successfully"}, 201

@album_ns.route('/<string:album_id>')
class Album(Resource):
    @album_ns.marshal_with(album_model)
    def get(self, album_id):
        """Get an album by ID"""
        connection = get_db_connection()
        album = connection.execute('SELECT * FROM Album WHERE album_id = ?', (album_id,)).fetchone()
        connection.close()
        if album is None:
            return {"message": "Album not found"}, 404
        return dict(album), 200

    @album_ns.expect(album_model)
    def put(self, album_id):
        """Update an album"""
        data = request.json
        connection = get_db_connection()
        connection.execute('UPDATE Album SET album_name = ?, about = ?, album_image = ? WHERE album_id = ?',
                           (data['album_name'], data.get('about'), data.get('album_image'), album_id))
        connection.commit()
        connection.close()
        return {"message": "Album updated successfully"}, 200

    def delete(self, album_id):
        """Delete an album"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Album WHERE album_id = ?', (album_id,))
        connection.commit()
        connection.close()
        return {"message": "Album deleted successfully"}, 200

api.add_namespace(album_ns)

# ---------------------------- Album_Info ----------------------------

album_info_ns = Namespace('album_info', description="Manage relationships between albums and songs")
album_info_model = api.model('AlbumInfo', {
    'album_id': fields.String(required=True, description="The ID of the album"),
    'song_id': fields.String(required=True, description="The ID of the song")
})

@album_info_ns.route('/')
class AlbumInfoList(Resource):
    @album_info_ns.marshal_list_with(album_info_model)
    def get(self):
        """Get all album-song relationships"""
        connection = get_db_connection()
        album_infos = connection.execute('SELECT * FROM Album_Info').fetchall()
        connection.close()
        return [dict(album_info) for album_info in album_infos], 200

    @album_info_ns.expect(album_info_model)
    def post(self):
        """Create a new album-song relationship"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Album_Info (album_id, song_id) VALUES (?, ?)',
                       (data['album_id'], data['song_id']))
        connection.commit()
        connection.close()
        return {"message": "Album-Song relationship created successfully"}, 201

@album_info_ns.route('/<string:album_id>/songs/<string:song_id>')
class AlbumInfo(Resource):
    @album_info_ns.marshal_with(album_info_model)
    def get(self, album_id, song_id):
        """Get a specific album-song relationship"""
        connection = get_db_connection()
        album_info = connection.execute('SELECT * FROM Album_Info WHERE album_id = ? AND song_id = ?',
                                        (album_id, song_id)).fetchone()
        connection.close()
        if album_info is None:
            return {"message": "Album-Song relationship not found"}, 404
        return dict(album_info), 200

    def delete(self, album_id, song_id):
        """Delete an album-song relationship"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Album_Info WHERE album_id = ? AND song_id = ?', (album_id, song_id))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "Album-Song relationship not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "Album-Song relationship deleted successfully"}, 200

api.add_namespace(album_info_ns)

# ---------------------------- Group ----------------------------

group_ns = Namespace('groups', description="Manage groups")
group_model = api.model('Group', {
    'group_id': fields.String(required=True, description="The ID of the group"),
    'group_name': fields.String(required=True, description="The name of the group"),
    'number_of_members': fields.Integer(description="The number of members in the group"),
    'creation_date': fields.String(description="The creation date of the group (YYYY-MM-DD)"),
    'group_image': fields.String(description="Group image encoded in base64 format")
})

@group_ns.route('/')
class GroupList(Resource):
    @group_ns.marshal_list_with(group_model)
    def get(self):
        """Get all groups"""
        connection = get_db_connection()
        groups = connection.execute('SELECT * FROM `Group`').fetchall()
        connection.close()
        return [dict(group) for group in groups], 200

    @group_ns.expect(group_model)
    def post(self):
        """Create a new group"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO `Group` (group_id, group_name, number_of_members, creation_date, group_image) VALUES (?, ?, ?, ?, ?)',
                       (data['group_id'], data['group_name'], data.get('number_of_members'),
                        data.get('creation_date'), data.get('group_image')))
        connection.commit()
        connection.close()
        return {"message": "Group created successfully"}, 201

@group_ns.route('/<string:group_id>')
class Group(Resource):
    @group_ns.marshal_with(group_model)
    def get(self, group_id):
        """Get a group by ID"""
        connection = get_db_connection()
        group = connection.execute('SELECT * FROM `Group` WHERE group_id = ?', (group_id,)).fetchone()
        connection.close()
        if group is None:
            return {"message": "Group not found"}, 404
        return dict(group), 200

    @group_ns.expect(group_model)
    def put(self, group_id):
        """Update a group"""
        data = request.json
        connection = get_db_connection()
        connection.execute('UPDATE `Group` SET group_name = ?, number_of_members = ?, creation_date = ?, group_image = ? WHERE group_id = ?',
                           (data['group_name'], data.get('number_of_members'), data.get('creation_date'), data.get('group_image'), group_id))
        connection.commit()
        connection.close()
        return {"message": "Group updated successfully"}, 200

    def delete(self, group_id):
        """Delete a group"""
        connection = get_db_connection()
        connection.execute('DELETE FROM `Group` WHERE group_id = ?', (group_id,))
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
    @album_group_ns.marshal_list_with(album_group_model)
    def get(self):
        """Get all album-group relationships"""
        connection = get_db_connection()
        album_groups = connection.execute('SELECT * FROM Album_Group').fetchall()
        connection.close()
        return [dict(album_group) for album_group in album_groups], 200

    @album_group_ns.expect(album_group_model)
    def post(self):
        """Create a new album-group relationship"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Album_Group (album_id, group_id) VALUES (?, ?)',
                       (data['album_id'], data['group_id']))
        connection.commit()
        connection.close()
        return {"message": "Album-Group relationship created successfully"}, 201

@album_group_ns.route('/<string:album_id>/groups/<string:group_id>')
class AlbumGroup(Resource):
    @album_group_ns.marshal_with(album_group_model)
    def get(self, album_id, group_id):
        """Get a specific album-group relationship"""
        connection = get_db_connection()
        album_group = connection.execute('SELECT * FROM Album_Group WHERE album_id = ? AND group_id = ?',
                                         (album_id, group_id)).fetchone()
        connection.close()
        if album_group is None:
            return {"message": "Album-Group relationship not found"}, 404
        return dict(album_group), 200

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
    'group_id': fields.String(required=True, description="The ID of the group"),
    'full_name': fields.String(required=True, description="The full name of the artist")
})

@artist_ns.route('/')
class ArtistList(Resource):
    @artist_ns.marshal_list_with(artist_model)
    def get(self):
        """Get all artists"""
        connection = get_db_connection()
        artists = connection.execute('SELECT * FROM Artist').fetchall()
        connection.close()
        return [dict(artist) for artist in artists], 200

    @artist_ns.expect(artist_model)
    def post(self):
        """Create a new artist"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Artist (group_id, full_name) VALUES (?, ?)',
                       (data['group_id'], data['full_name']))
        connection.commit()
        connection.close()
        return {"message": "Artist created successfully"}, 201

@artist_ns.route('/<string:group_id>/artists/<string:full_name>')
class Artist(Resource):
    @artist_ns.marshal_with(artist_model)
    def get(self, group_id, full_name):
        """Get an artist by group ID and name"""
        connection = get_db_connection()
        artist = connection.execute('SELECT * FROM Artist WHERE group_id = ? AND full_name = ?',
                                    (group_id, full_name)).fetchone()
        connection.close()
        if artist is None:
            return {"message": "Artist not found"}, 404
        return dict(artist), 200

    def delete(self, group_id, full_name):
        """Delete an artist"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Artist WHERE group_id = ? AND full_name = ?', (group_id, full_name))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "Artist not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "Artist deleted successfully"}, 200

api.add_namespace(artist_ns)

# ---------------------------- History ----------------------------

history_ns = Namespace('history', description="Manage user listening history")
history_model = api.model('History', {
    'user_id': fields.String(required=True, description="The ID of the user"),
    'start_time': fields.String(required=True, description="The start time of the listening session"),
    'duration': fields.String(description="The duration of the session"),
    'song': fields.String(required=True, description="The ID of the song")
})

@history_ns.route('/')
class HistoryList(Resource):
    @history_ns.marshal_list_with(history_model)
    def get(self):
        """Get all history records"""
        connection = get_db_connection()
        history_records = connection.execute('SELECT * FROM History').fetchall()
        connection.close()
        return [dict(history) for history in history_records], 200

    @history_ns.expect(history_model)
    def post(self):
        """Create a new history record"""
        data = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO History (user_id, start_time, duration, song) VALUES (?, ?, ?, ?)',
                       (data['user_id'], data['start_time'], data.get('duration'), data['song']))
        connection.commit()
        connection.close()
        return {"message": "History record created successfully"}, 201

@history_ns.route('/<string:user_id>/history/<string:start_time>')
class History(Resource):
    @history_ns.marshal_with(history_model)
    def get(self, user_id, start_time):
        """Get a specific history record"""
        connection = get_db_connection()
        history = connection.execute('SELECT * FROM History WHERE user_id = ? AND start_time = ?',
                                     (user_id, start_time)).fetchone()
        connection.close()
        if history is None:
            return {"message": "History record not found"}, 404
        return dict(history), 200

    def delete(self, user_id, start_time):
        """Delete a history record"""
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM History WHERE user_id = ? AND start_time = ?', (user_id, start_time))
        if cursor.rowcount == 0:
            connection.close()
            return {"message": "History record not found"}, 404
        connection.commit()
        connection.close()
        return {"message": "History record deleted successfully"}, 200

api.add_namespace(history_ns)

# add dummy data
insert_dummy_data(DATABASE)
#insert_dummy_user_data(DATABASE)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
