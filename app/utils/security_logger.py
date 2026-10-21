"""
Modul Security Audit Logging untuk SIBESTI.
Mengimplementasikan panduan OWASP ASVS V8.1 (Security Logging & Monitoring).
// ASVS 8.1.1: Log security events including authentication, authorization failures, and administrative actions.
// ASVS 8.1.2: Ensure logs do not contain sensitive data like plaintext passwords or session secrets.
"""
import logging
from datetime import datetime
from flask import current_app, request


def get_request_ip():
    """Mengambil IP klien dari request dengan mempertimbangkan proxy terpercaya."""
    if not request:
        return 'system'
    if request.remote_addr:
        return request.remote_addr
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return 'unknown'


def log_security_event(event_type: str, actor: str, description: str, status: str = 'SUCCESS', target: str = None):
    """
    Catat event keamanan terstruktur.
    
    :param event_type: Kategori event (e.g. AUTH_LOGIN, AUTH_LOGOUT, USER_CREATE, REVIEW_APPROVE, REVIEW_REJECT)
    :param actor: Identitas pelaku (email/NIM atau 'anonymous')
    :param description: Ringkasan aksi
    :param status: Status event ('SUCCESS', 'FAILURE', 'WARNING')
    :param target: Entitas target yang terdampak (e.g. user_id, pengajuan_id)
    """
    ip = get_request_ip()
    timestamp = datetime.utcnow().isoformat()
    log_msg = (
        f"[SECURITY_AUDIT] [{timestamp}] [TYPE={event_type}] [STATUS={status}] "
        f"[ACTOR={actor}] [IP={ip}] [TARGET={target or '-'}] - {description}"
    )
    
    # // ASVS 8.1.1: Emit ke logger Flask
    logger = current_app.logger if current_app else logging.getLogger('sibesti.security')
    if status == 'FAILURE':
        logger.warning(log_msg)
    else:
        logger.info(log_msg)
