import psycopg
from django.conf import settings
from django.core.management.base import BaseCommand
from psycopg import sql
from psycopg.errors import UndefinedObject


class Command(BaseCommand):
    help = "Drops and recreates the database defined in settings.py."

    def handle(self, *args, **kwargs):
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default'].get('HOST', 'localhost')
        db_port = settings.DATABASES['default'].get('PORT', '5432')

        try:
            # Connect to the PostgreSQL server
            with psycopg.connect(dbname='postgres', user=db_user, password=db_password, host=db_host,
                                 port=db_port) as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    # Terminate connections to the target database
                    cursor.execute(sql.SQL("""
                        SELECT pg_terminate_backend(pid) 
                        FROM pg_stat_activity 
                        WHERE datname = %s;
                    """), [db_name])

                    # Drop the existing database
                    cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
                    self.stdout.write(self.style.WARNING(f"Database '{db_name}' dropped successfully."))

                    # Recreate the database
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                    self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' recreated successfully."))
        except UndefinedObject:
            self.stdout.write(self.style.ERROR(f"Database '{db_name}' does not exist."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
