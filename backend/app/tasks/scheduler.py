"""APScheduler-based periodic tasks."""
import os
import subprocess
import datetime
import shutil
from pathlib import Path
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def backup_database():
    """Daily database backup."""
    backup_dir = Path(os.environ.get('BACKUP_DIR', '/app/backups'))
    backup_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.date.today().isoformat()
    db_host = os.environ.get('MYSQL_HOST', 'mysql')
    db_user = os.environ.get('MYSQL_USER', 'recipe_user')
    db_pass = os.environ.get('MYSQL_PASSWORD', '')
    db_name = os.environ.get('MYSQL_DATABASE', 'smart_recipe')

    sql_file = backup_dir / f"db_{date_str}.sql.gz"
    cmd = f"mysqldump -h{db_host} -u{db_user} -p{db_pass} {db_name} | gzip > {sql_file}"
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, timeout=300)
        print(f"[Backup] Database: {sql_file} ({sql_file.stat().st_size} bytes)")
    except Exception as e:
        print(f"[Backup] Database failed: {e}")


def backup_uploads():
    """Daily uploads backup."""
    backup_dir = Path(os.environ.get('BACKUP_DIR', '/app/backups'))
    backup_dir.mkdir(parents=True, exist_ok=True)

    uploads_dir = Path(os.environ.get('UPLOADS_DIR', '/app/uploads'))
    if not uploads_dir.exists():
        return

    date_str = datetime.date.today().isoformat()
    tar_file = backup_dir / f"uploads_{date_str}.tar.gz"
    try:
        shutil.make_archive(
            str(tar_file).replace('.tar.gz', ''),
            'gztar',
            uploads_dir,
        )
        print(f"[Backup] Uploads: {tar_file} ({tar_file.stat().st_size} bytes)")
    except Exception as e:
        print(f"[Backup] Uploads failed: {e}")


def cleanup_old_backups(days: int = 30):
    """Remove backups older than specified days."""
    backup_dir = Path(os.environ.get('BACKUP_DIR', '/app/backups'))
    if not backup_dir.exists():
        return

    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    for f in backup_dir.iterdir():
        if f.is_file() and datetime.datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            f.unlink()
            print(f"[Backup] Deleted old: {f}")


def init_scheduler(app: Flask):
    """Initialize scheduler with app context."""
    # Daily at 3:00 AM
    scheduler.add_job(backup_database, 'cron', hour=3, minute=0, id='backup_db')
    scheduler.add_job(backup_uploads, 'cron', hour=3, minute=15, id='backup_uploads')
    scheduler.add_job(cleanup_old_backups, 'cron', hour=4, minute=0, id='cleanup_backups')

    if not scheduler.running:
        scheduler.start()
