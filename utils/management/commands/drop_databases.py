from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.utils import OperationalError
import psycopg

class Command(BaseCommand):
    help = "Drops all databases defined in Django settings."

    def handle(self, *args, **options):
        for alias, db_config in settings.DATABASES.items():
            db_name = db_config['NAME']
            db_user = db_config['USER']
            db_password = db_config['PASSWORD']
            db_host = db_config.get('HOST', 'localhost')
            db_port = db_config.get('PORT', '5432')

            self.stdout.write(f"Attempting to drop database '{db_name}'...")

            try:
                # Connect to the PostgreSQL server
                with psycopg.connect(
                    dbname='postgres', user=db_user, password=db_password, host=db_host, port=db_port
                ) as conn:
                    conn.autocommit = True  # Ensure commands execute immediately

                    with conn.cursor() as cursor:
                        # Terminate any active connections to the database
                        cursor.execute(
                            f"""
                            SELECT pg_terminate_backend(pid) 
                            FROM pg_stat_activity 
                            WHERE datname = '{db_name}';
                            """
                        )
                        # Drop the database
                        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
                        self.stdout.write(self.style.SUCCESS(f"Successfully dropped database '{db_name}'"))
            except OperationalError as e:
                self.stderr.write(f"Error: Could not connect to database {db_name}. Details: {e}")
            except Exception as e:
                self.stderr.write(f"Unexpected error: {e}")
