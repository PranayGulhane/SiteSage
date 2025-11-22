# SiteSage Architecture Documentation

## System Architecture Overview

SiteSage is built using a modern microservices architecture with clear separation between frontend, backend, and data layers.

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Next.js Frontend (Port 5000)                 │    │
│  │  - React 18 + TypeScript                             │    │
│  │  - TailwindCSS for styling                           │    │
│  │  - Server-side rendering                             │    │
│  └──────────────────┬──────────────────────────────────┘    │
└────────────────────│────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│                      APPLICATION LAYER                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         FastAPI Backend (Port 8000)                  │    │
│  │                                                       │    │
│  │  ┌──────────────┐  ┌──────────────┐                │    │
│  │  │   Crawler    │  │  SEO Scorer  │                │    │
│  │  │   Service    │  │   Service    │                │    │
│  │  └──────────────┘  └──────────────┘                │    │
│  │                                                       │    │
│  │  ┌──────────────┐  ┌──────────────┐                │    │
│  │  │     AI       │  │     PDF      │                │    │
│  │  │   Service    │  │  Generator   │                │    │
│  │  └──────────────┘  └──────────────┘                │    │
│  │                                                       │    │
│  └─────────────┬────────────────┬──────────────────────┘    │
└────────────────│────────────────│─────────────────────────── │
                 │                │
         ┌───────▼────────┐  ┌───▼──────────┐
         │   PostgreSQL   │  │  Groq API    │
         │   Database     │  │  (LLM)       │
         └────────────────┘  └──────────────┘
```

## Component Architecture

### 1. Frontend Layer (Next.js)

**Technology**: Next.js 14 with App Router, React 18, TypeScript, TailwindCSS

**Key Components**:

```
frontend/src/app/
├── layout.tsx           # Root layout with global styles
├── page.tsx             # Home page with URL submission form
├── reports/
│   ├── page.tsx         # Reports list view
│   └── [id]/
│       └── page.tsx     # Report detail view
└── globals.css          # Global Tailwind styles
```

**Responsibilities**:
- User interface rendering
- Form validation and submission
- Real-time updates (polling for report status)
- Data visualization
- Responsive design

**API Integration**:
- Uses Next.js rewrites to proxy `/api/*` requests to backend
- Axios/Fetch for HTTP requests
- React Query for data fetching and caching

---

### 2. Backend Layer (FastAPI)

**Technology**: Python 3.11, FastAPI, SQLAlchemy, Alembic

**Module Structure**:

```
backend/app/
├── main.py              # FastAPI app, routes, background tasks
├── config.py            # Configuration management
├── database.py          # Database connection & session
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── crawler.py           # Web crawler service
├── seo_scorer.py        # SEO scoring engine
├── ai_service.py        # AI insights generator
└── pdf_generator.py     # PDF report generator
```

**Core Services**:

#### 2.1 Web Crawler Service

**File**: `crawler.py`

**Purpose**: Asynchronously crawl websites and extract SEO data

**Key Features**:
- Async HTTP requests using `aiohttp`
- HTML parsing with BeautifulSoup4
- Extracts: title, meta, headings, images, links
- Checks for broken links (parallel requests)
- Measures page load time and size

**Process Flow**:
```
URL Input → Fetch HTML → Parse with BeautifulSoup →
Extract Data → Check Broken Links → Return SEO Data
```

#### 2.2 SEO Scoring Engine

**File**: `seo_scorer.py`

**Purpose**: Calculate SEO quality scores based on multiple factors

**Scoring Algorithm**:

```python
Total Score (100) = Weighted Sum of:
- Title Score (15%)
- Meta Description Score (15%)
- Headings Score (20%)
- Images Score (20%)
- Links Score (15%)
- Performance Score (15%)
```

**Grading System**:
- A: 90-100 (Excellent)
- B: 80-89 (Good)
- C: 70-79 (Average)
- D: 60-69 (Poor)
- F: Below 60 (Critical Issues)

#### 2.3 AI Insights Service

**File**: `ai_service.py`

**Purpose**: Generate AI-powered SEO recommendations

**Technology**: LangChain + Groq (llama-3.3-70b-versatile)

**Process**:
1. Receives SEO data and scores
2. Constructs prompts for LLM
3. Generates:
   - 2-3 paragraph summary
   - 3-5 specific recommendations
4. Returns structured insights

**LLM Prompt Strategy**:
- Context-rich prompts with all SEO metrics
- Structured output format
- Temperature: 0.7 for balanced creativity

#### 2.4 PDF Report Generator

**File**: `pdf_generator.py`

**Purpose**: Create professional PDF reports

**Technology**: ReportLab

**Report Structure**:
1. Header (title, logo)
2. Metadata (URL, date, ID)
3. Score summary (overall score, grade)
4. AI insights (summary, recommendations)
5. Technical details (table format)

---

### 3. Data Layer

#### 3.1 Database Schema (PostgreSQL)

**Models** (`models.py`):

```python
Report (Main Entity)
├── id (PK)
├── url
├── status (pending/processing/completed/failed)
├── seo_score
├── created_at
├── completed_at
├── error_message
└── Relationships:
    ├── seo_data (1-to-1)
    └── ai_insights (1-to-1)

SEOData (Extracted Data)
├── id (PK)
├── report_id (FK)
├── title
├── meta_description
├── h1_tags (JSON)
├── h2_tags (JSON)
├── images (JSON)
├── total_images
├── images_without_alt
├── internal_links (JSON)
├── external_links (JSON)
├── broken_links (JSON)
├── total_links
├── broken_links_count
├── load_time
└── page_size

AIInsight (AI-Generated Content)
├── id (PK)
├── report_id (FK)
├── summary
├── recommendations (JSON)
├── model_used
└── generated_at
```

**Relationships**:
- Report → SEOData: One-to-One
- Report → AIInsight: One-to-One
- Cascade delete enabled (deleting report removes related data)

#### 3.2 Database Migrations (Alembic)

**Location**: `backend/alembic/`

**Migration Flow**:
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Current Migrations**:
- `initial_migration.py`: Creates reports, seo_data, ai_insights tables

---

## Request Flow

### Typical Request Lifecycle

#### 1. Submit URL for Analysis

```
User (Frontend)
  │
  ├─► POST /api/reports {"url": "https://example.com"}
  │
  ▼
FastAPI Backend
  │
  ├─► Create Report (status: pending)
  ├─► Save to PostgreSQL
  ├─► Return Report ID
  │
  ▼
Background Task (async)
  │
  ├─► Update status to "processing"
  ├─► WebCrawler.crawl(url)
  │   ├─► Fetch HTML
  │   ├─► Extract SEO data
  │   └─► Check broken links
  │
  ├─► SEOScorer.calculate_score(seo_data)
  │   ├─► Score each category
  │   └─► Calculate overall score
  │
  ├─► AIInsightGenerator.generate_insights()
  │   ├─► Call Groq API via LangChain
  │   └─► Parse recommendations
  │
  ├─► Save SEOData to DB
  ├─► Save AIInsight to DB
  ├─► Update Report (status: completed, seo_score)
  └─► Complete
```

#### 2. View Report

```
User (Frontend)
  │
  ├─► GET /api/reports/{id}
  │
  ▼
FastAPI Backend
  │
  ├─► Query Report from PostgreSQL
  ├─► Join with SEOData and AIInsight
  └─► Return complete report JSON
      │
      ▼
Frontend
  │
  ├─► Render report details
  ├─► Display score with grade
  ├─► Show AI insights
  └─► Show technical details
```

#### 3. Download PDF

```
User (Frontend)
  │
  ├─► GET /api/reports/{id}/pdf
  │
  ▼
FastAPI Backend
  │
  ├─► Retrieve Report data
  ├─► PDFGenerator.generate_report()
  │   ├─► Create PDF with ReportLab
  │   └─► Save to reports/ directory
  │
  └─► Return PDF file
      │
      ▼
User's Browser
  └─► Download PDF
```

---

## Scalability Considerations

### Current Architecture (Single Instance)

- **Frontend**: Single Next.js server
- **Backend**: Single FastAPI server
- **Database**: Single PostgreSQL instance

### Scaling Strategies

#### Horizontal Scaling (Multiple Instances)

1. **Frontend**:
   - Deploy multiple Next.js instances
   - Use load balancer (AWS ALB/ELB)
   - Session state in cookies (stateless)

2. **Backend**:
   - Deploy multiple FastAPI instances
   - Use load balancer
   - Background tasks via Celery + Redis

3. **Database**:
   - Read replicas for GET requests
   - Write to primary, read from replicas
   - Connection pooling (PgBouncer)

#### Vertical Scaling

- Increase instance sizes (more CPU/RAM)
- Optimize database queries
- Add indexes for frequently queried fields

#### Caching Layer

```
User → CloudFront CDN → Next.js
                ↓
          Redis Cache → FastAPI → PostgreSQL
```

- Cache completed reports (TTL: 1 hour)
- Cache AI responses for duplicate URLs
- CDN for static assets

---

## Security Architecture

### 1. Authentication & Authorization

**Current**: No authentication (public API)

**Future Enhancements**:
- JWT-based authentication
- API key system for programmatic access
- Role-based access control (RBAC)

### 2. Data Security

- **In Transit**: HTTPS/TLS for all communications
- **At Rest**: PostgreSQL encryption
- **Secrets**: Environment variables, AWS Secrets Manager

### 3. Rate Limiting

```python
# Future implementation
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/reports")
@limiter.limit("10/minute")
def create_report():
    ...
```

### 4. Input Validation

- Pydantic schemas validate all inputs
- URL validation prevents malicious URLs
- SQL injection prevented by ORM (SQLAlchemy)
- XSS prevention in frontend (React auto-escaping)

---

## Performance Optimization

### 1. Database Optimization

- **Indexes**: Created on `reports.url`, `reports.id`
- **Connection Pooling**: SQLAlchemy pool
- **Query Optimization**: Eager loading relationships

### 2. Async Processing

- **Crawler**: Async HTTP requests (aiohttp)
- **Link Checking**: Parallel requests
- **Background Tasks**: FastAPI BackgroundTasks

### 3. Frontend Optimization

- **Code Splitting**: Next.js automatic
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Dynamic imports
- **Caching**: Browser caching headers

---

## Monitoring & Observability

### Logging

**Backend**:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**Frontend**:
- Console errors logged
- Sentry for error tracking (optional)

### Metrics

**Key Metrics to Track**:
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- AI API latency
- Active reports count

### Health Checks

```python
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": check_db_connection()
    }
```

---

## Deployment Architecture

### Development

```
Developer Machine
├── Backend (localhost:8000)
├── Frontend (localhost:5000)
└── PostgreSQL (localhost:5432)
```

### Production (AWS)

```
AWS Cloud
├── Amplify (Frontend)
│   └── CloudFront CDN
│
├── Elastic Beanstalk (Backend)
│   ├── Auto Scaling Group
│   ├── Load Balancer
│   └── EC2 Instances
│
└── RDS PostgreSQL
    ├── Primary Instance
    └── Read Replicas (optional)
```

---

## Technology Decisions

### Why Next.js?
- Server-side rendering for SEO
- File-based routing
- Built-in API routes
- Excellent developer experience
- Vercel/Amplify deployment support

### Why FastAPI?
- High performance (async support)
- Automatic API documentation (OpenAPI)
- Type safety with Pydantic
- Easy to test
- Modern Python features

### Why PostgreSQL?
- ACID compliance
- JSON support for flexible data
- Robust and reliable
- Excellent ORM support (SQLAlchemy)
- Wide cloud provider support

### Why Groq?
- Ultra-fast inference (faster than OpenAI)
- Cost-effective
- High-quality models (Llama-3.3)
- Easy LangChain integration

---

## Future Enhancements

1. **User Authentication**
   - User accounts and login
   - Report ownership
   - Usage limits per user

2. **Real-time Updates**
   - WebSocket connections
   - Live progress updates
   - No polling required

3. **Scheduled Scans**
   - Cron-like scheduling
   - Automated re-scans
   - Email notifications

4. **Batch Processing**
   - Upload CSV of URLs
   - Bulk analysis
   - Aggregate reports

5. **Historical Tracking**
   - Track score changes over time
   - Trend analysis
   - Improvement suggestions

6. **Advanced SEO Features**
   - Mobile-friendliness check
   - Schema markup validation
   - Core Web Vitals
   - Sitemap analysis

---

## Conclusion

SiteSage's architecture is designed for:
- **Maintainability**: Clear separation of concerns
- **Scalability**: Horizontal and vertical scaling options
- **Performance**: Async processing, efficient queries
- **Reliability**: Error handling, retries, health checks
- **Security**: Input validation, secure secrets management

The modular design allows for easy extension and modification of individual components without affecting the entire system.
