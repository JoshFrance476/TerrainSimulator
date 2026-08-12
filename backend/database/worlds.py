from database.db import pool
from psycopg.types.json import Jsonb

def upsert_save(name, description, owner_id, map_data, map_png, biome_config, story_setup, region_list):
    with pool.connection() as conn:
        return conn.execute(
            """
            INSERT INTO worlds (name, description, owner_id, map_data, map_png, biome_config, story_setup, region_list)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (owner_id, name) DO UPDATE SET
                description = EXCLUDED.description,
                map_data = EXCLUDED.map_data,
                map_png = EXCLUDED.map_png,
                biome_config = EXCLUDED.biome_config,
                story_setup = EXCLUDED.story_setup,
                region_list = EXCLUDED.region_list
            RETURNING id;
            """,
            (name, description, owner_id, map_data, map_png, Jsonb(biome_config), Jsonb(story_setup), Jsonb(region_list)),
        ).fetchone()

def get_world(world_id):
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM worlds WHERE id = %s", (world_id,)
        ).fetchone()

def list_worlds():
    with pool.connection() as conn:
        return conn.execute(
            "SELECT id, name, description, biome_config, story_setup, region_list FROM worlds ORDER BY name"
        ).fetchall()

def get_world_png(world_id): 
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT map_png FROM worlds WHERE id = %s", (world_id,)
        ).fetchone()
        return row["map_png"] if row else None