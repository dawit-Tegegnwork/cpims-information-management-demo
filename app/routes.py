from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models import CaseStatus
from app.schemas import (
    CaseRecordCreate,
    CaseRecordRead,
    CaseRecordUpdate,
    CompletenessResult,
    DuplicateCandidate,
    DataQualityReport,
)
from app.services.completeness import assess_completeness
from app.services.data_quality import generate_data_quality_report
from app.services.duplicates import find_duplicate_candidates

router = APIRouter(prefix="/api/v1", tags=["cases"])


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "cpims-information-management-demo"}


@router.post("/cases", response_model=CaseRecordRead, status_code=201)
def register_case(payload: CaseRecordCreate, db: Session = Depends(get_db)):
    if crud.get_case_by_number(db, payload.case_number):
        raise HTTPException(status_code=409, detail="Case number already exists")
    return crud.create_case(db, payload)


@router.get("/cases", response_model=list[CaseRecordRead])
def list_cases(
    status: CaseStatus | None = None,
    county: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.list_cases(db, status=status, county=county, skip=skip, limit=limit)


@router.get("/cases/{case_id}", response_model=CaseRecordRead)
def get_case(case_id: int, db: Session = Depends(get_db)):
    record = crud.get_case(db, case_id)
    if not record:
        raise HTTPException(status_code=404, detail="Case not found")
    return record


@router.patch("/cases/{case_id}", response_model=CaseRecordRead)
def update_case(case_id: int, payload: CaseRecordUpdate, db: Session = Depends(get_db)):
    record = crud.get_case(db, case_id)
    if not record:
        raise HTTPException(status_code=404, detail="Case not found")
    return crud.update_case(db, record, payload)


@router.patch("/cases/{case_id}/status", response_model=CaseRecordRead)
def update_case_status(case_id: int, status: CaseStatus, db: Session = Depends(get_db)):
    record = crud.get_case(db, case_id)
    if not record:
        raise HTTPException(status_code=404, detail="Case not found")
    return crud.update_status(db, record, status)


@router.get("/cases/{case_id}/completeness", response_model=CompletenessResult)
def case_completeness(case_id: int, db: Session = Depends(get_db)):
    record = crud.get_case(db, case_id)
    if not record:
        raise HTTPException(status_code=404, detail="Case not found")
    score, missing = assess_completeness(record)
    return CompletenessResult(
        case_id=record.id,
        case_number=record.case_number,
        completeness_score=score,
        missing_fields=missing,
        is_complete=score >= 80 and len(missing) == 0,
    )


@router.get("/duplicates", response_model=list[DuplicateCandidate])
def list_duplicates(
    threshold: float = Query(0.85, ge=0.5, le=1.0),
    db: Session = Depends(get_db),
):
    return find_duplicate_candidates(db, threshold=threshold)


@router.get("/reports/data-quality", response_model=DataQualityReport)
def data_quality_report(db: Session = Depends(get_db)):
    return generate_data_quality_report(db)


@router.get("/export/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db)):
    return PlainTextResponse(content=crud.export_cases_csv(db), media_type="text/csv")


@router.post("/import/csv")
async def import_csv(file: UploadFile, db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    created, errors = crud.import_cases_csv(db, content)
    return {"created": created, "errors": errors}
