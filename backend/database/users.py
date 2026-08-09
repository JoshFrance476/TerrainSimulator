from database.db import pool


def get_user(user_id):
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        ).fetchone()

def get_user_by_provider(provider, provider_id):
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE provider = %s AND provider_id = %s",
            (provider, provider_id),
        ).fetchone()


def create_user(provider, provider_id, email, name):
    with pool.connection() as conn:
        return conn.execute(
            "INSERT INTO users (provider, provider_id, email, name) VALUES (%s, %s, %s, %s) RETURNING *",
            (provider, provider_id, email, name),
        ).fetchone()