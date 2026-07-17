from datetime import date
from decimal import Decimal

from app.modules.fees.models import ChallanStatus, FeeHeadType, PaymentMethod, PaymentStatus
from app.modules.fees.schemas import ChallanLineCreate, FeeHeadCreate, ManualChallanCreate, PaymentCreate
from app.modules.fees.service import FeeService


def test_manual_challan_and_partial_payment(db_session):
    service = FeeService(db_session, "college-a")
    head = service.create_head(FeeHeadCreate(code="TUI", name="Tuition", head_type=FeeHeadType.TUITION))
    challan = service.create_manual_challan(
        ManualChallanCreate(
            student_id="stu-1",
            billing_period="2026-07",
            issue_date=date(2026, 7, 1),
            due_date=date(2026, 7, 10),
            lines=[
                ChallanLineCreate(
                    fee_head_id=head.id,
                    description="Tuition fee",
                    amount=Decimal("1000"),
                )
            ],
        )
    )
    assert challan.total_amount == Decimal("1000")
    payment = service.record_payment(
        PaymentCreate(
            challan_id=challan.id,
            amount=Decimal("400"),
            method=PaymentMethod.CASH,
            reference_number="R-1",
            paid_on=date(2026, 7, 2),
        ),
        "cashier",
    )
    assert payment.status == PaymentStatus.RECONCILED
    assert challan.status == ChallanStatus.PARTIALLY_PAID
    assert challan.balance_amount == Decimal("600")


def test_duplicate_payment_is_flagged_without_double_counting(db_session):
    service = FeeService(db_session, "college-a")
    head = service.create_head(FeeHeadCreate(code="EXAM", name="Exam", head_type=FeeHeadType.EXAM))
    challan = service.create_manual_challan(
        ManualChallanCreate(
            student_id="stu-1",
            billing_period="2026-FALL",
            issue_date=date(2026, 8, 1),
            due_date=date(2026, 8, 15),
            lines=[
                ChallanLineCreate(
                    fee_head_id=head.id,
                    description="Examination fee",
                    amount=Decimal("500"),
                )
            ],
        )
    )
    payload = PaymentCreate(
        challan_id=challan.id,
        amount=Decimal("500"),
        method=PaymentMethod.BANK_TRANSFER,
        reference_number="BANK-1",
        paid_on=date(2026, 8, 2),
    )
    service.record_payment(payload, "cashier")
    duplicate = service.record_payment(payload, "cashier")
    assert duplicate.status == PaymentStatus.DUPLICATE
    assert challan.paid_amount == Decimal("500")
