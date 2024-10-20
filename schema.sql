CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    hashed_password TEXT,
    max_token_age TIMESTAMP
);
