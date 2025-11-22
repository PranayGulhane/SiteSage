# SiteSage - Project Overview

## Project Description

SiteSage is a production-grade automated SEO performance analyzer that uses AI to provide actionable insights for website optimization.

## Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18 + TypeScript
- TailwindCSS 3
- Running on port 5000

**Backend:**
- FastAPI (Python 3.11)
- LangChain + Groq AI (llama-3.3-70b-versatile)
- PostgreSQL + Alembic migrations
- Running on port 8000

**Testing:**
- Pytest (backend)
- Jest + React Testing Library (frontend)

## Project Structure

```
/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API routes & app
│   │   ├── crawler.py   # Async web crawler
│   │   ├── seo_scorer.py # Scoring engine
│   │   ├── ai_service.py # LangChain/Groq integration
│   │   ├── pdf_generator.py # PDF reports
│   │   ├── models.py    # Database models
│   │   └── database.py  # DB connection
│   ├── tests/           # Pytest tests
│   └── alembic/         # DB migrations
│
├── frontend/            # Next.js frontend
│   ├── src/app/
│   │   ├── page.tsx     # Home page
│   │   └── reports/     # Reports pages
│   └── tests/           # Jest tests
│
├── docs/                # Documentation
│   ├── AWS_AMPLIFY_DEPLOYMENT.md
│   ├── ARCHITECTURE.md
│   └── API_DOCUMENTATION.md
│
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Key Features

1. **URL Crawling**: Asynchronous web crawling with BeautifulSoup
2. **SEO Analysis**: Comprehensive scoring (0-100) across 6 categories
3. **AI Insights**: LangChain + Groq generates summaries and recommendations
4. **PDF Reports**: Professional reports with ReportLab
5. **Database**: PostgreSQL with Alembic migrations
6. **Modern UI**: Responsive Next.js dashboard

## Environment Variables

**Backend (.env):**
- `DATABASE_URL`: PostgreSQL connection string (auto-configured in Replit)
- `GROQ_API_KEY`: Groq API key (configured in Secrets)
- `GROQ_MODEL`: llama-3.3-70b-versatile

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: http://localhost:8000

## Running the Application

Both workflows are configured and auto-start:

1. **Backend API** (port 8000):
   ```bash
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend Dashboard** (port 5000):
   ```bash
   cd frontend && npm run dev
   ```

Access the app at the Webview (port 5000).

## Database

PostgreSQL database is auto-configured with Replit's built-in database.

### Migrations

```bash
cd backend
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

### Schema

- **reports**: Main report entity
- **seo_data**: Extracted SEO data (1-to-1 with reports)
- **ai_insights**: AI-generated insights (1-to-1 with reports)

## Testing

**Backend:**
```bash
cd backend
pytest                    # Run all tests
pytest --cov=app         # With coverage
```

**Frontend:**
```bash
cd frontend
npm test                 # Run Jest tests
npm run test:coverage   # With coverage
```

## API Endpoints

- `GET /` - Health check
- `POST /api/reports` - Submit URL for analysis
- `GET /api/reports` - List all reports
- `GET /api/reports/{id}` - Get report details
- `GET /api/reports/{id}/pdf` - Download PDF
- `DELETE /api/reports/{id}` - Delete report

Full API docs: http://localhost:8000/docs

## Deployment

### Docker Compose

```bash
docker-compose up -d
```

### AWS Amplify

See `docs/AWS_AMPLIFY_DEPLOYMENT.md` for complete guide.

## User Preferences

None specified yet.

## Recent Changes

- Initial project setup (2024-11-22)
- Implemented all core features
- Added comprehensive tests
- Created Docker configuration
- Written complete documentation
- Fixed frontend-backend integration with Next.js rewrites

## Known Issues

None at this time. All core functionality is working.

## Future Enhancements

1. User authentication
2. Real-time WebSocket updates
3. Scheduled re-scans
4. Batch URL processing
5. Historical tracking
6. Mobile-friendliness check
