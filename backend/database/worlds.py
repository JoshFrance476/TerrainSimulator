from database.db import pool
from psycopg.types.json import Jsonb

def upsert_save(owner_id, name, description, width, height, starting_location,
                biome, elevation, region, map_png,
                biome_lookup, region_lookup, story_setup, detail_lookup, component_lookup, detail, component):
    with pool.connection() as conn:
        conn.execute("""
            INSERT INTO worlds_v2 (owner_id, name, description, width, height, starting_location,
                                biome, elevation, region, map_png,
                                biome_lookup, region_lookup, story_setup, detail_lookup, component_lookup, detail, component)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (owner_id, name) DO UPDATE SET
                description   = EXCLUDED.description,
                width         = EXCLUDED.width,
                height        = EXCLUDED.height,
                starting_location = EXCLUDED.starting_location,
                biome         = EXCLUDED.biome,
                elevation     = EXCLUDED.elevation,
                region        = EXCLUDED.region,
                map_png       = EXCLUDED.map_png,
                biome_lookup  = EXCLUDED.biome_lookup,
                region_lookup = EXCLUDED.region_lookup,
                story_setup   = EXCLUDED.story_setup,
                detail_lookup = EXCLUDED.detail_lookup, 
                component_lookup = EXCLUDED.component_lookup,
                detail        = EXCLUDED.detail,
                component     = EXCLUDED.component
        """, (owner_id, name, description, width, height, Jsonb(starting_location),
              biome, elevation, region, map_png,
              Jsonb(biome_lookup), Jsonb(region_lookup), Jsonb(story_setup), Jsonb(detail_lookup), Jsonb(component_lookup), detail, component))

def get_world(world_id):
    with pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM worlds_v2 WHERE id = %s", (world_id,)
        ).fetchone()

def list_worlds():
    with pool.connection() as conn:
        return conn.execute(
            "SELECT id, name, description, biome_lookup, story_setup, region_lookup, component_lookup FROM worlds_v2 ORDER BY name"
        ).fetchall()

def get_world_png(world_id): 
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT map_png FROM worlds_v2 WHERE id = %s", (world_id,)
        ).fetchone()
        return row["map_png"] if row else None