import sqlite3
from flask import Flask
from statements import statements

app = Flask(__name__)
DATABASE = 'music.db'

# Initialize database
def init_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for statement in statements:
        cursor.execute(statement)
    connection.commit()
    connection.close()

@app.route('/')
def home():
    return "Database initialized with tables!"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
