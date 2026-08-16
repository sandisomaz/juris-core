import pytest
import uuid
from sqlalchemy import select
from src.core.security import hash_password, verify_password, create_access_token, decode_access_token
from src.storage.db import AsyncSessionLocal, init_db
from src.storage.models import UserDB, MatterDB, DocumentDB, FindingDB, AuditLogDB


def test_password_hashing_and_verification():
    raw_pass = "EnterpriseLegal2026!#"
    hashed = hash_password(raw_pass)

    assert "$" in hashed
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_jwt_token_lifecycle():
    payload = {"sub": "attorney@juriscore.io", "role": "Senior Counsel"}
    token = create_access_token(payload)

    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "attorney@juriscore.io"
    assert decoded["role"] == "Senior Counsel"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_async_database_initialization_and_crud():
    # Initialize DB schema
    await init_db()

    test_matter_id = f"m-test-{uuid.uuid4().hex[:6]}"
    test_doc_id = f"doc-test-{uuid.uuid4().hex[:6]}"

    async with AsyncSessionLocal() as session:
        # Create Matter
        matter = MatterDB(
            id=test_matter_id,
            title="Cross-Border Data Transfer Audit",
            client_name="Test Enterprise Inc",
            jurisdiction="South Africa",
            status="ACTIVE",
            risk_score=75.0
        )
        session.add(matter)

        # Create Document
        doc = DocumentDB(
            id=test_doc_id,
            matter_id=test_matter_id,
            filename="Supplier_DPA_Addendum.txt",
            doc_type="CONTRACT",
            content_raw="Sample clause text with POPIA s72 requirements.",
            processing_status="Verified"
        )
        session.add(doc)

        # Create Finding
        finding = FindingDB(
            id=f"f-{uuid.uuid4().hex[:6]}",
            matter_id=test_matter_id,
            document_id=test_doc_id,
            clause_id="3.1",
            location="Clause 3.1",
            issue="Unrestricted Cross-Border Transfer",
            severity="HIGH",
            legal_basis="POPIA Section 72",
            explanation="Requires binding corporate rules or data subject consent.",
            recommended_action="Insert model clauses."
        )
        session.add(finding)

        # Create Audit Log
        audit = AuditLogDB(
            id=f"a-{uuid.uuid4().hex[:6]}",
            matter_id=test_matter_id,
            document_id=test_doc_id,
            action="FINDING_VERIFIED",
            actor="Senior Legal Counsel",
            details_json={"score": 75}
        )
        session.add(audit)
        await session.commit()

    # Query back in a separate session
    async with AsyncSessionLocal() as session:
        m_stmt = select(MatterDB).where(MatterDB.id == test_matter_id)
        m_res = await session.execute(m_stmt)
        persisted_matter = m_res.scalar_one_or_none()

        assert persisted_matter is not None
        assert persisted_matter.client_name == "Test Enterprise Inc"

        d_stmt = select(DocumentDB).where(DocumentDB.id == test_doc_id)
        d_res = await session.execute(d_stmt)
        persisted_doc = d_res.scalar_one_or_none()

        assert persisted_doc is not None
        assert persisted_doc.filename == "Supplier_DPA_Addendum.txt"

        f_stmt = select(FindingDB).where(FindingDB.matter_id == test_matter_id)
        f_res = await session.execute(f_stmt)
        findings = f_res.scalars().all()

        assert len(findings) >= 1
        assert findings[0].issue == "Unrestricted Cross-Border Transfer"
