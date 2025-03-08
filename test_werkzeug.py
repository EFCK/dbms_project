from werkzeug.security import generate_password_hash

# Test the werkzeug library
password = "test_password"
hashed_password = generate_password_hash(password)

print("Original password:", password)
print("Hashed password:", hashed_password)
print("First 29 characters:", hashed_password[:29])
print("Werkzeug is working properly!") 