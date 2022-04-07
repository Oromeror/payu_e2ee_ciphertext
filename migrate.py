from database import mysql


MIGRATE_FILE = 'migrate.sql'


def migrate():
    mysql.sql_conn = mysql.db_connection(is_migrate=True)
    mysql.execute_query(MIGRATE_FILE)
    mysql.sql_conn.close()


if __name__ == '__main__':
    migrate()