import os
import psycopg2
import uuid
import json
import numpy as np
from langchain_openai import OpenAIEmbeddings

def load_openai_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
        return config.get("openai_api_key"), config.get("openai_api_base")

openai_api_key, openai_api_base = load_openai_config('config.json')

os.environ['OPENAI_API_KEY'] = openai_api_key
os.environ['OPENAI_API_BASE'] = openai_api_base

embeddings = OpenAIEmbeddings(
    model="text-embedding-nomic-embed-text-v1.5-embedding",
    openai_api_key=openai_api_key,
    openai_api_base=openai_api_base,
    check_embedding_ctx_length=False
)

def load_texts_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

texts = load_texts_from_json('texts.json')

def normalize_embedding(embedding):
    norm = np.linalg.norm(embedding)
    return embedding if norm == 0 else embedding / norm

def fetch_embeddings(texts):
    embedded_texts = []
    for text in texts:
        embedding = embeddings.embed_query(text)
        normalized_embedding = normalize_embedding(embedding)
        embedded_texts.append(normalized_embedding.tolist())
    return embedded_texts


def generate_prefixed_uuid():
    return str(uuid.uuid4())


def check_error_exists(cursor, error_text):
    cursor.execute(
        "SELECT id FROM knowledge_base_error WHERE text = %s",
        (error_text,)
    )
    return cursor.fetchone() is not None


def save_error_fix_to_db(data):
    connection = cursor = None
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
                print(f"Error '{error_text}' already exists. Skipping.")
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
        print(f"Inserted {len(data)} ERROR and FIX pairs.")

    except Exception as error:
        print(f"Database error: {error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Database connection closed.")

save_error_fix_to_db(texts)
