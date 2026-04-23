# 📄 ATS Resume Checker

A free, lightweight, end-to-end ATS (Applicant Tracking System) resume analyzer.  
Upload your PDF/DOCX resume and get an instant ATS score with actionable improvement suggestions.

---

## 🚀 Features

- **ATS Score (0–100)** — Weighted scoring across 4 dimensions
- **Section Completeness** — Checks for all critical resume sections
- **Keyword Analysis** — Matches against 100+ tech & soft keywords
- **Job Description Matching** — Paste a JD for targeted keyword gap analysis
- **Language & Impact** — Detects weak phrases, missing metrics, and overused words
- **Formatting Check** — Flags ATS-unfriendly formatting patterns
- **Actionable Suggestions** — Prioritized, specific improvements

---

## 📁 Project Structure

```
ats-checker/
├── backend/
│   ├── app.py              # Flask API server
│   ├── resume_parser.py    # PDF & DOCX text extraction
│   ├── ats_analyzer.py     # Core scoring & analysis engine
│   ├── requirements.txt    # Python dependencies
│   └── Procfile            # For Render/Railway deployment
├── frontend/
│   └── index.html          # Complete single-file frontend
├── sample_resume.txt       # Sample resume for testing
├── render.yaml             # Render deployment config
└── README.md
```

---

## ⚡ Run Locally (5 Minutes)

### Step 1: Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start the backend

```bash
python app.py
# Server starts at http://localhost:5000
# Test: open http://localhost:5000/health in your browser
```

### Step 3: Open the frontend

Simply open `frontend/index.html` in your browser.  
No build step required — it's a single HTML file.

> **Note**: The frontend is pre-configured to call `http://localhost:5000`.  
> For production, change the `API_URL` constant at the top of `index.html`.

---

## 🧪 Testing

**Quick test without a resume file:**

```bash
cd backend
python -c "
from ats_analyzer import analyze_resume
text = open('../sample_resume.txt').read()
result = analyze_resume(text)
print(f'Score: {result[\"score\"]}/100 ({result[\"grade\"]})')
"
```

**Test the API with curl:**

```bash
# Health check
curl http://localhost:5000/health

# Upload a resume (PDF)
curl -X POST http://localhost:5000/analyze \
  -F "resume=@my_resume.pdf"

# With a job description
curl -X POST http://localhost:5000/analyze \
  -F "resume=@my_resume.pdf" \
  -F "job_description=Python Django AWS Senior Engineer"
```

---

## ☁️ Deployment

### Option A: Render (Recommended — Free Tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
5. Deploy. Copy your Render URL (e.g. `https://ats-checker-api.onrender.com`)
6. Update `API_URL` in `frontend/index.html` to your Render URL
7. Deploy `frontend/index.html` to [Vercel](https://vercel.com) or [Netlify](https://netlify.com) (just drag the file)

### Option B: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy backend
cd backend
railway login
railway init
railway up
```

### Option C: Local + Ngrok (Quick Public URL)

```bash
# Run backend
python app.py &

# Expose it publicly
npx ngrok http 5000

# Copy ngrok URL → update API_URL in index.html
```

### Frontend Deployment (Any Option)

The frontend is a **single static HTML file** — deploy it anywhere:

- **Netlify**: Drag & drop `frontend/` folder at netlify.com
- **Vercel**: `npx vercel frontend/`
- **GitHub Pages**: Push to a `gh-pages` branch
- **Cloudflare Pages**: Connect GitHub repo

---

## 📊 Scoring Algorithm

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Section Completeness | 30% | Presence of Contact, Summary, Experience, Education, Skills, etc. |
| Keyword Optimization | 30% | Matching against 100+ keywords + optional JD keywords |
| ATS Formatting | 20% | No tables, special chars, proper dates, email, phone |
| Language & Impact | 20% | Strong verbs, quantified achievements, no weak phrases |

---

## 🔧 Customization

**Add more keywords** — Edit `COMMON_KEYWORDS` in `ats_analyzer.py`  
**Add more weak phrases** — Edit `WEAK_PHRASES` in `ats_analyzer.py`  
**Change scoring weights** — Edit the final `analyze_resume()` function  
**Add sections to detect** — Edit `SECTION_PATTERNS` in `ats_analyzer.py`

---

## 🛡️ Privacy

- No resume data is stored or logged
- Files are processed in-memory and immediately deleted
- No database required

---

## 📦 Dependencies

**Backend** (all lightweight):
- `flask` — Web framework
- `flask-cors` — Cross-origin requests
- `pymupdf` — Fast PDF text extraction
- `python-docx` — DOCX text extraction
- `gunicorn` — Production WSGI server

**Frontend**: Zero dependencies — pure HTML/CSS/JavaScript

---

## 🤝 Contributing

Pull requests welcome! Ideas:
- Add more language/grammar checks
- Add resume comparison (before vs after)
- Add PDF report download
- Add more industry-specific keyword sets
