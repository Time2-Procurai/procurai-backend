import os
import sys
import time
import psycopg
import traceback

# Ensure application root is on PYTHONPATH so importing settings works
APP_DIR = '/app'
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

LOCK_ID = 123456789  # constant advisory lock id for migrations
DB_URL = os.environ.get('DATABASE_URL')
TIMEOUT = int(os.environ.get('MIGRATION_LOCK_TIMEOUT', '300'))  # seconds
SLEEP_INTERVAL = 2


def acquire_lock(conn):
    with conn.cursor() as cur:
        cur.execute('SELECT pg_try_advisory_lock(%s)', (LOCK_ID,))
        return cur.fetchone()[0]


def release_lock(conn):
    with conn.cursor() as cur:
        cur.execute('SELECT pg_advisory_unlock(%s)', (LOCK_ID,))


if __name__ == '__main__':
    if not DB_URL:
        print('DATABASE_URL not set; skipping migrations in entrypoint.')
        sys.exit(0)

    started = time.time()
    conn = None
    got_lock = False
    try:
        # keep trying to connect until timeout
        while True:
            try:
                conn = psycopg.connect(DB_URL, autocommit=True)
                break
            except Exception as e:
                if time.time() - started > TIMEOUT:
                    print('Timed out trying to connect to DB:', e)
                    raise
                print('Waiting for DB to be available...')
                time.sleep(SLEEP_INTERVAL)

        # try to acquire advisory lock
        while True:
            try:
                got_lock = acquire_lock(conn)
                if got_lock:
                    print('Acquired migration advisory lock; running migrations')
                    break
                else:
                    elapsed = time.time() - started
                    if elapsed > TIMEOUT:
                        print('Timed out waiting for migration lock; exiting')
                        sys.exit(1)
                    print('Another instance is running migrations — waiting...')
                    time.sleep(SLEEP_INTERVAL)
            except Exception:
                traceback.print_exc()
                time.sleep(SLEEP_INTERVAL)

        # Run Django migrations programmatically
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'procurai_backend.settings')
        import django
        django.setup()
        from django.core.management import call_command

        call_command('migrate', interactive=False, verbosity=1)
        print('Migrations complete')

    except Exception:
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            if got_lock and conn is not None:
                release_lock(conn)
                print('Released migration advisory lock')
        except Exception:
            traceback.print_exc()
        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass
