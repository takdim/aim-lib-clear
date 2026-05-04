import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler = None


def cleanup_expired_files(app):
    """
    Hapus file upload mahasiswa yang sudah melewati masa simpan.
    Dijalankan oleh scheduler setiap hari pukul 02.00.
    """
    with app.app_context():
        from app import db
        from app.models.bebas_pustaka import BebasPustaka

        retention_days = app.config.get('FILE_RETENTION_DAYS', 30)
        cutoff = datetime.utcnow() - timedelta(days=retention_days)

        # Cari pengajuan yang sudah disetujui > retention_days dan file belum dihapus
        expired = BebasPustaka.query.filter(
            BebasPustaka.status == 'disetujui',
            BebasPustaka.file_deleted == False,  # noqa: E712
            BebasPustaka.approved_at <= cutoff
        ).all()

        count = 0
        for pengajuan in expired:
            try:
                pengajuan.delete_files()
                db.session.commit()
                count += 1
                logger.info(
                    f'[Scheduler] File pengajuan ID={pengajuan.id} berhasil dihapus '
                    f'(approved_at={pengajuan.approved_at})'
                )
            except Exception as e:
                db.session.rollback()
                logger.error(f'[Scheduler] Gagal hapus file pengajuan ID={pengajuan.id}: {e}')

        logger.info(f'[Scheduler] Selesai. Total file dihapus: {count}')


def start_scheduler(app):
    """Mulai APScheduler background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone='Asia/Jakarta')
    _scheduler.add_job(
        func=cleanup_expired_files,
        args=[app],
        trigger='cron',
        hour=2,
        minute=0,
        id='cleanup_expired_files',
        replace_existing=True,
        name='Cleanup Expired Upload Files',
    )
    _scheduler.start()
    logger.info('[Scheduler] APScheduler started — cleanup job aktif setiap pukul 02:00 WIB')
