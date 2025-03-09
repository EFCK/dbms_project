uuid_default = (
    "lower(hex(randomblob(4))) || '-' || "
    "lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || "
    "substr('89ab', abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || "
    "lower(hex(randomblob(6)))"
)

statements = [
    # Account table and its indexes (created first)
    f"""CREATE TABLE IF NOT EXISTS Account (
        account_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        mail VARCHAR(50) NOT NULL UNIQUE CHECK (mail LIKE '%_@_%.__%'),
        password_hash CHAR(60) NOT NULL,
        password_salt CHAR(29) NOT NULL,
        full_name VARCHAR(50) CHECK (length(full_name) >= 2),
        is_subscriber INTEGER NOT NULL DEFAULT 0 CHECK (is_subscriber IN (0, 1)),
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        country VARCHAR(50),
        sex VARCHAR(50) CHECK (sex IN ('Male', 'Female', 'Other', 'Prefer not to say')),
        language VARCHAR(50) NOT NULL,
        birth_date DATE CHECK (birth_date <= CURRENT_DATE AND birth_date >= '1900-01-01'),
        last_login DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE INDEX IF NOT EXISTS idx_account_mail ON Account(mail)""",
    """CREATE INDEX IF NOT EXISTS idx_account_registration ON Account(registration_date)""",

    # User table and its index (references Account)
    f"""CREATE TABLE IF NOT EXISTS User (
        user_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        nickname VARCHAR(50) NOT NULL CHECK (length(nickname) >= 3),
        favorite_genre VARCHAR(50),
        user_image BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Account(account_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",
    """CREATE INDEX IF NOT EXISTS idx_user_nickname ON User(nickname)""",

    # Follower table and its indexes
    """CREATE TABLE IF NOT EXISTS Follower (
        user_id_1 CHAR(36),
        user_id_2 CHAR(36),
        followed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id_1, user_id_2),
        FOREIGN KEY (user_id_1) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (user_id_2) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
        CHECK (user_id_1 != user_id_2)
    )""",
    """CREATE INDEX IF NOT EXISTS idx_follower_user1 ON Follower(user_id_1)""",
    """CREATE INDEX IF NOT EXISTS idx_follower_user2 ON Follower(user_id_2)""",

    # Playlist table and its indexes
    f"""CREATE TABLE IF NOT EXISTS Playlist (
        playlist_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        playlist_name VARCHAR(50) NOT NULL CHECK (length(playlist_name) > 0),
        playlist_description VARCHAR(300),
        playlist_image BLOB,
        creator_id CHAR(36),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (creator_id) REFERENCES User(user_id) ON DELETE SET NULL ON UPDATE CASCADE
    )""",
    """CREATE INDEX IF NOT EXISTS idx_playlist_creator_id ON Playlist(creator_id)""",
    """CREATE INDEX IF NOT EXISTS idx_playlist_name ON Playlist(playlist_name)""",

    # Song table and its index
    f"""CREATE TABLE IF NOT EXISTS Song (
        song_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        song_name VARCHAR(50) NOT NULL CHECK (length(song_name) > 0),
        song_time INTEGER NOT NULL CHECK (song_time > 0 AND song_time <= 7200), -- Duration in seconds (max 2 hours)
        song_image BLOB,
        audio BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE INDEX IF NOT EXISTS idx_song_name ON Song(song_name)""",

    # Playlist_User table
    """CREATE TABLE IF NOT EXISTS Playlist_User (
        user_id CHAR(36),
        playlist_id CHAR(36),
        followed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, playlist_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",

    # Playlist_Song table
    """CREATE TABLE IF NOT EXISTS Playlist_Song (
        playlist_id CHAR(36),
        song_id CHAR(36),
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (playlist_id, song_id),
        FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",

    # UserLikes table and its index
    """CREATE TABLE IF NOT EXISTS UserLikes (
        user_id CHAR(36),
        song_id CHAR(36),
        liked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, song_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",
    """CREATE INDEX IF NOT EXISTS idx_user_likes_user_id ON UserLikes(user_id)""",

    # Genre table
    f"""CREATE TABLE IF NOT EXISTS Genre (
        song_id CHAR(36) NOT NULL,
        genre_id INTEGER NOT NULL,
        PRIMARY KEY (song_id, genre_id),
        FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (genre_id) REFERENCES GenreFields(genre_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",
    """CREATE INDEX IF NOT EXISTS idx_genre_song_id ON Genre(song_id)""",
    


    # Album table and its indexes
    f"""CREATE TABLE IF NOT EXISTS Album (
        album_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        album_name VARCHAR(50) NOT NULL UNIQUE CHECK (length(album_name) > 0),
        about VARCHAR(250),
        album_image BLOB,
        release_date DATE DEFAULT CURRENT_DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE INDEX IF NOT EXISTS idx_album_name ON Album(album_name)""",
    """CREATE INDEX IF NOT EXISTS idx_album_release_date ON Album(release_date)""",

    # Album_Info table
    """CREATE TABLE IF NOT EXISTS Album_Info (
        album_id CHAR(36),
        song_id CHAR(36),
        track_number INTEGER CHECK (track_number > 0),
        PRIMARY KEY (album_id, song_id),
        FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",

    # MusicGroup table and its index
    f"""CREATE TABLE IF NOT EXISTS MusicGroup (
        group_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        group_name VARCHAR(50) NOT NULL UNIQUE CHECK (length(group_name) > 0),
        number_of_members INTEGER CHECK (number_of_members > 0),
        creation_date DATE,
        group_image BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE INDEX IF NOT EXISTS idx_music_group_name ON MusicGroup(group_name)""",

    # Artist table
    f"""CREATE TABLE IF NOT EXISTS Artist (
        artist_id CHAR(36) PRIMARY KEY DEFAULT ({uuid_default}),
        full_name VARCHAR(50) CHECK (length(full_name) >= 2),
        origin_country VARCHAR(50),
        instrument VARCHAR(50)
    )""",

    # Album_Group table
    """CREATE TABLE IF NOT EXISTS Album_Group (
        album_id CHAR(36),
        group_id CHAR(36),
        PRIMARY KEY (album_id, group_id),
        FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (group_id) REFERENCES MusicGroup(group_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",

    # History table and its indexes
    """CREATE TABLE IF NOT EXISTS History (
        user_id CHAR(36),
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        duration INTEGER CHECK (duration > 0),
        song_id CHAR(36),
        PRIMARY KEY (user_id, start_time),
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (song_id) REFERENCES Song(song_id) ON DELETE CASCADE ON UPDATE CASCADE
    )""",
    """CREATE INDEX IF NOT EXISTS idx_history_user_id ON History(user_id)""",
    """CREATE INDEX IF NOT EXISTS idx_history_start_time ON History(start_time)""",

    # GenreFields table
    """CREATE TABLE IF NOT EXISTS GenreFields (
        genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
        genre_name VARCHAR(50) NOT NULL CHECK (length(genre_name) > 0)
    )""",

    # GroupArtist table
    """CREATE TABLE IF NOT EXISTS GroupArtist (
        group_id CHAR(36),
        artist_id CHAR(36),
        PRIMARY KEY (group_id, artist_id),
        FOREIGN KEY (group_id) REFERENCES MusicGroup(group_id) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (artist_id) REFERENCES Artist(artist_id) ON DELETE CASCADE ON UPDATE CASCADE
    )"""
]
