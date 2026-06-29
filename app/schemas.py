from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models import CaseStatus


class CaseRecordBase(BaseModel):
    case_number: str = Field(..., min_length=3, max_length=32)
    child_first_name: str = Field(..., min_length=1, max_length=100)
    child_last_name: str = Field(..., min_length=1, max_length=100)
    child_date_of_birth: date | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = None
    guardian_email: str | None = None
    referral_source: str | None = None
    county: str | None = None
    assigned_worker: str | None = None
    status: CaseStatus = CaseStatus.DRAFT
    intake_date: date | None = None
    notes: str | None = None


class CaseRecordCreate(CaseRecordBase):
    pass


class CaseRecordUpdate(BaseModel):
    child_first_name: str | None = None
    child_last_name: str | None = None
    child_date_of_birth: date | None = None
    guardian_name: str | None = None
    guardian_phone: str | None = None
    guardian_email: str | None = None
    referral_source: str | None = None
    county: str | None = None
    assigned_worker: str | None = None
    status: CaseStatus | None = None
    intake_date: date | None = None
    notes: str | None = None


class CaseRecordRead(CaseRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CompletenessResult(BaseModel):
    case_id: int
    case_number: str
    completeness_score: float
    missing_fields: list[str]
    is_complete: bool


class DuplicateCandidate(BaseModel):
    case_id: int
    case_number: str
    matched_case_id: int
    matched_case_number: str
    match_reason: str
    confidence: Literal["high", "medium", "low"]


class DataQualityReport(BaseModel):
    generated_at: datetime
    total_cases: int
    complete_cases: int
    incomplete_cases: int
    duplicate_candidates: int
    status_breakdown: dict[str, int]
    field_null_rates: dict[str, float]
    completeness_average: float
