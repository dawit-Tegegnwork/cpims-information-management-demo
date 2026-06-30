from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database import SessionLocal, init_db
from app.models import CaseRecord, CaseStatus
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
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>CPIMS Information Management Demo</title>
        <style>
          body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #f8fafc; color: #102033; }
          main { max-width: 1040px; margin: 0 auto; padding: 56px 22px; }
          .hero { border-radius: 30px; padding: 40px; background: #ffffff; box-shadow: 0 24px 70px rgba(15, 23, 42, .12); border: 1px solid #e2e8f0; }
          .kicker { color: #0f766e; text-transform: uppercase; letter-spacing: .16em; font-size: 12px; font-weight: 800; }
          h1 { margin: 12px 0; font-size: clamp(34px, 6vw, 62px); line-height: .98; letter-spacing: -.05em; }
          p { color: #475569; line-height: 1.7; font-size: 17px; }
          .notice { margin-top: 18px; padding: 14px 16px; border-radius: 16px; background: #ecfdf5; color: #065f46; border: 1px solid #99f6e4; }
          .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 24px; }
          .card { border: 1px solid #e2e8f0; border-radius: 18px; padding: 18px; background: #f8fafc; }
          .card strong { display: block; margin-bottom: 8px; color: #0f172a; }
          .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }
          a { color: #fff; background: #0f766e; padding: 12px 16px; border-radius: 999px; text-decoration: none; font-weight: 800; }
          a.secondary { color: #0f766e; background: #ecfdf5; border: 1px solid #99f6e4; }
        </style>
      </head>
      <body>
        <main>
          <section class="hero">
            <div class="kicker">Synthetic information management demo</div>
            <h1>Data quality, duplicate detection, and reporting for sensitive case records.</h1>
            <p>
              This portfolio project demonstrates database-backed case registration, completeness scoring,
              duplicate-candidate review, CSV import/export, and operational reporting workflows.
            </p>
            <div class="notice">Synthetic demo only. Not official CPIMS and never for real case records.</div>
            <div class="grid">
              <div class="card"><strong>Data quality</strong>Required-field completeness and reporting metrics.</div>
              <div class="card"><strong>Confidentiality</strong>Privacy notes and synthetic records only.</div>
              <div class="card"><strong>NGO readiness</strong>CSV workflows, user guide, and reporting documentation.</div>
            </div>
            <div class="actions">
              <a href="/dashboard">Operations dashboard</a>
              <a class="secondary" href="/docs">Open API docs</a>
              <a class="secondary" href="/api/v1/reports/data-quality">View data quality report</a>
            </div>
          </section>
        </main>
      </body>
    </html>
    """


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
