from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(db: Session, log: AuditLog) -> AuditLog:
    """Persist an audit log entry."""
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
