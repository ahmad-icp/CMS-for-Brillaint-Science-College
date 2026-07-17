import pytest

from app.modules.certificates.models import (
    CertificateStatus,
    CertificateType,
    DocumentApprovalStatus,
    RepositoryDocumentType,
)
from app.modules.certificates.schemas import (
    CertificateApprovalUpdate,
    CertificateRequestCreate,
    CertificateTemplateCreate,
    DocumentApprovalUpdate,
    DocumentCreate,
)
from app.modules.certificates.service import CertificateService


def test_certificate_approval_issue_and_verification(db_session):
    service = CertificateService(db_session, "college-a")
    template = service.create_template(
        CertificateTemplateCreate(
            code="BON",
            name="Bonafide",
            certificate_type=CertificateType.BONAFIDE,
            body_template="Certificate for {{name}}",
        )
    )
    request = service.request_certificate(
        CertificateRequestCreate(
            template_id=template.id,
            certificate_type=CertificateType.BONAFIDE,
            student_id="student-1",
            purpose="Scholarship",
            context={"name": "Ayesha"},
        ),
        requested_by="student-1",
    )
    assert request.rendered_html == "Certificate for Ayesha"
    approved = service.approve(
        request.id,
        CertificateApprovalUpdate(status=CertificateStatus.APPROVED),
        "principal",
    )
    assert approved.status == CertificateStatus.APPROVED
    issued = service.issue(request.id, "registrar")
    assert issued.status == CertificateStatus.ISSUED
    assert service.verify(issued.verification_code).id == issued.id


def test_document_approval_workflow(db_session):
    service = CertificateService(db_session, "college-a")
    document = service.upload_document(
        DocumentCreate(
            owner_type="student",
            owner_id="student-1",
            document_type=RepositoryDocumentType.ACADEMIC,
            title="Matric Result",
            file_path="storage/documents/matric.pdf",
        )
    )
    approved = service.approve_document(
        document.id,
        DocumentApprovalUpdate(status=DocumentApprovalStatus.APPROVED),
        "registrar",
    )
    assert approved.approval_status == DocumentApprovalStatus.APPROVED
