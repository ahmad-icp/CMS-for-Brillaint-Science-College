from enum import StrEnum

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


bearer_scheme = HTTPBearer(auto_error=False)


class Permission(StrEnum):
    STUDENT_READ = "student:read"
    STUDENT_WRITE = "student:write"
    STUDENT_DELETE = "student:delete"
    STUDENT_PROMOTE = "student:promote"
    STUDENT_ALUMNI = "student:alumni"
    DOCUMENT_VERIFY = "document:verify"
    ADMISSION_READ = "admission:read"
    ADMISSION_WRITE = "admission:write"
    ADMISSION_DECIDE = "admission:decide"
    ADMISSION_ENROLL = "admission:enroll"
    MERIT_LIST_MANAGE = "merit_list:manage"
    ACADEMIC_READ = "academic:read"
    ACADEMIC_WRITE = "academic:write"
    ACADEMIC_ASSIGN = "academic:assign"
    ACADEMIC_DELETE = "academic:delete"
    TIMETABLE_READ = "timetable:read"
    TIMETABLE_WRITE = "timetable:write"
    TIMETABLE_PUBLISH = "timetable:publish"
    TIMETABLE_DELETE = "timetable:delete"
    ATTENDANCE_READ = "attendance:read"
    ATTENDANCE_WRITE = "attendance:write"
    ATTENDANCE_MARK = "attendance:mark"
    ATTENDANCE_FINALIZE = "attendance:finalize"
    EXAM_READ = "exam:read"
    EXAM_WRITE = "exam:write"
    EXAM_CONFIGURE = "exam:configure"
    EXAM_SCHEDULE = "exam:schedule"
    EXAM_PUBLISH = "exam:publish"
    EXAM_LOCK = "exam:lock"
    MARKS_READ = "marks:read"
    MARKS_WRITE = "marks:write"
    MARKS_SUBMIT = "marks:submit"
    MARKS_LOCK = "marks:lock"
    RESULT_READ = "result:read"
    RESULT_CALCULATE = "result:calculate"
    RESULT_CONFIGURE = "result:configure"
    RESULT_PUBLISH = "result:publish"
    RESULT_LOCK = "result:lock"
    GRADE_READ = "grade:read"
    GRADE_CONFIGURE = "grade:configure"
    GRADE_CALCULATE = "grade:calculate"
    REPORT_CARD_READ = "report_card:read"
    REPORT_CARD_WRITE = "report_card:write"
    REPORT_CARD_ISSUE = "report_card:issue"
    GAZETTE_READ = "gazette:read"
    GAZETTE_WRITE = "gazette:write"
    MERIT_READ = "merit:read"
    MERIT_WRITE = "merit:write"
    MERIT_PUBLISH = "merit:publish"
    TRANSCRIPT_READ = "transcript:read"
    TRANSCRIPT_WRITE = "transcript:write"
    TRANSCRIPT_ISSUE = "transcript:issue"
    FEE_READ = "fee:read"
    FEE_WRITE = "fee:write"
    FEE_COLLECT = "fee:collect"
    FEE_REFUND = "fee:refund"
    FEE_MANAGE = "fee:manage"
    STUDENT_PORTAL_READ = "student_portal:read"
    PARENT_PORTAL_READ = "parent_portal:read"
    TEACHER_PORTAL_READ = "teacher_portal:read"
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_SEND = "notification:send"
    NOTIFICATION_MANAGE = "notification:manage"
    CERTIFICATE_READ = "certificate:read"
    CERTIFICATE_WRITE = "certificate:write"
    CERTIFICATE_APPROVE = "certificate:approve"
    CERTIFICATE_ISSUE = "certificate:issue"
    CERTIFICATE_MANAGE = "certificate:manage"
    DOCUMENT_READ = "document:read"
    DOCUMENT_WRITE = "document:write"
    DOCUMENT_APPROVE = "document:approve"
    REPORTING_READ = "reporting:read"
    REPORTING_EXPORT = "reporting:export"
    REPORTING_MANAGE = "reporting:manage"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "platform_super_admin": set(Permission),
    "college_owner": set(Permission),
    "principal": set(Permission),
    "administrator": set(Permission),
    "admission_officer": {
        Permission.STUDENT_READ,
        Permission.STUDENT_WRITE,
        Permission.DOCUMENT_VERIFY,
        Permission.ADMISSION_READ,
        Permission.ADMISSION_WRITE,
        Permission.ADMISSION_DECIDE,
        Permission.ADMISSION_ENROLL,
        Permission.MERIT_LIST_MANAGE,
        Permission.ACADEMIC_READ,
        Permission.TIMETABLE_READ,
        Permission.ATTENDANCE_READ,
        Permission.EXAM_READ,
        Permission.MARKS_READ,
        Permission.RESULT_READ,
        Permission.GRADE_READ,
        Permission.REPORT_CARD_READ,
        Permission.GAZETTE_READ,
        Permission.MERIT_READ,
        Permission.TRANSCRIPT_READ,
        Permission.FEE_READ,
        Permission.CERTIFICATE_READ,
        Permission.CERTIFICATE_WRITE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_SEND,
        Permission.REPORTING_READ,
        Permission.REPORTING_EXPORT,
    },
    "teacher": {
        Permission.STUDENT_READ,
        Permission.ACADEMIC_READ,
        Permission.TIMETABLE_READ,
        Permission.ATTENDANCE_READ,
        Permission.ATTENDANCE_MARK,
        Permission.EXAM_READ,
        Permission.MARKS_READ,
        Permission.MARKS_WRITE,
        Permission.MARKS_SUBMIT,
        Permission.RESULT_READ,
        Permission.GRADE_READ,
        Permission.REPORT_CARD_READ,
        Permission.GAZETTE_READ,
        Permission.MERIT_READ,
        Permission.TRANSCRIPT_READ,
        Permission.FEE_READ,
        Permission.CERTIFICATE_READ,
        Permission.DOCUMENT_READ,
        Permission.TEACHER_PORTAL_READ,
        Permission.NOTIFICATION_READ,
        Permission.NOTIFICATION_SEND,
        Permission.REPORTING_READ,
        Permission.REPORTING_EXPORT,
    },
    "parent": {
        Permission.STUDENT_READ,
        Permission.ACADEMIC_READ,
        Permission.TIMETABLE_READ,
        Permission.ATTENDANCE_READ,
        Permission.EXAM_READ,
        Permission.MARKS_READ,
        Permission.RESULT_READ,
        Permission.GRADE_READ,
        Permission.REPORT_CARD_READ,
        Permission.GAZETTE_READ,
        Permission.MERIT_READ,
        Permission.TRANSCRIPT_READ,
        Permission.FEE_READ,
        Permission.CERTIFICATE_READ,
        Permission.DOCUMENT_READ,
        Permission.PARENT_PORTAL_READ,
        Permission.NOTIFICATION_READ,
        Permission.REPORTING_READ,
    },
    "student": {
        Permission.STUDENT_READ,
        Permission.ACADEMIC_READ,
        Permission.TIMETABLE_READ,
        Permission.ATTENDANCE_READ,
        Permission.EXAM_READ,
        Permission.MARKS_READ,
        Permission.RESULT_READ,
        Permission.GRADE_READ,
        Permission.REPORT_CARD_READ,
        Permission.GAZETTE_READ,
        Permission.MERIT_READ,
        Permission.TRANSCRIPT_READ,
        Permission.FEE_READ,
        Permission.CERTIFICATE_READ,
        Permission.DOCUMENT_READ,
        Permission.STUDENT_PORTAL_READ,
        Permission.NOTIFICATION_READ,
        Permission.REPORTING_READ,
    },
}


ROLE_ALIASES = {"admin": "administrator", "super_admin": "platform_super_admin"}


class CurrentUser:
    def __init__(self, user_id: str, college_id: str, role: str) -> None:
        canonical_role = ROLE_ALIASES.get(role, role)
        if canonical_role not in ROLE_PERMISSIONS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unknown or unsupported role: {role}",
            )
        self.user_id = user_id
        self.college_id = college_id
        self.role = canonical_role
        self.permissions = ROLE_PERMISSIONS[canonical_role]


def _get_dev_header_user(x_user_id: str, x_college_id: str, x_role: str) -> CurrentUser:
    if not settings.ALLOW_DEV_AUTH_HEADERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return CurrentUser(user_id=x_user_id, college_id=x_college_id, role=x_role)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
    x_college_id: str | None = Header(default=None),
    x_role: str | None = Header(default=None),
) -> CurrentUser:
    token = credentials.credentials if credentials is not None else None
    if not token and x_user_id and x_college_id and x_role:
        return _get_dev_header_user(x_user_id, x_college_id, x_role)

    from app.modules.authentication.models import User
    from app.modules.authentication.service import decode_access_token

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    user_id = str(payload["sub"])
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    if payload.get("college_id") != user.college_id or payload.get("role") != user.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token claims no longer match user")
    return CurrentUser(user_id=user.id, college_id=user.college_id, role=user.role)


def require_permission(permission: Permission):
    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission.value}",
            )
        return current_user

    return dependency
