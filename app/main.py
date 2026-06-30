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
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>CPIMS Demo Dashboard</title>
      <style>
        body { font-family: system-ui, sans-serif; margin: 0; background: #FBF7F0; color: #0E2A3B; }
        .banner { background: #ecfdf5; border-bottom: 1px solid #6ee7b7; color: #065f46; padding: 0.65rem 1.5rem; font-size: 0.85rem; }
        main { max-width: 1000px; margin: 0 auto; padding: 1.75rem 1.25rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; margin: 1rem 0 1.5rem; }
        .stat { background: #fff; border: 1px solid #E8DFD0; border-radius: 12px; padding: 1rem; }
        .stat span { font-size: 0.7rem; text-transform: uppercase; color: #5B6B73; }
        .stat strong { display: block; font-size: 1.5rem; margin-top: 0.25rem; color: #0E9E8E; }
        table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #E8DFD0; border-radius: 12px; overflow: hidden; }
        th, td { padding: 0.75rem 1rem; border-bottom: 1px solid #E8DFD0; text-align: left; font-size: 0.88rem; }
        th { background: #F8F3EA; font-size: 0.72rem; text-transform: uppercase; color: #5B6B73; }
        .warn { color: #F2742C; font-weight: 600; }
        .bar { height: 8px; background: #F4ECDE; border-radius: 4px; overflow: hidden; min-width: 80px; }
        .bar i { display: block; height: 100%; background: #1FA85B; border-radius: 4px; }
        .bar.low i { background: #F2742C; }
        a { color: #0E9E8E; font-weight: 600; }
      </style>
    </head>
    <body>
      <div class="banner"><strong>Synthetic demo only.</strong> Not official CPIMS. No real individuals or case records.</div>
      <main>
        <h1>CPIMS Operations Dashboard</h1>
        <p>Case completeness, duplicate flags, and quality metrics.</p>
        <div class="stats" id="stats">Loading...</div>
        <table>
          <thead><tr><th>Case #</th><th>Child</th><th>County</th><th>Status</th><th>Completeness</th></tr></thead>
          <tbody id="cases"><tr><td colspan="5">Loading...</td></tr></tbody>
        </table>
        <p style="margin-top:1.25rem"><a href="/">Home</a> · <a href="/docs">API docs</a></p>
      </main>
      <script>
        fetch('/api/v1/reports/data-quality').then(r => r.json()).then(q => {
          document.getElementById('stats').innerHTML = `
            <div class="stat"><span>Total cases</span><strong>${q.total_cases}</strong></div>
            <div class="stat"><span>Avg completeness</span><strong>${q.completeness_average}%</strong></div>
            <div class="stat"><span>Duplicates flagged</span><strong>${q.duplicate_candidates}</strong></div>`;
        });
        fetch('/api/v1/cases').then(r => r.json()).then(async cases => {
          const scores = await Promise.all(
            cases.map(c => fetch(`/api/v1/cases/${c.id}/completeness`).then(r => r.json()))
          );
          const scoreMap = Object.fromEntries(scores.map(s => [s.case_id, s.completeness_score]));
          document.getElementById('cases').innerHTML = cases.map(c => {
            const score = scoreMap[c.id] ?? 0;
            const low = score < 70;
            return `<tr>
              <td>${c.case_number}</td>
              <td>${c.child_first_name} ${c.child_last_name}</td>
              <td>${c.county || '—'}</td>
              <td>${c.status}</td>
              <td><div class="bar ${low ? 'low' : ''}"><i style="width:${score}%"></i></div> <span class="${low ? 'warn' : ''}">${score}%</span></td>
            </tr>`;
          }).join('');
        });
      </script>
    </body>
    </html>
    """
