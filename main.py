# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import google.generativeai as genai

app = FastAPI()

# Load environment variables and configure Genai
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

class Query(BaseModel):
    question: str

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content([prompt, question])
    return response.text.strip()  # Added strip() to remove any extra whitespace

sql_prompt = """
Convert the following English question to a PostgreSQL query for the Pagila DVD rental database.
Only return the SQL query without any markdown formatting or explanations.
The database has these main tables:
- actor (actor_id, first_name, last_name)
- film (film_id, title, description, release_year, rental_rate, length, rating)
- category (category_id, name)
- film_category (film_id, category_id)
- inventory (inventory_id, film_id, store_id)
- rental (rental_id, rental_date, inventory_id, customer_id, return_date, staff_id)
- customer (customer_id, first_name, last_name, email)
- payment (payment_id, customer_id, staff_id, rental_id, amount, payment_date)

Example queries:
Q: List all actors
A: SELECT * FROM actor;

Q: Show top 10 most rented movies
A: SELECT f.title, COUNT(r.rental_id) as rental_count FROM film f JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.title ORDER BY rental_count DESC LIMIT 10;
"""

def execute_sql_query(query):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', '5432')
        )
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Database Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.post("/query")
async def process_query(query: Query):
    try:
        sql_query = get_gemini_response(query.question, sql_prompt)
        # Remove any SQL code block markers if present
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        result = execute_sql_query(sql_query)
        return {"query": sql_query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))