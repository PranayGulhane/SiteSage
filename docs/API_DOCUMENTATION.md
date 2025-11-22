# SiteSage API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://your-backend-url.com
```

## Authentication

Currently, the API is open and does not require authentication.

**Future**: JWT-based authentication will be implemented.

---

## Endpoints

### 1. Health Check

Check API health and database connectivity.

#### Request

```http
GET /
```

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

#### Status Codes

- `200 OK`: Service is healthy
- `503 Service Unavailable`: Database connection failed

---

### 2. Create Report

Submit a URL for SEO analysis.

#### Request

```http
POST /api/reports
Content-Type: application/json

{
  "url": "https://example.com"
}
```

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| url | string (URL) | Yes | The URL to analyze |

#### Response

```json
{
  "id": 1,
  "url": "https://example.com",
  "status": "pending",
  "seo_score": null,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": null,
  "seo_data": null,
  "ai_insights": null
}
```

#### Status Codes

- `201 Created`: Report created successfully
- `422 Unprocessable Entity`: Invalid URL format

#### Example

```bash
curl -X POST http://localhost:8000/api/reports \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

### 3. List Reports

Get a paginated list of all reports.

#### Request

```http
GET /api/reports?skip=0&limit=50
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip |
| limit | integer | 50 | Maximum number of records to return |

#### Response

```json
[
  {
    "id": 1,
    "url": "https://example.com",
    "status": "completed",
    "seo_score": 85.5,
    "created_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:31:30Z"
  },
  {
    "id": 2,
    "url": "https://another-site.com",
    "status": "processing",
    "seo_score": null,
    "created_at": "2024-01-15T11:00:00Z",
    "completed_at": null
  }
]
```

#### Status Codes

- `200 OK`: Successfully retrieved reports

#### Example

```bash
curl http://localhost:8000/api/reports?skip=0&limit=10
```

---

### 4. Get Report Details

Get complete details of a specific report.

#### Request

```http
GET /api/reports/{report_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| report_id | integer | The ID of the report |

#### Response

```json
{
  "id": 1,
  "url": "https://example.com",
  "status": "completed",
  "seo_score": 85.5,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:30Z",
  "seo_data": {
    "title": "Example Domain",
    "meta_description": "This domain is for use in illustrative examples",
    "h1_tags": ["Example Domain"],
    "h2_tags": [],
    "total_images": 0,
    "images_without_alt": 0,
    "total_links": 1,
    "broken_links_count": 0,
    "load_time": 0.45,
    "page_size": 1256
  },
  "ai_insights": {
    "summary": "The website has a good basic structure...",
    "recommendations": [
      "Add more descriptive meta description",
      "Include H2 subheadings for better content structure",
      "Optimize page load time by implementing caching"
    ],
    "model_used": "llama-3.3-70b-versatile"
  }
}
```

#### Status Codes

- `200 OK`: Successfully retrieved report
- `404 Not Found`: Report with given ID does not exist

#### Example

```bash
curl http://localhost:8000/api/reports/1
```

---

### 5. Download PDF Report

Download a PDF version of the report.

#### Request

```http
GET /api/reports/{report_id}/pdf
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| report_id | integer | The ID of the report |

#### Response

Binary PDF file

#### Headers

```
Content-Type: application/pdf
Content-Disposition: attachment; filename=sitesage_report_1.pdf
```

#### Status Codes

- `200 OK`: PDF generated and returned
- `404 Not Found`: Report does not exist
- `400 Bad Request`: Report not yet completed

#### Example

```bash
curl http://localhost:8000/api/reports/1/pdf -o report.pdf
```

---

### 6. Delete Report

Delete a report and all associated data.

#### Request

```http
DELETE /api/reports/{report_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| report_id | integer | The ID of the report to delete |

#### Response

No content (empty response body)

#### Status Codes

- `204 No Content`: Report successfully deleted
- `404 Not Found`: Report does not exist

#### Example

```bash
curl -X DELETE http://localhost:8000/api/reports/1
```

---

## Data Models

### Report Object

```typescript
interface Report {
  id: number;
  url: string;
  status: "pending" | "processing" | "completed" | "failed";
  seo_score: number | null;
  created_at: string;  // ISO 8601 datetime
  completed_at: string | null;  // ISO 8601 datetime
  error_message?: string;
  seo_data?: SEOData;
  ai_insights?: AIInsight;
}
```

### SEOData Object

```typescript
interface SEOData {
  title: string | null;
  meta_description: string | null;
  h1_tags: string[];
  h2_tags: string[];
  total_images: number;
  images_without_alt: number;
  total_links: number;
  broken_links_count: number;
  load_time: number | null;  // in seconds
  page_size: number | null;  // in bytes
}
```

### AIInsight Object

```typescript
interface AIInsight {
  summary: string | null;
  recommendations: string[];
  model_used: string | null;
}
```

---

## Report Status Lifecycle

```
pending → processing → completed
                    ↘
                      failed
```

1. **pending**: Report created, waiting to be processed
2. **processing**: Crawler is actively analyzing the URL
3. **completed**: Analysis finished successfully
4. **failed**: Analysis encountered an error

---

## Error Responses

### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "invalid or missing URL scheme",
      "type": "value_error.url.scheme"
    }
  ]
}
```

### Not Found (404)

```json
{
  "detail": "Report not found"
}
```

### Server Error (500)

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

**Current**: No rate limiting implemented

**Future**: 
- 100 requests per hour per IP
- 10 report creations per hour per IP

---

## Pagination

List endpoints support pagination using `skip` and `limit` parameters:

```http
GET /api/reports?skip=20&limit=10
```

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 50, max: 100)

---

## Webhooks

**Status**: Not yet implemented

**Future**: Webhook support for report completion notifications

```json
{
  "event": "report.completed",
  "report_id": 1,
  "url": "https://example.com",
  "seo_score": 85.5,
  "timestamp": "2024-01-15T10:31:30Z"
}
```

---

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Code Examples

### Python

```python
import requests

# Create report
response = requests.post(
    "http://localhost:8000/api/reports",
    json={"url": "https://example.com"}
)
report = response.json()
report_id = report["id"]

# Get report details
report = requests.get(f"http://localhost:8000/api/reports/{report_id}").json()

# Download PDF
pdf = requests.get(f"http://localhost:8000/api/reports/{report_id}/pdf")
with open("report.pdf", "wb") as f:
    f.write(pdf.content)
```

### JavaScript/TypeScript

```typescript
// Create report
const createReport = async (url: string) => {
  const response = await fetch('/api/reports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  return await response.json();
};

// Get report details
const getReport = async (id: number) => {
  const response = await fetch(`/api/reports/${id}`);
  return await response.json();
};

// Download PDF
const downloadPDF = (id: number) => {
  window.open(`/api/reports/${id}/pdf`, '_blank');
};
```

### cURL

```bash
# Create report
curl -X POST http://localhost:8000/api/reports \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# List reports
curl http://localhost:8000/api/reports

# Get report details
curl http://localhost:8000/api/reports/1

# Download PDF
curl http://localhost:8000/api/reports/1/pdf -o report.pdf

# Delete report
curl -X DELETE http://localhost:8000/api/reports/1
```

---

## CORS Configuration

The API allows cross-origin requests from:

- `http://localhost:5000` (development frontend)
- `http://127.0.0.1:5000`

Additional origins can be configured in `backend/app/config.py`:

```python
cors_origins: list = [
    "http://localhost:5000",
    "https://your-production-domain.com"
]
```

---

## Versioning

**Current Version**: v1 (no version prefix in URL)

**Future**: API versioning will be implemented:
- `/v1/api/reports`
- `/v2/api/reports`

---

## Support

For API issues or questions:
- GitHub Issues: <your-repo-url>/issues
- Email: api-support@sitesage.com
- Documentation: https://docs.sitesage.com
