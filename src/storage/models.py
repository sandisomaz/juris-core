import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), default="")
    role = Column(String(50), default="Legal Counsel")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)


class MatterDB(Base):
    __tablename__ = "matters"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    client_name = Column(String(255), default="")
    jurisdiction = Column(String(50), default="South Africa")
    status = Column(String(50), default="ACTIVE")
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    documents = relationship("DocumentDB", back_populates="matter", cascade="all, delete-orphan")


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True)
    matter_id = Column(String(36), ForeignKey("matters.id"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    doc_type = Column(String(50), default="CONTRACT")
    file_size_bytes = Column(Integer, default=0)
    processing_status = Column(String(50), default="Verified")
    content_raw = Column(Text, default="")
    clauses_json = Column(JSON, default=list)
    parsed_metadata_json = Column(JSON, default=dict)
    upload_timestamp = Column(DateTime, default=utc_now)

    matter = relationship("MatterDB", back_populates="documents")


class FindingDB(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True)
    matter_id = Column(String(36), index=True, nullable=False)
    document_id = Column(String(36), index=True, nullable=False)
    clause_id = Column(String(50), nullable=False)
    location = Column(String(255), default="")
    issue = Column(String(255), nullable=False)
    severity = Column(String(50), default="HIGH")
    legal_basis = Column(String(255), default="")
    source = Column(String(255), default="")
    confidence = Column(Float, default=0.9)
    explanation = Column(Text, default="")
    recommended_action = Column(Text, default="")
    redline = Column(Text, nullable=True)
    related_sources_json = Column(JSON, default=list)
    conflicting_clause_ids_json = Column(JSON, default=list)
    verification_status = Column(String(50), default="UNCERTAIN_HUMAN_REVIEW")
    human_decision = Column(String(50), default="PENDING")
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class AuditLogDB(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    matter_id = Column(String(36), index=True, nullable=False)
    document_id = Column(String(36), default="")
    finding_id = Column(String(36), default="")
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="Senior Legal Counsel")
    details_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)
