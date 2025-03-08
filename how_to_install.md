# SUPERTIFY Installation Guide

This guide provides step-by-step instructions to set up and run the SUPERTIFY music streaming platform on your local machine.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dbms_project.git
cd dbms_project
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with other Python projects:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

#### On Windows (Command Prompt):
```bash
venv\Scripts\activate.bat
```

#### On Windows (PowerShell):
```bash
.\venv\Scripts\Activate.ps1
```
    
#### On macOS and Linux:
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating that the virtual environment is active.

### 4. Install Required Packages

```bash
pip install -r requirements.txt
```

This will install all dependencies including Flask, Flask-RESTX, Flask-JWT-Extended, and other required packages.

## Running the Application

### 1. Navigate to the Project Directory

Make sure your virtual environment is activated, then navigate to the milestone3 directory:

```bash
cd milestone3
```

### 2. Start the Flask Application

```bash
python api.py
```

### 3. Access the API

The API should now be running at:
- API endpoints: http://127.0.0.1:5000/
- Swagger documentation: http://127.0.0.1:5000/

## Database Initialization

The database will be automatically initialized when you first run the application. It includes:

1. Creating all necessary tables
2. Setting up foreign key constraints
3. Adding indexes for performance
4. Inserting sample data for testing

## Troubleshooting

### Common Issues

1. **Package Installation Errors**: If you encounter issues installing packages, try upgrading pip:
   ```bash
   pip install --upgrade pip
   ```

2. **Port Already in Use**: If port 5000 is already in use, you can modify the port in `api.py`.

3. **Database Errors**: If you encounter database issues, you can reset the database by deleting the `supertify.db` file and restarting the application.

## Next Steps

Once the application is running, you can:

1. Explore the API using the Swagger documentation
2. Create users and authenticate
3. Add songs, albums, and playlists
4. Test the various endpoints

For any questions or issues, please refer to the project documentation or create an issue on the GitHub repository. 