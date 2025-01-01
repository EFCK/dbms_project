import sqlite3

def insert_dummy_data(DATABASE):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        # Insert dummy data into the Account table
        cursor.execute("""
            INSERT INTO Account (account_id, mail, full_name, is_subscriber, registiration_date, country, sex, language, birth_date) VALUES
            ('41T70U4BZZQGZFNXKXNQ8ZYT', 'tuncerservice@gmail.com', 'Mahmut Tuncer', 1, '2021-05-01', 'Turkey', 'male', 'Turkish', '1961-05-05'),
            ('64KZGKHPS2HIOVRCN0ERNG28', 'mathematics@hotmail.com', 'Pisagor Pisagor', 0, '2021-05-01', 'Grace', 'male', 'English', '450-01-01'),
            ('87A0V0LUU5794LVQF34J25FM', 'krbykefecan@gmail.com', 'Efe Can kirbiyik', 1, '2021-05-01', 'Turkey', 'male', 'Turkish', '2001-12-12'),
            ('1A1SBQP9W8Y1J195HFVARMJR', 'imbatman@gmail.com', 'Bruce Wayne', 0, '2021-05-01', 'USA', 'attack helicopter', 'English', '1939-05-05'),
            ('3DSJQ63NOBPTYRDJKIM27CX6', 'random4@gmail.com', 'Random Person 3', 0, '2021-05-01', 'Canada', 'female', 'English', '1990-01-01'),
            ('5GJLFW72REGUEHQOCL33MS1K', 'kojimaint@gmail.com', 'Hideo Kojima', 1, '2021-05-01', 'Japan', 'alpha male', 'Japanese', '1963-08-24'),
            ('YJ0CUDKGTHXMTXU3EPUV1IEZ', 'adcarry@hotmail.com', 'miss fortune', 1, '2021-05-01', 'Runeterra', 'female', 'English', '1996-02-21'),
            ('0MR4A2OLLKODINYHGSLNHYI3', 'zerotwo@gmail.com', 'Zero Zero Two', 1, '2021-05-01', 'Klaxosaur', 'female', 'Japanese', '2000-02-02'),
            ('2PIWPJSZONEFX3CV9VBOWOMI', 'rockson@gmail.com', 'Dost Kayaoğlu', 1, '2021-05-01', 'Turkey', 'male', 'Turkish', '1999-01-01'),
            ('VT8X496EQQ56DTG0BY2FLE0W', '800kmidsal@gmail.com', 'Fatih Ucubeoğlu', 0, '2021-05-01', 'Turkey', 'minion', 'Turkish', '2015-01-01') 
        """)
        connection.commit()
        # Insert dummy data into the User table
        cursor.execute("""
            INSERT INTO User (user_id, nickname, favorite_genre, user_image) VALUES
            ('41T70U4BZZQGZFNXKXNQ8ZYT', 'Tunceredits', 'Pop', NULL),
            ('64KZGKHPS2HIOVRCN0ERNG28', '345math', 'Rock', NULL),
            ('87A0V0LUU5794LVQF34J25FM', 'EFCK', 'Jazz', NULL),
            ('1A1SBQP9W8Y1J195HFVARMJR', 'Batman', 'Rock', NULL),
            ('3DSJQ63NOBPTYRDJKIM27CX6', 'Charlie', 'Pop', NULL),
            ('5GJLFW72REGUEHQOCL33MS1K', 'mgs6', 'Jazz', NULL),
            ('YJ0CUDKGTHXMTXU3EPUV1IEZ', 'infinityedge', 'Rock', NULL),
            ('0MR4A2OLLKODINYHGSLNHYI3', 'franxx', 'Pop', NULL),
            ('2PIWPJSZONEFX3CV9VBOWOMI', 'rockson', 'Jazz', NULL),
            ('VT8X496EQQ56DTG0BY2FLE0W', '800kmid', 'Rap', NULL)
        """)
        connection.commit()
        # Insert dummy data into the Fallower table
        # cursor.execute("""
        #     INSERT INTO Follower (user_id_1, user_id_2) VALUES
        #     ('41T70U4BZZQGZFNXKXNQ8ZYT', '64KZGKHPS2HIOVRCN0ERNG28'),
        #     ('41T70U4BZZQGZFNXKXNQ8ZYT', '87A0V0LUU5794LVQF34J25FM'),
        #     ('64KZGKHPS2HIOVRCN0ERNG28', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('87A0V0LUU5794LVQF34J25FM', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('1A1SBQP9W8Y1J195HFVARMJR', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('3DSJQ63NOBPTYRDJKIM27CX6', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('5GJLFW72REGUEHQOCL33MS1K', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('YJ0CUDKGTHXMTXU3EPUV1IEZ', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('0MR4A2OLLKODINYHGSLNHYI3', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('2PIWPJSZONEFX3CV9VBOWOMI', '41T70U4BZZQGZFNXKXNQ8ZYT'),
        #     ('VT8X496EQQ56DTG0BY2FLE0W', '41T70U4BZZQGZFNXKXNQ8ZYT')
        # """)
        # Insert dummy data into the Playlist table
        cursor.execute("""
            INSERT INTO Playlist (playlist_id, playlist_name, playlist_description, playlist_image, creator) VALUES
            (1, 'AGLAMA GARANTILI KARISIK', 'A playlist of popular rock songs', NULL, '41T70U4BZZQGZFNXKXNQ8ZYT'),
            (2, 'Lofi', 'Studentdying musics', NULL, '64KZGKHPS2HIOVRCN0ERNG28'),
            (3, 'Zam yaparken dinlemelik müzikler', NULL, NULL, '87A0V0LUU5794LVQF34J25FM')
        """)
        # Insert dummy data into the Playlist_User table
        cursor.execute("""
            INSERT INTO Playlist_User (user, fallows) VALUES
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '1'),
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '2'),
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '3'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '1'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '2'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '3'),
            ('87A0V0LUU5794LVQF34J25FM', '1'),
            ('87A0V0LUU5794LVQF34J25FM', '2'),
            ('87A0V0LUU5794LVQF34J25FM', '3')
        """)
        # Insert dummy data into the Song table
        cursor.execute("""
            INSERT INTO Song (song_id, song_name, song_time, song_image, audio) VALUES
            ('1A1SBQP9W812J195HF', 'Stairway to Heaven', 482, NULL, NULL),
            ('3DSJQ63NZNPTYRDJKI', 'Bohemian Rhapsody', 355, NULL, NULL),
            ('5GJLFW12REGUEHQOCL', 'Metal Gear Solid 3 Theme', 150, NULL, NULL),
            ('YJ0CUDKGTHXMTXU3EF', 'Bilgewater', 180, NULL, NULL),
            ('0MR4A202LKODINYHGS', 'Kiss of Death', 240, NULL, NULL),
            ('2PIWPJSZTWOFX3CV9V', 'Under the tree', 122, NULL, NULL),
            ('VT8X566EQQ56DTG0BY', '800kmid', 120, NULL, NULL),
            ('41T70U4ZZZQGZFNXKX', 'Tunceredits', 210, NULL, NULL),
            ('64KZGKHPSASIOVRCN0', '345math', 210, NULL, NULL),
            ('156ASDASDASFASGADA', 'take me out', 237, NULL, NULL)
        """)
        # Insert dummy data into the Playlist_Song table
        cursor.execute("""
            INSERT INTO Playlist_Song (playlist_id, song_id) VALUES
            ('1', '1A1SBQP9W812J195HF'),
            ('1', '3DSJQ63NZNPTYRDJKI'),
            ('1', '5GJLFW12REGUEHQOCL'),
            ('2', 'YJ0CUDKGTHXMTXU3EF'),
            ('2', '0MR4A202LKODINYHGS'),
            ('3', '2PIWPJSZTWOFX3CV9V')
        """)
        # Insert dummy data into the 'Like' table
        cursor.execute("""
            INSERT INTO 'Like' (user_id, song_id) VALUES
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '1A1SBQP9W812J195HF'),
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '3DSJQ63NZNPTYRDJKI'),
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '5GJLFW12REGUEHQOCL'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '1A1SBQP9W812J195HF'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '3DSJQ63NZNPTYRDJKI'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '5GJLFW12REGUEHQOCL'),
            ('87A0V0LUU5794LVQF34J25FM', '1A1SBQP9W812J195HF'),
            ('87A0V0LUU5794LVQF34J25FM', '3DSJQ63NZNPTYRDJKI'),
            ('87A0V0LUU5794LVQF34J25FM', '5GJLFW12REGUEHQOCL')
        """)
        # Insert dummy data into the Genre table
        cursor.execute("""
            INSERT INTO Genre (song_id, genre) VALUES
            ('1A1SBQP9W812J195HF', 'Rock'),
            ('3DSJQ63NZNPTYRDJKI', 'Rock'),
            ('5GJLFW12REGUEHQOCL', 'Jazz'),
            ('YJ0CUDKGTHXMTXU3EF', 'Rock'),
            ('0MR4A202LKODINYHGS', 'Pop'),
            ('2PIWPJSZTWOFX3CV9V', 'Jazz'),
            ('VT8X566EQQ56DTG0BY', 'Rap'),
            ('41T70U4ZZZQGZFNXKX', 'Pop'),
            ('64KZGKHPSASIOVRCN0', 'Rock'),
            ('156ASDASDASFASGADA', 'Rock')
        """)
        # Insert dummy data into the Album table
        cursor.execute("""
            INSERT INTO Album (album_id, album_name, about, album_image) VALUES
            ('85XC5Z8F33UL4JS2', 'This fffire', 'This is a dummy album', NULL),
            ('P1RUC42YA8O3KOMU', 'The Wall', 'This is a dummy album', NULL),
            ('W6LMTZWGR4IVRK6C', 'Evolve', 'This is a dummy album', NULL),
            ('DBF505QZY9CE8P0V', 'The Division Bell', 'This is a dummy album', NULL)
        """)
        # Insert dummy data into the Album_Info table
        cursor.execute("""
            Insert INTO Album_Info (album_id, song_id) VALUES
            ('85XC5Z8F33UL4JS2', '1A1SBQP9W812J195HF'),
            ('P1RUC42YA8O3KOMU', '3DSJQ63NZNPTYRDJKI'),
            ('W6LMTZWGR4IVRK6C', '5GJLFW12REGUEHQOCL'),
            ('DBF505QZY9CE8P0V', 'YJ0CUDKGTHXMTXU3EF'),
            ('85XC5Z8F33UL4JS2', '0MR4A202LKODINYHGS'),
            ('P1RUC42YA8O3KOMU', '2PIWPJSZTWOFX3CV9V'),
            ('W6LMTZWGR4IVRK6C', 'VT8X566EQQ56DTG0BY'),
            ('DBF505QZY9CE8P0V', '41T70U4ZZZQGZFNXKX'),
            ('85XC5Z8F33UL4JS2', '64KZGKHPSASIOVRCN0'),
            ('P1RUC42YA8O3KOMU', '156ASDASDASFASGADA')
        """)
        # Insert dummy data into the 'Group' table
        cursor.execute("""
            INSERT INTO 'Group' (group_id, group_name, group_image) VALUES
            ('85XB4Y7F32UK3IR1', 'The Beatles', NULL),
            ('O0QTB31XA8N3KOLT', 'Queen', NULL),
            ('V5KLSZVFQ3HVRJ5B', 'Pink Floyd', NULL),
            ('CBE4Z4PYX9BD7PZU', 'Metallica', NULL),
            ('J68M69JQ4E5VEUTC', 'Led Zeppelin', NULL)
        """)
        # Insert dummy data into the Artist table
        cursor.execute("""
            INSERT INTO Artist (group_id, full_name) VALUES
            ('85XB4Y7F32UK3IR1', 'John Lennon'),
            ('85XB4Y7F32UK3IR1', 'Paul McCartney'),
            ('85XB4Y7F32UK3IR1', 'George Harrison'),
            ('85XB4Y7F32UK3IR1', 'Ringo Starr'),
            ('O0QTB31XA8N3KOLT', 'Freddie Mercury'),
            ('V5KLSZVFQ3HVRJ5B', 'David Gilmour'),
            ('V5KLSZVFQ3HVRJ5B', 'Nick Mason'),
            ('V5KLSZVFQ3HVRJ5B', 'Richard Wright'),
            ('CBE4Z4PYX9BD7PZU', 'James Hetfield'),
            ('CBE4Z4PYX9BD7PZU', 'Lars Ulrich'),
            ('CBE4Z4PYX9BD7PZU', 'Kirk Hammett'),
            ('CBE4Z4PYX9BD7PZU', 'Robert Trujillo'),
            ('J68M69JQ4E5VEUTC', 'Robert Plant')
        """)
        # Insert dummy data into the Album_Group table
        cursor.execute("""
            INSERT INTO Album_Group (album_id, group_id) VALUES
            ('85XC5Z8F33UL4JS2', '85XB4Y7F32UK3IR1'),
            ('P1RUC42YA8O3KOMU', 'O0QTB31XA8N3KOLT'),
            ('W6LMTZWGR4IVRK6C', 'V5KLSZVFQ3HVRJ5B'),
            ('DBF505QZY9CE8P0V', 'V5KLSZVFQ3HVRJ5B'),
            ('85XC5Z8F33UL4JS2', 'CBE4Z4PYX9BD7PZU'),
            ('P1RUC42YA8O3KOMU', 'J68M69JQ4E5VEUTC')
        """)
        # Insert dummy data into the History table
        cursor.execute("""
            Insert INTO History (user_id, start_time, duration, song) VALUES
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '2021-05-01 12:00:00', 210, '1A1SBQP9W812J195HF'),
            ('64KZGKHPS2HIOVRCN0ERNG28', '2021-05-01 12:00:00', 210, '3DSJQ63NZNPTYRDJKI'),
            ('87A0V0LUU5794LVQF34J25FM', '2021-05-01 12:00:00', 210, '5GJLFW12REGUEHQOCL'),
            ('1A1SBQP9W8Y1J195HFVARMJR', '2021-05-01 12:00:00', 210, 'YJ0CUDKGTHXMTXU3EF'),
            ('41T70U4BZZQGZFNXKXNQ8ZYT', '2021-05-01 12:00:00', 210, '0MR4A202LKODINYHGS')
        """)

        connection.commit()
        print("Dummy data inserted successfully.")
    except sqlite3.IntegrityError:
        pass
    finally:
        connection.close()