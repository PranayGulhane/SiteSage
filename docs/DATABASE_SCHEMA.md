# Database Schema

## Tables

### reports
- **id**: Integer, primary key
- **url**: String (2048), not nullable
- **status**: String (50), default "pending" (possible values: pending, processing, completed, failed)
- **seo_score**: Float, nullable
- **created_at**: DateTime, default value is the current time
- **completed_at**: DateTime, nullable
- **error_message**: Text, nullable

### seo_data
- **id**: Integer, primary key
- **report_id**: Integer, Foreign Key referencing `reports.id`, unique
- **title**: String (500), nullable
- **meta_description**: Text, nullable
- **h1_tags**: JSON, nullable
- **h2_tags**: JSON, nullable
- **images**: JSON, nullable
- **total_images**: Integer, default 0
- **images_without_alt**: Integer, default 0
- **internal_links**: JSON, nullable
- **external_links**: JSON, nullable
- **broken_links**: JSON, nullable
- **total_links**: Integer, default 0
- **broken_links_count**: Integer, default 0
- **load_time**: Float, nullable
- **page_size**: Integer, nullable

### ai_insights
- **id**: Integer, primary key
- **report_id**: Integer, Foreign Key referencing `reports.id`, unique
- **summary**: Text, nullable
- **recommendations**: JSON, nullable
- **model_used**: String (100), nullable
- **generated_at**: DateTime, nullable

## Relationships
- **reports** has one `seo_data` and one `ai_insights` associated.