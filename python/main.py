import os
import psycopg2
import uuid
import json
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def load_google_api_key(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
        return config.get("google_api_key")

google_api_key = load_google_api_key('config.json')
os.environ['GOOGLE_API_KEY'] = google_api_key
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

def load_texts_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

texts = load_texts_from_json('texts.json')

def normalize_embedding(embedding):
    """Normalize the embedding vector to unit length."""
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm

def fetch_embeddings(texts):
    embedded_texts = []
    for text in texts:
        embedding = embeddings.embed_query(text)
        normalized_embedding = normalize_embedding(embedding)
        embedded_texts.append(normalized_embedding.tolist())
    return embedded_texts

def generate_prefixed_uuid():
    generated_uuid = uuid.uuid4()
    return f"{generated_uuid}"

def check_error_exists(cursor, error_text):
    cursor.execute(
        "SELECT id FROM knowledge_base_error WHERE text = %s",
        (error_text,)
    )
    existing_error = cursor.fetchone()
    return existing_error is not None

def save_error_fix_to_db(data):
    cursor = None
    connection = None
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="mydatabase",
            user="myuser",
            password="mypassword"
        )
        cursor = connection.cursor()

        for entry in data:
            error_text = entry["Error"]
            fix_text = entry["Fix"]
            language = entry["Language"]
            tool = entry["Tool"]

            if check_error_exists(cursor, error_text):
                print(f"Error '{error_text}' already exists in the database. Skipping insertion.")
                continue

            error_embedding = fetch_embeddings([error_text])[0]

            reference = generate_prefixed_uuid()

            cursor.execute(
                "INSERT INTO knowledge_base_error (embedding, text, metadata) "
                "VALUES (%s, %s, %s) RETURNING id",
                (error_embedding, error_text, reference)
            )
            error_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO knowledge_base_fix (fix, metadata, language, tool) "
                "VALUES (%s, %s, %s, %s)",
                (fix_text, reference, language, tool)
            )

        connection.commit()
        print(f"Inserted {len(data)} ERROR and FIX pairs into the knowledge_base table.")

    except Exception as error:
        print(f"Error: {error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Connection closed.")

save_error_fix_to_db(texts)
