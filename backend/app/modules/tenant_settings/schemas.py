from pydantic import BaseModel, Field


class TenantSettingsPayload(BaseModel):
    institution_name: str = Field(min_length=2, max_length=180)
    campus_name: str = Field(default="", max_length=180)
    principal_name: str = Field(default="", max_length=180)
    address: str = Field(default="", max_length=500)
    phone: str = Field(default="", max_length=40)
    email: str = Field(default="", max_length=255)
    website: str = Field(default="", max_length=255)
    academic_year: str = Field(default="", max_length=40)
    timezone: str = Field(default="Asia/Karachi", max_length=64)
    currency: str = Field(default="PKR", min_length=3, max_length=8)
    logo_url: str = Field(default="", max_length=500)
    primary_color: str = Field(default="#1F4E79", pattern=r"^#[0-9A-Fa-f]{6}$")


class TenantSettingsResponse(TenantSettingsPayload):
    college_id: str
