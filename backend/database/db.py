import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

load_dotenv()

pool = ConnectionPool(  
    os.environ["DATABASE_URL"],
    open=False,
    kwargs={"row_factory": dict_row},
    timeout=10
)