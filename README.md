# SiteSage - Automated SEO Performance Analyzer

<div align="center">

![SiteSage](https://img.shields.io/badge/SiteSage-SEO%20Analyzer-blue)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Next.js](https://img.shields.io/badge/Next.js-14.1-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)

**Production-grade SEO analysis platform powered by AI**

[Features](#features) • [Tech Stack](#tech-stack) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Deployment](#deployment)

</div>

---

## 🚀 Features

- **🔍 Deep Website Analysis**: Asynchronous crawling extracts comprehensive SEO data including:
  - Page titles and meta descriptions
  - Heading structure (H1/H2 tags)
  - Image optimization (alt tags, counts)
  - Internal and external links
  - Broken link detection
  - Page load time and performance metrics

- **🤖 AI-Powered Insights**: LangChain + Groq integration provides:
  - 2-3 paragraph SEO summary
  - 3-5 specific optimization recommendations
  - Context-aware analysis based on industry best practices

- **📊 Comprehensive Scoring**: Intelligent SEO scoring algorithm evaluates:
  - Title optimization (0-100 score)
  - Meta description quality
  - Heading structure
  - Image alt tag coverage
  - Link health
  - Performance metrics

- **📄 PDF Reports**: Generate professional PDF reports with ReportLab

- **💾 Full History**: PostgreSQL database stores all analyses for tracking improvements

- **🎨 Modern Dashboard**: Next.js + TailwindCSS interface with:
  - URL submission form
  - Reports table with filtering
  - Detailed report views
  - Responsive design

---

## 🛠 Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TailwindCSS 3** - Utility-first CSS
- **TypeScript** - Type safety
- **Jest** - Testing framework

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Programming language
- **LangChain** - AI/LLM orchestration
- **Groq** - Fast LLM inference
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **BeautifulSoup4** - HTML parsing
- **aiohttp** - Async HTTP client
- **ReportLab** - PDF generation
- **Pytest** - Testing framework

### Database & Storage
- **PostgreSQL 14** - Primary database
- **Local file storage** - PDF reports

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Uvicorn** - ASGI server

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Groq API Key ([Get one here](https://console.groq.com/keys))

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd sitesage
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your DATABASE_URL and GROQ_API_KEY

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5000`

### 4. Access the Application

Open your browser and navigate to:
- **Frontend Dashboard**: http://localhost:5000
- **Backend API Docs**: http://localhost:8000/docs

---

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

```bash
# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:5000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

---

## 📚 Documentation

### API Endpoints

#### Health Check
```http
GET /
```

Returns application health status.

#### Submit URL for Analysis
```http
POST /api/reports
Content-Type: application/json

{
  "url": "https://example.com"
}
```

Returns: `201 Created` with report object

#### List All Reports
```http
GET /api/reports?skip=0&limit=50
```

Returns: Array of report summaries

#### Get Report Details
```http
GET /api/reports/{report_id}
```

Returns: Complete report with SEO data and AI insights

#### Download PDF Report
```http
GET /api/reports/{report_id}/pdf
```

Returns: PDF file

#### Delete Report
```http
DELETE /api/reports/{report_id}
```

Returns: `204 No Content`

### Database Schema

See [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for detailed schema information.

### Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system architecture details.

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage  # With coverage
```

---

## 🚀 Deployment

### AWS Amplify Deployment

See [docs/AWS_AMPLIFY_DEPLOYMENT.md](docs/AWS_AMPLIFY_DEPLOYMENT.md) for complete deployment guide.

### Other Platforms

- **Vercel** (Frontend): Configure with Next.js preset
- **Railway/Render** (Backend): Use `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Heroku**: Add Procfile with `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📁 Project Structure

```
sitesage/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app & routes
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crawler.py       # Web crawler
│   │   ├── seo_scorer.py    # SEO scoring engine
│   │   ├── ai_service.py    # AI insights generator
│   │   └── pdf_generator.py # PDF report generator
│   ├── alembic/             # Database migrations
│   ├── tests/               # Pytest tests
│   └── requirements.txt
│
├── frontend/                # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx     # Home page
│   │   │   └── reports/     # Reports pages
│   │   └── __tests__/       # Jest tests
│   ├── public/
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── docs/                    # Documentation
├── reports/                 # Generated PDF reports
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/sitesage
GROQ_API_KEY=your_groq_api_key
DEBUG=False
```

#### Frontend

API endpoints are proxied through Next.js config.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference
- **LangChain** - LLM application framework
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **TailwindCSS** - CSS framework

---

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Contact: support@sitesage.com

---

<div align="center">

**Built with ❤️ by the SiteSage Team**

</div>
