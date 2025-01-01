statements = [
    """CREATE TABLE IF NOT EXISTS Account(
        account_id CHAR(24) PRIMARY KEY,
        mail VARCHAR(50) NOT NULL UNIQUE,
        full_name VARCHAR(50),
        is_subscriber BOOL NOT NULL DEFAULT False,
        registiration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        country VARCHAR(50),
        sex VARCHAR(50),
        language VARCHAR(50) NOT NULL,
        birth_date DATE
    )""",
    """CREATE TABLE IF NOT EXISTS User(
        user_id CHAR(24) PRIMARY KEY,
        nickname VARCHAR(50) NOT NULL,
        favorite_genre VARCHAR(50),
        user_image BLOB
    )""",
    """CREATE TABLE IF NOT EXISTS Follower(
        user_id_1 CHAR(24),
        user_id_2 CHAR(24),
        PRIMARY KEY (user_id_1, user_id_2),
        FOREIGN KEY (user_id_1) REFERENCES User (user_id),
        FOREIGN KEY (user_id_2) REFERENCES User (user_id)
    )""",
    """CREATE TABLE IF NOT EXISTS Playlist(
        playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_name VARCHAR(50) NOT NULL,
        playlist_description VARCHAR(300),
        playlist_image BLOB,
        creator CHAR(24),
        FOREIGN KEY (creator) REFERENCES User (user_id)
    )""",
        """CREATE TABLE IF NOT EXISTS Song(
        song_id CHAR(16) PRIMARY KEY,
        song_name VARCHAR(50) NOT NULL,
        song_time INT NOT NULL,
        song_image BLOB,
        audio BLOB
    )""",
    """CREATE TABLE IF NOT EXISTS Playlist_User(
        user CHAR(24),
        fallows INT,
        PRIMARY KEY (user, fallows),
        FOREIGN KEY (user) REFERENCES User (user_id),
        FOREIGN KEY (fallows) REFERENCES Playlist (playlist_id)
    )""",
    """CREATE TABLE IF NOT EXISTS Playlist_Song(
        playlist_id INT,
        song_id CHAR(16),
        PRIMARY KEY (playlist_id, song_id),
        FOREIGN KEY (playlist_id) REFERENCES Playlist (playlist_id),
        FOREIGN KEY (song_id) REFERENCES Song (song_id)
    )""",
    """CREATE TABLE IF NOT EXISTS 'Like'(
        user_id CHAR(24),
        song_id CHAR(16),
        PRIMARY KEY (user_id, song_id),
        FOREIGN KEY (user_id) REFERENCES User (user_id),
        FOREIGN KEY (song_id) REFERENCES Song (song_id)
    )""",
    """CREATE TABLE IF NOT EXISTS Genre(
        song_id CHAR(16) PRIMARY KEY,
        genre VARCHAR(50),
        FOREIGN KEY (song_id) REFERENCES Song (song_id)
    )""",
    """CREATE TABLE IF NOT EXISTS Album(
        album_id CHAR(24) PRIMARY KEY,
        album_name VARCHAR(50) NOT NULL UNIQUE,
        about VARCHAR(250),
        album_image BLOB
    )""",
    """CREATE TABLE IF NOT EXISTS Album_Info(
        album_id CHAR(16),
        song_id CHAR(16),
        PRIMARY KEY (album_id, song_id),
        FOREIGN KEY (album_id) REFERENCES Album (album_id),
        FOREIGN KEY (song_id) REFERENCES Song (song_id)
    )""",
    """CREATE TABLE IF NOT EXISTS 'Group'(
        group_id CHAR(16) PRIMARY KEY,
        group_name VARCHAR(50) NOT NULL UNIQUE,
        number_of_members INT,
        creation_date DATE,
        group_image BLOB
    )""",
    """CREATE TABLE IF NOT EXISTS Artist(
        group_id CHAR(16),
        full_name VARCHAR(50),
        PRIMARY KEY (group_id, full_name),
        FOREIGN KEY (group_id) REFERENCES `Group` (group_id)
    )""",
    """CREATE TABLE IF NOT EXISTS Album_Group(
        album_id CHAR(16),
        group_id CHAR(16),
        PRIMARY KEY (album_id, group_id),
        FOREIGN KEY (album_id) REFERENCES Album (album_id),
        FOREIGN KEY (group_id) REFERENCES `Group` (group_id)
    )""",
    """CREATE TABLE IF NOT EXISTS History(
        user_id CHAR(24),
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        duration INT,
        song CHAR(16),
        PRIMARY KEY (user_id, start_time),
        FOREIGN KEY (user_id) REFERENCES User (user_id),
        FOREIGN KEY (song) REFERENCES Song (song_id)
    )"""
]
