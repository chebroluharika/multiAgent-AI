import psycopg2

def get_db_string():
    database_string = 'postgresql://{user}:{pw}@{host}:{port}/{dbname}'
    return database_string.format(user='postgres', pw='postgres', host='localhost',
                                  port='5432', dbname='postgres')
# Connect to PostgreSQL
def get_db_conn():
    db_string = get_db_string()
    try:
        conn = psycopg2.connect(db_string)
    except psycopg2.OperationalError as err:
        err_msg = 'DB Connection Error - Error: {}'.format(err)
        print(err_msg)
        return None
    return conn