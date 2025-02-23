# Text-to-SQL Query Assistant for PagilaDB

A powerful natural language to SQL query converter specifically designed for the Pagila DVD rental database, powered by Google's Gemini AI.

## Features

- 🤖 Natural language to SQL conversion using Gemini AI
- 📊 Interactive Streamlit web interface
- 🔄 Real-time query execution
- 💾 PostgreSQL database integration
- 🐳 Docker support for easy deployment

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 14+ 
- Google API key for Gemini AI

### PostgreSQL Setup

1. Install PostgreSQL:
   ```bash
   # For Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # For macOS using Homebrew
   brew install postgresql
   
   # For Windows
   # Download and run installer from https://www.postgresql.org/download/windows/
   ```

2. Start PostgreSQL service:
   ```bash
   # For Ubuntu/Debian
   sudo service postgresql start
   
   # For macOS
   brew services start postgresql
   
   # For Windows
   # PostgreSQL service starts automatically after installation
   ```

3. Create Pagila database:
   ```bash
   # Login as postgres user
   sudo -u postgres psql

   # Create database
   CREATE DATABASE pagila;
   
   # Exit psql
   \q
   ```

4. Import Pagila schema and data:
   ```bash
   # Import schema
   psql -U postgres -d pagila -f pagila\1. pagila-schema.sql
   
   # Import data
   psql -U postgres -d pagila -f pagila\2. pagila-insert-data.sql
   ```

5. Verify installation:
   ```bash
   psql -U postgres -d pagila
   
   # List all tables
   \dt
   
   # Test a simple query
   SELECT count(*) FROM film;
   ```

### Environment Variables

Create a `.env` file with:

```
GOOGLE_API_KEY=your_gemini_api_key
DB_NAME=pagila
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/PrathamKumar125/Text-to-SQL-PagilaDB.git
cd Text-to-SQL-PagilaDB
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the FastAPI backend:
```bash
uvicorn main:app --reload
```

2. Start the Streamlit frontend:
```bash
streamlit run streamlit_app.py
```

### Docker Deployment

Build and run using Docker:
```bash
docker build -t text-to-sql .
docker run -p 7860:7860 -p 8000:8000 text-to-sql
```

## Usage

1. Open the Streamlit interface in your browser
2. Enter your question in natural language
3. Click "Submit" to generate and execute the SQL query
4. View the results in a formatted table

## Database Schema

The application works with the Pagila DVD rental database, which includes tables for:
- Actors
- Films
- Categories
- Customers
- Rentals
- Payments
- Inventory
