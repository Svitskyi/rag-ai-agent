CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL
);

INSERT INTO users (username, email) VALUES
('myuser', 'myuser@example.com');

CREATE EXTENSION IF NOT EXISTS vector;

--CREATE TABLE IF NOT EXISTS embeddings (
--  id SERIAL PRIMARY KEY,
--  embedding vector,
--  text text,
--  created_at timestamptz DEFAULT now()
--);

CREATE TABLE knowledge_base_error (
    id SERIAL PRIMARY KEY,
    embedding VECTOR(768),
    text TEXT NOT NULL,            
    metadata UUID NOT NULL
);

CREATE TABLE knowledge_base_fix (
    id SERIAL PRIMARY KEY,
    fix TEXT NOT NULL,
    metadata UUID NOT NULL,
    language VARCHAR(255),
    tool VARCHAR(255),
    knowledge_base_error_id INT,
    FOREIGN KEY (knowledge_base_error_id) REFERENCES knowledge_base_error(id) ON DELETE CASCADE
);