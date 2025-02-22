import sys
import os
import pandas as pd
import json
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import time
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent))
from main import get_gemini_response, sql_prompt

def validate_sql_query(query, conn):
    """Validate if the SQL query is syntactically correct"""
    try:
        with conn.cursor() as cursor:
            # Reset any aborted transaction
            conn.rollback()
            
            # Now try to validate the query
            cursor.execute("EXPLAIN " + query)
            conn.commit()  # Commit the successful EXPLAIN
            return True, None
    except psycopg2.Error as e:
        # Rollback on error
        conn.rollback()
        return False, str(e)

def handle_api_error(error):
    """Handle different types of API errors"""
    if "429" in str(error):
        return "API quota exceeded", 30  # Wait 30 seconds
    return str(error), 0

def run_query_tests():
    load_dotenv()
    
    # Database connection
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432')
    )
    
    # Read the test dataset with encoding specification
    csv_path = Path(__file__).parent / 'Pagila Evals Dataset(Sheet1).csv'
    try:
        test_data = pd.read_csv(csv_path, encoding='cp1252')
    except UnicodeDecodeError:
        # Fallback to latin-1 if cp1252 fails
        test_data = pd.read_csv(csv_path, encoding='latin-1')
    
    # Clean up any special quotes in the queries
    test_data['Natural Language Query'] = test_data['Natural Language Query'].str.replace('"', '"').str.replace('"', '"')
    
    results_dir = Path(__file__).parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Load existing results if any
    output_file = results_dir / 'query_results.json'
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = {}
    
    # Process queries with progress bar
    for _, row in tqdm(test_data.iterrows(), total=len(test_data), desc="Processing queries"):
        query_num = str(row['Query Number'])
        
        # Skip if already processed successfully
        if query_num in results and results[query_num]['sql_query'] and results[query_num]['is_valid']:
            continue
            
        nl_query = row['Natural Language Query']
        difficulty = row['Difficulty']
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                sql_query = get_gemini_response(nl_query, sql_prompt)
                sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
                
                is_valid, error_msg = validate_sql_query(sql_query, conn)
                
                results[query_num] = {
                    'natural_language_query': nl_query,
                    'sql_query': sql_query,
                    'difficulty': difficulty,
                    'is_valid': is_valid,
                    'error': error_msg
                }
                
                # Save progress after each successful query
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                break  # Success, exit retry loop
                
            except Exception as e:
                error_msg, wait_time = handle_api_error(e)
                retry_count += 1
                
                if wait_time > 0:
                    print(f"\nAPI quota exceeded. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                
                if retry_count == max_retries:
                    results[query_num] = {
                        'natural_language_query': nl_query,
                        'sql_query': None,
                        'difficulty': difficulty,
                        'is_valid': False,
                        'error': error_msg
                    }
                    
                    # Save progress even for failed queries
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
    
    conn.close()
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    run_query_tests()
