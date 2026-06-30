# Deploy to Render (free tier)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/dawit-Tegegnwork/cpims-information-management-demo)

## One-click deploy

1. Click **Deploy to Render** above.
2. Render reads [`render.yaml`](../render.yaml) and builds the Docker image.
3. After deploy, open `https://<your-service>.onrender.com/dashboard` — 4 synthetic cases seed on startup.
4. API docs: `https://<your-service>.onrender.com/docs`

## Quick test

```bash
curl https://<your-service>.onrender.com/health
curl https://<your-service>.onrender.com/api/v1/reports/data-quality
```

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `CPIMS_DATABASE_URL` | `sqlite:////tmp/cpims_demo.db` | Ephemeral on free tier |

## Health check

Expected: `{"status":"ok","service":"cpims-information-management-demo"}`

**Synthetic data only** — not official CPIMS. No real individuals.
