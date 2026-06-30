from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database import SessionLocal, init_db
from app.models import CaseRecord, CaseStatus
from app.landing import render_landing
from app.routes import router


def seed_synthetic_data() -> None:
    db = SessionLocal()
    try:
        if db.query(CaseRecord).count() > 0:
            return
        samples = [
            CaseRecord(
                case_number="DEMO-2024-001",
                child_first_name="Alex",
                child_last_name="Rivera",
                child_date_of_birth=date(2016, 3, 14),
                guardian_name="Maria Rivera",
                guardian_phone="555-0101",
                guardian_email="maria.rivera@example.com",
                referral_source="School counselor",
                county="Oakridge",
                assigned_worker="Jordan Lee",
                status=CaseStatus.ACTIVE,
                intake_date=date(2024, 1, 8),
                notes="Synthetic demo case — reunification plan in progress.",
            ),
            CaseRecord(
                case_number="DEMO-2024-002",
                child_first_name="Alex",
                child_last_name="Rivera",
                child_date_of_birth=date(2016, 3, 14),
                guardian_name="M. Rivera",
                guardian_phone="555-0101",
                referral_source="Hotline",
                county="Oakridge",
                assigned_worker=None,
                status=CaseStatus.DRAFT,
                intake_date=date(2024, 2, 1),
                notes="Potential duplicate intake — pending review.",
            ),
            CaseRecord(
                case_number="DEMO-2024-003",
                child_first_name="Sam",
                child_last_name="Chen",
                child_date_of_birth=date(2019, 7, 22),
                guardian_name="Pat Chen",
                guardian_phone="555-0202",
                referral_source="Pediatric clinic",
                county="Maple",
                assigned_worker="Taylor Brooks",
                status=CaseStatus.UNDER_REVIEW,
                intake_date=date(2024, 3, 15),
            ),
            CaseRecord(
                case_number="DEMO-2024-004",
                child_first_name="Jordan",
                child_last_name="Nguyen",
                child_date_of_birth=None,
                guardian_name=None,
                guardian_phone=None,
                referral_source="Community partner",
                county="Pine",
                assigned_worker=None,
                status=CaseStatus.DRAFT,
                intake_date=None,
                notes="Incomplete registration — missing guardian and DOB.",
            ),
        ]
        db.add_all(samples)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_synthetic_data()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Portfolio demonstration of child protection information management concepts. "
        "All records are synthetic and for educational purposes only."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def landing_page():
    return render_landing(
        "CPIMS Information Management Demo",
        "Production-style portfolio API — case records, completeness scoring, duplicate detection, reporting.",
        "Not official CPIMS. No real individuals or case records.",
        "cpims-information-management-demo",
        extra_links=[
            ("/dashboard", "Operations dashboard"),
            ("/api/v1/reports/data-quality", "Data quality report"),
        ],
        quick_steps=[
            'Check <a href="/health">/health</a>',
            'Open <a href="/dashboard">/dashboard</a> — 4 seeded synthetic cases',
            "<code>GET /api/v1/duplicates</code> — review duplicate candidates",
            "<code>GET /api/v1/reports/data-quality</code> — completeness metrics",
        ],
    )


@app.get("/health")
def root_health():
    return {"status": "ok", "service": "cpims-information-management-demo"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>CPIMS Demo Dashboard</title>
      <style>
        body { font-family: system-ui, sans-serif; margin: 2rem; background: #f8fafc; color: #0f172a; }
        table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e2e8f0; }
        th, td { padding: 0.75rem 1rem; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 0.9rem; }
        th { background: #f1f5f9; }
        .warn { color: #b45309; font-weight: 600; }
      </style>
    </head>
    <body>
      <h1>CPIMS Operations Dashboard</h1>
      <p>Synthetic case records — portfolio demo only.</p>
      <div id="quality">Loading data quality summary...</div>
      <h2>Cases</h2>
      <table>
        <thead><tr><th>Case #</th><th>Child</th><th>County</th><th>Status</th><th>Completeness</th></tr></thead>
        <tbody id="cases"><tr><td colspan="5">Loading...</td></tr></tbody>
      </table>
      <p><a href="/docs">API docs</a></p>
      <script>
        fetch('/api/v1/reports/data-quality').then(r => r.json()).then(q => {
          document.getElementById('quality').innerHTML =
            `<p><strong>${q.total_cases}</strong> cases · avg completeness <strong>${q.completeness_average}%</strong> · duplicates flagged: <strong>${q.duplicate_candidates}</strong></p>`;
        });
        fetch('/api/v1/cases').then(r => r.json()).then(async cases => {
          const scores = await Promise.all(
            cases.map(c => fetch(`/api/v1/cases/${c.id}/completeness`).then(r => r.json()))
          );
          const scoreMap = Object.fromEntries(scores.map(s => [s.case_id, s.completeness_score]));
          document.getElementById('cases').innerHTML = cases.map(c => {
            const score = scoreMap[c.id] ?? '—';
            const low = typeof score === 'number' && score < 70 ? ' class="warn"' : '';
            return `<tr><td>${c.case_number}</td><td>${c.child_first_name} ${c.child_last_name}</td><td>${c.county || '—'}</td><td>${c.status}</td><td${low}>${score}${typeof score === 'number' ? '%' : ''}</td></tr>`;
          }).join('');
        });
      </script>
    </body>
    </html>
    """
