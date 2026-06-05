#!/usr/bin/env python3
"""Python backup script for database + uploads. Can be run standalone or via scheduler."""
import os, sys, subprocess, datetime, shutil, gzip
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BACKUP_DIR = Path(os.environ.get('BACKUP_DIR', os.path.dirname(__file__) + '/../backups'))
UPLOADS_DIR = Path(os.environ.get('UPLOADS_DIR', os.path.dirname(__file__) + '/../uploads'))
DB_NAME = os.environ.get('MYSQL_DATABASE', 'smart_recipe')
DB_USER = os.environ.get('MYSQL_USER', 'recipe_user')
DB_PASS = os.environ.get('MYSQL_PASSWORD', '')
DB_HOST = os.environ.get('MYSQL_HOST', 'mysql')
RETENTION_DAYS = int(os.environ.get('RETENTION_DAYS', '30'))


def backup_database():
    """Dump MySQL database to gzipped SQL file."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.date.today().isoformat()
    sql_file = BACKUP_DIR / f"db_{date_str}.sql.gz"

    cmd = f"mysqldump -h{DB_HOST} -u{DB_USER} -p{DB_PASS} {DB_NAME} | gzip > {sql_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

    if result.returncode == 0 and sql_file.exists():
        size = sql_file.stat().st_size
        print(f"[Backup] Database: {sql_file} ({size:,} bytes)")
        return str(sql_file)
    else:
        print(f"[Backup] Database failed: {result.stderr[:200]}")
        return None


def backup_uploads():
    """Tar and gzip the uploads directory."""
    if not UPLOADS_DIR.exists():
        print(f"[Backup] Uploads skipped: {UPLOADS_DIR} not found")
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.date.today().isoformat()
    tar_file = BACKUP_DIR / f"uploads_{date_str}.tar.gz"

    try:
        shutil.make_archive(
            str(tar_file).replace('.tar.gz', '').replace('.tar', ''),
            'gztar',
            str(UPLOADS_DIR),
        )
        size = tar_file.stat().st_size
        print(f"[Backup] Uploads: {tar_file} ({size:,} bytes)")
        return str(tar_file)
    except Exception as e:
        print(f"[Backup] Uploads failed: {e}")
        return None


def cleanup_old_backups(days: int = RETENTION_DAYS):
    """Remove backups older than `days`."""
    if not BACKUP_DIR.exists():
        return

    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    deleted = 0
    for f in BACKUP_DIR.iterdir():
        if f.is_file():
            mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                deleted += 1
                print(f"[Backup] Deleted old: {f.name}")

    print(f"[Backup] Cleanup: removed {deleted} old backup(s)")


if __name__ == '__main__':
    print(f"=== Backup started at {datetime.datetime.now()} ===")
    backup_database()
    backup_uploads()
    cleanup_old_backups()
    print(f"=== Backup completed at {datetime.datetime.now()} ===")
