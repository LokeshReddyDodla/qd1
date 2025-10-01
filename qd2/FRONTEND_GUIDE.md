# Frontend User Guide

Beautiful, interactive HTML interface for the Patient Data RAG System.

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Make sure services are running
make start

# Start the API
python main.py
```

### 2. Open the Frontend

Open your browser and navigate to:
```
http://localhost:8000
```

The frontend will load automatically at the root path.

Alternative: You can also open `frontend.html` directly in your browser, but you'll need to ensure the API is running on `localhost:8000`.

## 🎨 Interface Overview

The frontend is divided into three main sections:

### 1. **Header & Status Bar**
- Shows system health status
- Displays collection name and point count
- Real-time connection status to the API

### 2. **Data Ingestion Panel (Left)**
- Four tabs for different data sources:
  - **Profile**: Ingest patient profiles
  - **Meals**: Ingest meal reports
  - **Fitness**: Ingest fitness data
  - **Sleep**: Ingest sleep reports
- Each tab has:
  - Info box explaining the data type
  - JSON input textarea
  - "Load Example" button to populate sample data
  - Ingest button
  - Response box showing results

### 3. **Query Panel (Right)**
- Natural language query interface
- Input fields:
  - **Person**: Name or patient UUID
  - **Question**: Your natural language question
  - **Source Filter**: Optional (profile/meals/fitness/sleep)
  - **Results Limit**: Number of evidence chunks (1-50)
  - **From/To Date**: Optional time range filters
- Results display:
  - **Answer**: LLM-generated answer in purple gradient box
  - **Evidence**: Scored chunks with metadata
  - **Query Metadata**: Execution details

### 4. **Collection Statistics (Bottom)**
- Shows current Qdrant collection stats
- Points count, vectors, status
- Refresh button to update

## 📥 Using Data Ingestion

### Step-by-Step: Ingest Patient Profile

1. Click the **Profile** tab
2. Click **Load Example** to populate sample data
3. Review/modify the JSON data
4. Click **Ingest Profiles**
5. Wait for processing
6. Check the green success box for results:
   - Accepted: Number of documents processed
   - Indexed points: Number of chunks created
   - Errors: Any validation errors

### Example Profile JSON

```json
[
  {
    "patient_id": "12345678-1234-1234-1234-123456789abc",
    "first_name": "John",
    "last_name": "Doe",
    "dob": "1980-01-15",
    "gender": "male",
    "height": 178.0,
    "waist": 90,
    "weight": 82,
    "email": "john.doe@example.com",
    "phone_number": "1234567890",
    "locale": "Asia/Kolkata",
    "created_at": "2025-09-30T10:00:00Z",
    "profile_completion": {
      "basic": {"is_complete": true},
      "lifestyle": {"is_complete": true},
      "medical_history": {"is_complete": false}
    }
  }
]
```

### Step-by-Step: Ingest Meals

1. Click the **Meals** tab
2. Click **Load Example**
3. Modify the `patient_id`, `date`, and meal details
4. Click **Ingest Meals**
5. Check results - should create multiple chunks:
   - 1 day summary
   - N meal chunks (one per meal)
   - 1 recommendation chunk

### Step-by-Step: Ingest Fitness

1. Click the **Fitness** tab
2. Click **Load Example**
3. Optional: Check "Include hourly chunks" for hour-by-hour data
4. Click **Ingest Fitness**
5. View results

### Step-by-Step: Ingest Sleep

1. Click the **Sleep** tab
2. Click **Load Example**
3. Update quality analysis data
4. Click **Ingest Sleep**
5. View results

## 🔍 Using Query Interface

### Step-by-Step: Execute a Query

1. Enter the **Person Name** (e.g., "John Doe") or patient UUID
2. Type your **Question** (e.g., "What did John eat for breakfast?")
3. **Optional**: Select a source filter (meals/fitness/sleep/profile)
4. **Optional**: Set date/time range using From/To fields
5. Set **Results Limit** (default: 10)
6. Click **Execute Query**
7. View results:
   - **Answer** in purple box at top
   - **Evidence chunks** below with scores
   - **Metadata** at bottom

### Example Queries

#### Query 1: Meal Information
```
Person: John Doe
Question: What did John eat for breakfast today?
Source: meals
From: 2025-09-30 00:00
To: 2025-09-30 23:59
```

#### Query 2: Fitness Data
```
Person: John Doe
Question: How many steps did John take today?
Source: fitness
From: 2025-09-30 00:00
To: 2025-09-30 23:59
```

#### Query 3: Profile Information
```
Person: John Doe
Question: What is John's height, weight, and BMI?
Source: profile
(No date range needed)
```

#### Query 4: General Health Summary
```
Person: John Doe
Question: Summarize John's health data for September 30th, 2025
Source: (leave blank for all sources)
From: 2025-09-30 00:00
To: 2025-09-30 23:59
```

#### Query 5: Sleep Quality
```
Person: John Doe
Question: How was John's sleep quality last night?
Source: sleep
From: 2025-09-30 00:00
To: 2025-09-30 23:59
```

### Understanding Results

**Answer Section**:
- LLM-generated answer grounded in retrieved evidence
- If data insufficient: "I don't have that data..."
- Always includes dates and units when available

**Evidence Section**:
- Each chunk shows:
  - **Score**: Similarity percentage (higher = more relevant)
  - **Metadata**: Source, date, section type
  - **Text**: Actual chunk content used for answer
- Chunks sorted by relevance (highest score first)

**Query Metadata**:
- `resolved_patient_id`: UUID found for person name
- `source_filter`: Applied source filter
- `time_range`: Applied time filters
- `results_count`: Number of evidence chunks found

## 🎯 Tips & Best Practices

### Ingestion Tips

1. **Always use valid UUIDs** for `patient_id`
2. **Use consistent date formats**: `YYYY-MM-DD` or ISO 8601
3. **Load examples first** to see correct format
4. **Check error messages** in response box for validation issues
5. **Refresh status bar** after ingestion to see updated point count

### Query Tips

1. **Be specific with dates**: Use date/time filters for time-based queries
2. **Use source filters**: Narrow down to relevant data source
3. **Check person name**: Ensure it matches database (case-insensitive)
4. **Start broad, then narrow**: Try without filters first, then add them
5. **Read evidence**: Check retrieved chunks to understand answer basis

### Performance Tips

1. **Limit results**: Use lower `top_k` for faster queries (default: 10)
2. **Disable hourly chunks**: Unless needed (reduces index size)
3. **Use source filters**: Speeds up vector search
4. **Batch ingestion**: Ingest multiple records at once

## 🔧 Troubleshooting

### "Cannot connect to API"

**Symptoms**: Red status bar, no health check
**Solution**:
```bash
# Check if API is running
curl http://localhost:8000/health

# If not, start it
python main.py
```

### "Person not found"

**Symptoms**: Query returns "Could not find patient..."
**Solution**:
- Verify person name spelling
- Try using patient UUID directly
- Check if profile was ingested
- Use exact name from database

### "Empty Results"

**Symptoms**: Query returns no evidence chunks
**Solution**:
- Check if data was ingested (collection info)
- Verify time range includes data
- Try removing source filter
- Check person name is correct

### JSON Parsing Errors

**Symptoms**: "Invalid JSON" error during ingestion
**Solution**:
- Use "Load Example" to get valid format
- Validate JSON with online tool (jsonlint.com)
- Check for missing commas, brackets, quotes
- Ensure all strings are double-quoted

### Slow Queries

**Symptoms**: Query takes >5 seconds
**Solution**:
- Reduce `top_k` value
- Use source filter
- Check OpenAI API status
- Verify Qdrant is running

## 🎨 UI Features

### Color Coding

- **Purple/Blue**: Primary actions and branding
- **Green**: Success messages, healthy status
- **Red**: Errors, unhealthy status
- **Gray**: Secondary actions, disabled states
- **White**: Content areas, cards

### Responsive Design

- **Desktop**: Two-column layout (ingestion + query)
- **Tablet/Mobile**: Single column, stacked layout
- **Adapts to screen size** automatically

### Interactive Elements

- **Tabs**: Switch between data sources
- **Buttons**: Hover effects, loading states
- **Input fields**: Focus highlights
- **Loading spinners**: Show during processing
- **Response boxes**: Color-coded by success/error

## 📱 Mobile Usage

The interface is fully responsive:

1. **Stack layout**: All sections stack vertically on mobile
2. **Touch-friendly**: Buttons and inputs sized for touch
3. **Scrollable**: Long content areas scroll smoothly
4. **Readable**: Text sizes optimized for mobile

## 🔐 Security Notes

### Production Deployment

When deploying to production:

1. **Enable authentication**: Add login/JWT middleware
2. **HTTPS only**: Redirect HTTP to HTTPS
3. **CORS configuration**: Restrict allowed origins
4. **Rate limiting**: Add API rate limits
5. **Input validation**: Backend validates all inputs

### Data Privacy

- **Never expose PII**: Don't show emails/phones in UI
- **Patient isolation**: Frontend enforces person selection
- **Audit logging**: Backend logs all queries (patient_id only)

## 🛠️ Customization

### Change API URL

Edit `frontend.html`, line ~429:
```javascript
const API_BASE = 'http://localhost:8000';
// Change to your API URL
```

### Modify Styling

Edit the `<style>` section in `frontend.html`:
- Colors: Search for `#667eea` (primary purple)
- Fonts: Change `font-family` in `body` selector
- Layout: Modify `.main-content` grid

### Add New Tabs

1. Add tab button in `.tabs` section
2. Add tab content div with `tab-content` class
3. Add switch function in JavaScript
4. Add example data function

## 📊 Advanced Usage

### Bulk Ingestion

1. Prepare large JSON array of records
2. Paste into appropriate tab
3. Ingest (processes all in batch)
4. Check response for errors

### Complex Queries

Use natural language for complex questions:
```
"Compare breakfast meals from last week and show nutritional trends"
"What days had the highest step count in August?"
"Show all meals with protein above 30g"
```

### Time Series Queries

Use date ranges for trends:
```
From: 2025-09-01 00:00
To: 2025-09-30 23:59
Question: "Analyze fitness trends for this month"
```

## 🎓 Learning Resources

1. **API Documentation**: http://localhost:8000/docs
2. **System README**: See README.md in project
3. **Architecture**: See ARCHITECTURE.md
4. **Examples**: Load example buttons in each tab

## 📞 Support

For issues:
1. Check browser console (F12) for JavaScript errors
2. Check API logs in terminal
3. Verify all services running: `docker-compose ps`
4. Review troubleshooting section above

---

**Frontend Version**: 1.0
**Last Updated**: 2025-09-30
**Compatible with API**: v1.0.0

**Enjoy your Patient Data RAG System! 🚀**




