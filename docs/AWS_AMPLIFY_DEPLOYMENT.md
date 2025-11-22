# AWS Amplify Deployment Guide for SiteSage

This guide provides step-by-step instructions for deploying the SiteSage application on AWS Amplify, including both the frontend (Next.js) and backend (FastAPI).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Backend Deployment (AWS Elastic Beanstalk)](#backend-deployment)
4. [Database Setup (AWS RDS PostgreSQL)](#database-setup)
5. [Frontend Deployment (AWS Amplify)](#frontend-deployment)
6. [Environment Configuration](#environment-configuration)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring & Logs](#monitoring--logs)
9. [Cost Estimation](#cost-estimation)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- GitHub/GitLab repository with your code
- Groq API key
- Domain name (optional, for custom domain)

---

## Architecture Overview

```
┌─────────────────┐
│   CloudFront    │ (CDN)
└────────┬────────┘
         │
┌────────▼────────┐
│  AWS Amplify    │ (Next.js Frontend)
│   Port 5000     │
└────────┬────────┘
         │
         │ API Calls
         │
┌────────▼────────────┐
│  Elastic Beanstalk  │ (FastAPI Backend)
│      Port 8000      │
└────────┬────────────┘
         │
┌────────▼────────┐
│   RDS Postgres  │ (Database)
└─────────────────┘
```

---

## Backend Deployment

### Step 1: Prepare Backend for AWS

#### 1.1 Create `Procfile`

Create a file named `Procfile` in the `backend/` directory:

```
web: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 1.2 Create `runtime.txt`

```
python-3.11
```

#### 1.3 Update `requirements.txt`

Ensure all dependencies are listed in `backend/requirements.txt`.

#### 1.4 Create `.ebignore`

```
__pycache__/
*.py[cod]
.pytest_cache/
tests/
.env
*.log
```

### Step 2: Initialize Elastic Beanstalk

```bash
cd backend

# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p python-3.11 sitesage-backend --region us-east-1

# Create environment
eb create sitesage-backend-prod \
  --instance-type t3.medium \
  --database.engine postgres \
  --database.size 20 \
  --envvars GROQ_API_KEY=your_groq_key
```

### Step 3: Configure Environment

```bash
# Set environment variables
eb setenv \
  GROQ_API_KEY=your_groq_api_key \
  DATABASE_URL=your_rds_connection_string \
  DEBUG=False

# Deploy backend
eb deploy
```

### Step 4: Run Database Migrations

```bash
# SSH into EB instance
eb ssh

# Run migrations
cd /var/app/current
source /var/app/venv/*/bin/activate
alembic upgrade head

# Exit
exit
```

---

## Database Setup (AWS RDS PostgreSQL)

### Option 1: Using EB Integrated Database (Simple)

The database is automatically created when using `--database.engine` flag during `eb create`.

### Option 2: Standalone RDS (Production Recommended)

#### 2.1 Create RDS Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier sitesage-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 14.7 \
  --master-username sitesageadmin \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 20 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --publicly-accessible \
  --backup-retention-period 7
```

#### 2.2 Get Connection String

```bash
aws rds describe-db-instances \
  --db-instance-identifier sitesage-postgres \
  --query 'DBInstances[0].Endpoint'
```

Connection string format:
```
postgresql://sitesageadmin:YourPassword@endpoint:5432/sitesage
```

#### 2.3 Create Database

```bash
# Connect to RDS
psql -h your-rds-endpoint.rds.amazonaws.com -U sitesageadmin -d postgres

# Create database
CREATE DATABASE sitesage;
\q
```

---

## Frontend Deployment (AWS Amplify)

### Step 1: Connect Repository to Amplify

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **New App** > **Host web app**
3. Select your Git provider (GitHub/GitLab/Bitbucket)
4. Authorize AWS Amplify to access your repository
5. Select the **sitesage** repository and **main** branch

### Step 2: Configure Build Settings

Update the auto-detected build settings:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

### Step 3: Add Environment Variables

In Amplify Console, go to **App settings** > **Environment variables**:

```
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-backend-url.elasticbeanstalk.com
```

### Step 4: Configure Rewrites (API Proxy)

Create `frontend/public/amplify.yml`:

```yaml
version: 1
frontend:
  phases:
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
customHeaders:
  - pattern: '**/*'
    headers:
      - key: 'Cache-Control'
        value: 'no-cache'
```

### Step 5: Update Frontend API Configuration

Update `frontend/next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
```

### Step 6: Deploy

```bash
# Amplify will auto-deploy on every push to main branch
git add .
git commit -m "Configure for AWS Amplify"
git push origin main
```

Your frontend will be deployed at: `https://main.xxxxxxxxx.amplifyapp.com`

---

## Environment Configuration

### Backend Environment Variables

Set these in Elastic Beanstalk:

```bash
eb setenv \
  DATABASE_URL="postgresql://user:pass@endpoint:5432/sitesage" \
  GROQ_API_KEY="your_groq_api_key" \
  GROQ_MODEL="llama-3.3-70b-versatile" \
  DEBUG="False" \
  REPORTS_DIR="/tmp/reports"
```

### Frontend Environment Variables

Set these in Amplify Console:

```
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-backend.elasticbeanstalk.com
```

---

## CI/CD Pipeline

### Automated Deployment

Both Amplify (frontend) and Elastic Beanstalk (backend) support Git-based auto-deployment:

1. **Frontend**: Every push to `main` triggers Amplify build
2. **Backend**: Configure CodePipeline for EB auto-deploy

### Manual Backend Deployment

```bash
cd backend
eb deploy
```

---

## Monitoring & Logs

### Backend Logs (Elastic Beanstalk)

```bash
# View logs
eb logs

# Stream logs
eb logs --stream

# Download logs
eb logs --all
```

Or use CloudWatch Logs:
1. Go to CloudWatch Console
2. Navigate to Log Groups
3. Find `/aws/elasticbeanstalk/sitesage-backend-prod`

### Frontend Logs (Amplify)

1. Go to Amplify Console
2. Select your app
3. Click on the build
4. View build logs and runtime logs

### Database Monitoring (RDS)

1. Go to RDS Console
2. Select your instance
3. View **Monitoring** tab for metrics
4. Enable Enhanced Monitoring for detailed metrics

---

## Cost Estimation

### Monthly AWS Costs (Approximate)

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **Elastic Beanstalk** | t3.medium instance | ~$35 |
| **RDS PostgreSQL** | db.t3.micro, 20GB | ~$15 |
| **Amplify Hosting** | Build minutes + hosting | ~$1-5 |
| **Data Transfer** | 50GB outbound | ~$4.50 |
| **CloudWatch Logs** | 5GB | ~$2.50 |
| **TOTAL** | | **~$58-62/month** |

### Cost Optimization Tips

1. Use **RDS Aurora Serverless** for variable workloads
2. Enable **Auto Scaling** for EB instances
3. Use **CloudFront** for caching (included with Amplify)
4. Set up **Budget Alerts** in AWS Cost Explorer

---

## Troubleshooting

### Issue: Backend Not Connecting to Database

**Solution:**
1. Check security groups allow EB to connect to RDS
2. Verify DATABASE_URL is correct
3. Check RDS is publicly accessible or in same VPC

```bash
# Test connection from EB
eb ssh
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: Frontend Can't Reach Backend

**Solution:**
1. Verify NEXT_PUBLIC_API_URL is set correctly
2. Check CORS settings in FastAPI
3. Ensure backend is healthy: `curl https://your-backend.com/`

### Issue: Database Migration Fails

**Solution:**
```bash
eb ssh
cd /var/app/current
source /var/app/venv/*/bin/activate
alembic upgrade head --sql  # Dry run first
alembic upgrade head
```

### Issue: Build Fails on Amplify

**Solution:**
1. Check build logs in Amplify Console
2. Verify package.json scripts are correct
3. Ensure Node version matches (20.x)

### Issue: "Too Many Requests" from Groq

**Solution:**
1. Implement rate limiting in backend
2. Cache AI responses for duplicate URLs
3. Upgrade Groq plan if needed

---

## Security Best Practices

1. **Secrets Management**: Use AWS Secrets Manager for sensitive values
2. **HTTPS Only**: Enforce SSL/TLS on all endpoints
3. **IAM Roles**: Use least-privilege IAM roles
4. **VPC**: Place RDS in private subnet
5. **WAF**: Enable AWS WAF for DDoS protection
6. **Security Groups**: Restrict inbound rules to necessary ports only

---

## Backup & Disaster Recovery

### Database Backups

```bash
# Enable automated backups (already enabled in RDS)
aws rds modify-db-instance \
  --db-instance-identifier sitesage-postgres \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier sitesage-postgres \
  --db-snapshot-identifier sitesage-backup-$(date +%Y%m%d)
```

### Application Backups

- Elastic Beanstalk: EB automatically maintains previous versions
- Amplify: Git-based, all versions available in repository

---

## Scaling

### Vertical Scaling (Increase Instance Size)

```bash
eb scale 1 --instance-type t3.large
```

### Horizontal Scaling (Add More Instances)

```bash
# Enable auto-scaling
eb config

# In the editor, update:
aws:autoscaling:asg:
  MinSize: 2
  MaxSize: 10
aws:autoscaling:trigger:
  MeasureName: CPUUtilization
  Unit: Percent
  UpperThreshold: 80
  LowerThreshold: 20
```

---

## Custom Domain Setup

### Frontend (Amplify)

1. Go to Amplify Console
2. Domain management > Add domain
3. Follow DNS configuration steps
4. SSL certificate auto-provisioned

### Backend (Elastic Beanstalk)

1. Get EB endpoint: `eb status`
2. Create CNAME record: `api.yourdomain.com` → EB endpoint
3. Or use Route 53 with alias record

---

## Next Steps

1. Set up monitoring alerts (CloudWatch Alarms)
2. Configure CloudFront CDN for better performance
3. Implement API rate limiting
4. Set up staging environment
5. Configure automated backups
6. Enable AWS X-Ray for tracing

---

## Support & Resources

- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS Support](https://console.aws.amazon.com/support/)

---

**Deployment Complete! 🎉**

Your SiteSage application is now running on AWS with high availability, automatic scaling, and robust monitoring.
