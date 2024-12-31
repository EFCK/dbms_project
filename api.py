from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from statements import statements
import sqlite3

app = Flask(__name__)
api = Api(app, title="Music Database API", version="1.0", description="API documentation for the music database")
DATABASE = 'music.db'

# Initialize database
def init_db():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    for statement in statements:
        cursor.execute(statement)
    connection.commit()
    connection.close()

# Helper function to get database connection
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

# Namespace for Account
account_ns = Namespace('account', description="Operations related to accounts")

# Account model for Swagger documentation
account_model = api.model('Account', {
    'account_id': fields.String(required=True, description="The account ID"),
    'mail': fields.String(required=True, description="The email address"),
    'full_name': fields.String(description="The full name of the account holder"),
    'is_subscriber': fields.Boolean(description="Subscription status"),
    'country': fields.String(description="The country of the account holder"),
    'sex': fields.String(description="The gender of the account holder"),
    'language': fields.String(required=True, description="Preferred language"),
    'birth_date': fields.String(description="Date of birth (YYYY-MM-DD)")
})

@account_ns.route('/')
class AccountList(Resource):
    @account_ns.marshal_list_with(account_model)
    def get(self):
        """Get all accounts"""
        connection = get_db_connection()
        accounts = connection.execute('SELECT * FROM Account').fetchall()
        connection.close()
        return [dict(account) for account in accounts]

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
    @account_ns.marshal_with(account_model)
    def get(self, account_id):
        """Get an account by ID"""
        connection = get_db_connection()
        account = connection.execute('SELECT * FROM Account WHERE account_id = ?', (account_id,)).fetchone()
        connection.close()
        if account is None:
            return {"message": "Account not found"}, 404
        return dict(account)

    @account_ns.expect(account_model)
    def put(self, account_id):
        """Update an account"""
        data = request.json
        connection = get_db_connection()
        connection.execute('''UPDATE Account SET mail = ?, full_name = ?, is_subscriber = ?, country = ?, 
                              sex = ?, language = ?, birth_date = ? WHERE account_id = ?''',
                           (data['mail'], data['full_name'], data.get('is_subscriber', 0), data.get('country'),
                            data.get('sex'), data['language'], data.get('birth_date'), account_id))
        connection.commit()
        connection.close()
        return {"message": "Account updated successfully"}, 200

    def delete(self, account_id):
        """Delete an account"""
        connection = get_db_connection()
        connection.execute('DELETE FROM Account WHERE account_id = ?', (account_id,))
        connection.commit()
        connection.close()
        return {"message": "Account deleted successfully"}, 200

api.add_namespace(account_ns)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
