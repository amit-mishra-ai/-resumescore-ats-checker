"""
ats_analyzer.py — Enhanced ATS Resume Analyzer
Comprehensive scoring across 4 dimensions + Work Experience deep analysis + Fresher detection.
Supports all IT roles:
  Software Engineering, Frontend, Backend, Data Analyst, Data Scientist/ML,
  DevOps/Cloud/SRE, Cybersecurity, QA/Testing, Mobile, Database, Networking,
  UI/UX, Product Management, Business Analyst, ERP/CRM, IT Support
"""

import re
from collections import Counter


# ──────────────────────────────────────────────────
#  SECTION PATTERNS
# ──────────────────────────────────────────────────

SECTION_PATTERNS = {
    "contact_info": [
        r'\b(phone|email|linkedin|github|portfolio|address|contact)\b',
        r'[\w.+-]+@[\w-]+\.[a-z]{2,}',
        r'\+?\d[\d\s\-\(\)]{7,}\d'
    ],
    "summary": [
        r'\b(summary|objective|profile|about me|professional summary|career objective|overview|introduction)\b'
    ],
    "experience": [
        r'\b(experience|work experience|employment|work history|professional experience|career history|internship|intern)\b'
    ],
    "education": [
        r'\b(education|academic|qualification|degree|university|college|school|bachelor|master|phd|b\.?tech|m\.?tech|b\.?sc|m\.?sc|mba|diploma|bca|mca)\b'
    ],
    "skills": [
        r'\b(skills|technical skills|core competencies|expertise|technologies|stack|tools|proficiencies|competencies|languages)\b'
    ],
    "projects": [
        r'\b(projects|personal projects|key projects|academic projects|portfolio|case studies|side projects)\b'
    ],
    "certifications": [
        r'\b(certif|certification|license|credential|certified|accreditation|aws certified|google certified|microsoft certified)\b'
    ],
    "achievements": [
        r'\b(achievement|award|honor|recognition|accomplishment|publication|patent|scholarship|hackathon|competition)\b'
    ]
}


# ──────────────────────────────────────────────────
#  WEAK PHRASES & STRONG VERBS
# ──────────────────────────────────────────────────

WEAK_PHRASES = [
    "responsible for", "worked on", "helped with", "assisted in",
    "duties included", "involved in", "participated in",
    "team player", "hardworking", "hard working", "go-getter",
    "detail oriented", "think outside the box", "synergy", "leverage",
    "dynamic", "proactive", "passionate about", "results-driven",
    "self-motivated", "strong communication skills", "fast learner",
    "go to person", "wore many hats", "various tasks", "handled",
    "tasked with", "tried to", "attempted to"
]

STRONG_VERBS = [
    "achieved", "architected", "automated", "built", "configured",
    "created", "debugged", "delivered", "deployed", "designed",
    "developed", "diagnosed", "engineered", "established", "exceeded",
    "executed", "founded", "generated", "grew", "implemented",
    "improved", "increased", "integrated", "launched", "led",
    "maintained", "managed", "mentored", "migrated", "monitored",
    "optimized", "orchestrated", "reduced", "refactored", "resolved",
    "saved", "scaled", "secured", "shipped", "solved",
    "streamlined", "tested", "transformed", "troubleshot", "upgraded",
    "spearheaded", "pioneered", "drove", "accelerated", "consolidated"
]


# ──────────────────────────────────────────────────
#  ROLE KEYWORDS (comprehensive, all IT roles)
# ──────────────────────────────────────────────────

ROLE_KEYWORDS = {
    "software_engineering": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go",
        "rust", "ruby", "php", "scala", "kotlin", "swift", "perl",
        "object oriented", "oop", "design patterns", "solid principles",
        "microservices", "rest", "restful", "graphql", "grpc", "api",
        "git", "github", "gitlab", "bitbucket", "code review",
        "unit testing", "tdd", "bdd", "debugging", "refactoring",
        "algorithms", "data structures", "system design", "architecture"
    ],
    "frontend": [
        "react", "angular", "vue", "next.js", "nuxt", "svelte",
        "html", "css", "sass", "scss", "tailwind", "bootstrap",
        "javascript", "typescript", "redux", "zustand", "webpack",
        "vite", "babel", "responsive design", "accessibility", "wcag",
        "figma", "storybook", "jest", "cypress", "playwright",
        "web performance", "seo", "pwa", "cross browser"
    ],
    "backend": [
        "node.js", "express", "django", "flask", "fastapi", "spring boot",
        "laravel", "rails", "asp.net", "nestjs", "gin", "fiber",
        "rest api", "graphql", "grpc", "microservices", "message queue",
        "rabbitmq", "kafka", "celery", "redis", "caching", "authentication",
        "oauth", "jwt", "websocket", "sql", "nosql", "orm"
    ],
    "data_analyst": [
        "sql", "mysql", "postgresql", "excel", "power bi", "tableau",
        "looker", "google analytics", "pandas", "numpy", "python",
        "r", "data analysis", "data visualization", "reporting",
        "dashboard", "kpi", "metrics", "etl", "data warehouse",
        "data cleaning", "pivot table", "statistics", "a/b testing",
        "hypothesis testing", "business intelligence", "data modelling",
        "snowflake", "bigquery", "redshift", "data storytelling", "forecasting"
    ],
    "data_science": [
        "machine learning", "deep learning", "neural network", "nlp",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "xgboost", "lightgbm", "pandas", "numpy", "matplotlib", "seaborn",
        "feature engineering", "model training", "model deployment",
        "mlops", "experiment tracking", "mlflow", "statistics", "probability",
        "regression", "classification", "clustering", "time series",
        "large language model", "llm", "generative ai", "langchain",
        "hugging face", "openai", "rag", "vector database", "embedding"
    ],
    "devops_cloud": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "puppet", "chef", "helm", "ci/cd",
        "jenkins", "github actions", "gitlab ci", "circleci",
        "linux", "bash", "shell scripting", "python", "monitoring",
        "prometheus", "grafana", "elk stack", "splunk", "datadog",
        "infrastructure as code", "iac", "sre", "reliability",
        "incident management", "load balancing", "auto scaling",
        "vpc", "networking", "cloudformation", "pulumi", "argocd",
        "service mesh", "istio", "nginx", "apache", "disaster recovery"
    ],
    "cybersecurity": [
        "penetration testing", "ethical hacking", "vulnerability assessment",
        "siem", "soc", "incident response", "threat hunting",
        "network security", "firewall", "ids", "ips", "waf",
        "owasp", "nmap", "metasploit", "burp suite", "kali linux",
        "encryption", "pki", "ssl", "tls", "vpn", "zero trust",
        "identity management", "iam", "privileged access", "pam",
        "compliance", "iso 27001", "nist", "gdpr", "hipaa", "soc2",
        "risk assessment", "security audit", "dlp", "endpoint security",
        "malware analysis", "reverse engineering", "forensics",
        "cloud security", "devsecops", "cissp", "ceh"
    ],
    "qa_testing": [
        "manual testing", "automation testing", "selenium", "cypress",
        "playwright", "appium", "testng", "junit", "pytest",
        "test cases", "test plan", "test strategy", "bug reporting",
        "jira", "defect tracking", "regression testing", "smoke testing",
        "integration testing", "api testing", "postman", "rest assured",
        "performance testing", "jmeter", "load testing", "stress testing",
        "mobile testing", "cross browser testing", "bdd", "cucumber",
        "gherkin", "page object model", "ci/cd", "quality assurance"
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "dart", "kotlin",
        "swift", "objective-c", "java", "xcode", "android studio",
        "firebase", "push notifications", "rest api", "mvvm", "mvp",
        "room database", "coredata", "app store", "play store",
        "jetpack compose", "swiftui"
    ],
    "database": [
        "sql", "mysql", "postgresql", "oracle", "sql server", "sqlite",
        "mongodb", "cassandra", "dynamodb", "redis", "elasticsearch",
        "database design", "data modelling", "normalization", "indexing",
        "query optimization", "stored procedures", "triggers", "views",
        "replication", "sharding", "partitioning", "backup", "recovery",
        "etl", "data migration", "database administration", "dba",
        "nosql", "acid", "transactions", "performance tuning"
    ],
    "networking": [
        "cisco", "juniper", "tcp/ip", "dns", "dhcp", "bgp", "ospf",
        "vlan", "vpn", "mpls", "sd-wan", "firewall", "routing",
        "switching", "network monitoring", "snmp", "wireshark",
        "load balancer", "f5", "network security", "ccna", "ccnp",
        "subnetting", "ipv4", "ipv6", "network troubleshooting",
        "infrastructure", "wan", "lan", "wireless", "wifi"
    ],
    "ui_ux": [
        "figma", "sketch", "adobe xd", "invision", "zeplin",
        "user research", "usability testing", "wireframing", "prototyping",
        "user journey", "information architecture", "design system",
        "ui design", "ux design", "interaction design", "visual design",
        "typography", "color theory", "responsive design", "accessibility",
        "wcag", "a/b testing", "heatmap", "user persona", "design thinking",
        "adobe photoshop", "illustrator", "after effects", "motion design"
    ],
    "product_management": [
        "product roadmap", "product strategy", "agile", "scrum",
        "kanban", "user stories", "backlog grooming", "sprint planning",
        "stakeholder management", "product requirements", "prd",
        "go-to-market", "product launch", "kpi", "okr", "metrics",
        "market research", "competitor analysis", "customer discovery",
        "ab testing", "feature prioritization", "mvp", "product vision",
        "jira", "confluence", "miro", "product analytics", "funnel"
    ],
    "business_analyst": [
        "requirements gathering", "business requirements", "brd", "frd",
        "gap analysis", "process mapping", "bpmn", "use cases",
        "stakeholder management", "uml", "wireframing", "sql",
        "excel", "power bi", "tableau", "data analysis",
        "agile", "scrum", "jira", "confluence", "visio",
        "user acceptance testing", "uat", "change management",
        "process improvement", "workflow", "business process"
    ],
    "erp_crm": [
        "sap", "sap s/4hana", "sap hana", "sap fiori", "sap abap",
        "salesforce", "salesforce crm", "apex", "visualforce",
        "lightning web component", "salesforce admin",
        "dynamics 365", "microsoft dynamics", "oracle erp",
        "workday", "servicenow", "zoho crm", "hubspot", "erp implementation"
    ],
    "it_support": [
        "windows server", "active directory", "group policy", "dns", "dhcp",
        "office 365", "microsoft 365", "azure ad", "helpdesk", "ticketing",
        "servicenow", "jira service desk", "remote support", "troubleshooting",
        "hardware", "software installation", "patch management",
        "backup", "recovery", "vmware", "hyper-v", "virtualization",
        "linux", "powershell", "bash", "itil", "sla", "incident management",
        "asset management", "endpoint management", "sccm", "intune"
    ],
    "universal": [
        "agile", "scrum", "kanban", "jira", "confluence", "git",
        "communication", "collaboration", "problem solving",
        "leadership", "teamwork", "analytical", "documentation",
        "project management", "time management", "critical thinking"
    ]
}

ROLE_SIGNALS = {
    "software_engineering": [
        "software engineer", "software developer", "backend", "full stack",
        "fullstack", "sde", "swe", "programmer", "java developer", "python developer"
    ],
    "frontend": ["frontend", "front-end", "front end", "react developer", "ui developer", "web developer"],
    "backend": ["backend", "back-end", "back end", "api developer", "node developer", "django", "spring boot"],
    "data_analyst": ["data analyst", "business analyst", "reporting analyst", "bi analyst", "analytics", "power bi", "tableau"],
    "data_science": ["data scientist", "machine learning", "ml engineer", "ai engineer", "deep learning", "nlp engineer", "mlops"],
    "devops_cloud": ["devops", "cloud engineer", "sre", "site reliability", "infrastructure", "platform engineer", "cloud architect", "aws", "azure", "kubernetes"],
    "cybersecurity": ["security engineer", "cybersecurity", "penetration tester", "soc analyst", "information security", "network security", "ethical hacker"],
    "qa_testing": ["qa engineer", "quality assurance", "test engineer", "sdet", "automation engineer", "manual tester"],
    "mobile": ["mobile developer", "android developer", "ios developer", "react native", "flutter developer"],
    "database": ["database administrator", "dba", "database developer", "sql developer", "data engineer"],
    "networking": ["network engineer", "network administrator", "network analyst", "cisco", "ccna"],
    "ui_ux": ["ui designer", "ux designer", "product designer", "ui/ux", "figma", "user experience"],
    "product_management": ["product manager", "product owner", "program manager", "product lead"],
    "business_analyst": ["business analyst", "ba", "systems analyst", "process analyst", "requirements analyst"],
    "erp_crm": ["sap", "salesforce", "dynamics", "erp", "crm", "workday", "servicenow"],
    "it_support": ["it support", "helpdesk", "help desk", "system administrator", "sysadmin", "it technician"]
}

ATS_RED_FLAGS = [
    (r'\b(text box)\b', "Text boxes are not readable by ATS parsers — use plain text sections"),
    (r'[^\x00-\x7F]{5,}', "Special/unicode characters detected — may cause ATS parsing issues"),
    (r'(.)\1{5,}', "Decorative characters (e.g. ====, ----) detected — remove them"),
]

QUANTIFICATION_PATTERNS = [
    r'\d+\s*(%|percent)',
    r'₹\s*\d+|\$\s*\d+',
    r'\d+\+?\s*(users|clients|people|team|employees|projects|tickets|bugs|features|customers)',
    r'(increased|reduced|improved|grew|saved|generated|decreased|boosted|cut|lowered)\D{1,25}\d+',
    r'\d+x\s*(faster|improvement|growth|increase)',
    r'\d+\s*(lakh|crore|million|billion|thousand)',
    r'\d+\s*(lines of code|repos|releases|sprints|deployments)',
]


# ──────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────

def normalize(text): return text.lower().strip()

def find_section(text, patterns):
    text_lower = normalize(text)
    for p in patterns:
        if re.search(p, text_lower, re.IGNORECASE): return True
    return False

def count_words(text): return len(re.findall(r'\b\w+\b', text))

def detect_repeated_words(text, threshold=5):
    stop_words = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with","by","from",
        "is","was","are","were","be","been","have","has","had","do","does","did","will",
        "would","could","should","may","might","my","your","their","i","we","you","he",
        "she","they","it","this","that","as","not","also","which","who","more","than",
        "up","out","can","using","used","work","worked","team","role","good","best","time",
        "based","well","make","made","into","over","across","new","its"
    }
    words = re.findall(r'\b[a-z]{4,}\b', normalize(text))
    word_counts = Counter(words)
    return {w: c for w, c in word_counts.items() if c >= threshold and w not in stop_words}

def check_quantification(text):
    matches = []
    for p in QUANTIFICATION_PATTERNS:
        found = re.findall(p, text, re.IGNORECASE)
        matches.extend(found)
    return len(matches)

def extract_keywords_from_jd(job_description):
    if not job_description: return []
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9\+\#\.]{2,}\b', job_description.lower())
    stop_words = {"with","that","this","will","from","have","been","they","were","your",
                  "their","also","must","work","able","good","strong","great","years","year","experience"}
    seen, keywords = set(), []
    for w in words:
        if w not in stop_words and w not in seen:
            seen.add(w); keywords.append(w)
    return keywords[:50]

def detect_roles(text):
    text_lower = text.lower()
    detected = ["universal"]
    for role, signals in ROLE_SIGNALS.items():
        for signal in signals:
            if signal in text_lower:
                if role not in detected: detected.append(role)
                break
    if len(detected) == 1:
        detected += ["software_engineering", "data_analyst", "devops_cloud"]
    return detected

def detect_fresher(text):
    """Detect if the resume belongs to a fresher/entry-level candidate."""
    text_lower = text.lower()
    fresher_signals = [
        r'\bfresher\b', r'\bfreshers\b', r'\bentry.?level\b', r'\bno experience\b',
        r'\bjust graduated\b', r'\brecent graduate\b', r'\bfresh graduate\b',
        r'\b0.?1 year\b', r'\bzero experience\b'
    ]
    for s in fresher_signals:
        if re.search(s, text_lower): return True

    # If no work experience section present but education is present
    has_experience = bool(re.search(r'\b(experience|work history|employment|worked at|worked for)\b', text_lower))
    has_education = bool(re.search(r'\b(education|university|college|degree|graduation)\b', text_lower))
    if has_education and not has_experience:
        return True
    return False


# ──────────────────────────────────────────────────
#  WORK EXPERIENCE DEEP ANALYSIS
# ──────────────────────────────────────────────────

def analyze_experience_section(text):
    """
    Deep analysis of the work experience section.
    Extracts job blocks, checks bullet quality, metrics, verbs, tenure.
    Only meaningful for experienced candidates.
    """
    is_fresher = detect_fresher(text)
    if is_fresher:
        return {
            "has_experience": False,
            "is_fresher": True,
            "total_years": 0,
            "jobs": [],
            "career_progression": "fresher",
            "average_tenure": "N/A",
            "gaps_detected": False,
            "note": "No work experience detected. Profile identified as fresher/entry-level."
        }

    text_lower = text.lower()
    jobs = []

    # Simple job block extraction by date ranges
    # Look for patterns like: Role — Company (Year – Year)
    date_pattern = re.compile(
        r'(?P<range>(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|(?:19|20)\d{2})'
        r'(?:\s*[-–—]\s*'
        r'(?:present|current|now|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}|(?:19|20)\d{2}))?',
        re.IGNORECASE
    )
    dates_found = date_pattern.findall(text)

    # Heuristic: check bullet count, metrics, action verbs
    lines = text.split('\n')
    bullet_lines = [l for l in lines if re.match(r'^\s*[•\-\*▶►]\s', l)]
    has_metrics = bool(check_quantification(text))
    has_action_verbs = len([v for v in STRONG_VERBS if re.search(r'\b' + re.escape(v) + r'\b', text_lower)]) >= 3

    # Build a summary job entry if we can't parse individual jobs
    if not jobs:
        year_refs = re.findall(r'\b(19|20)\d{2}\b', text)
        total_years = None
        if len(year_refs) >= 2:
            try:
                years = [int(y) for y in year_refs]
                span = max(years) - min(years)
                total_years = round(span, 1) if span > 0 else None
            except: pass

        quality = 50
        if has_metrics: quality += 20
        if has_action_verbs: quality += 15
        if len(bullet_lines) >= 5: quality += 15

        jobs = [{
            "title": "Detected Role",
            "company": "Detected from resume",
            "duration": f"{min(year_refs) if year_refs else 'N/A'} – Present",
            "years": total_years,
            "bullet_count": len(bullet_lines),
            "has_metrics": has_metrics,
            "has_action_verbs": has_action_verbs,
            "quality_score": min(100, quality),
            "strengths": [
                *( ["Quantified achievements present"] if has_metrics else []),
                *( ["Strong action verbs used"] if has_action_verbs else []),
                *( ["Good detail in bullet points"] if len(bullet_lines) >= 5 else [])
            ],
            "weaknesses": [
                *( ["No quantified metrics — add numbers and percentages"] if not has_metrics else []),
                *( ["Weak action verbs — start bullets with power verbs"] if not has_action_verbs else []),
                *( ["Too few bullet points — aim for 4-6 per role"] if len(bullet_lines) < 3 else [])
            ]
        }]

    return {
        "has_experience": True,
        "is_fresher": False,
        "total_years": jobs[0].get("years"),
        "jobs": jobs,
        "career_progression": "unknown",
        "average_tenure": f"~{jobs[0].get('years', '?')} years" if jobs[0].get("years") else "N/A",
        "gaps_detected": False
    }


# ──────────────────────────────────────────────────
#  SCORING FUNCTIONS
# ──────────────────────────────────────────────────

def score_sections(text, is_fresher=False):
    weights = {
        "contact_info":   {"weight": 15, "label": "Contact Information",  "required": True},
        "summary":        {"weight": 10, "label": "Professional Summary",  "required": False},
        "experience":     {"weight": 25 if not is_fresher else 0, "label": "Work Experience", "required": not is_fresher},
        "education":      {"weight": 20, "label": "Education",             "required": True},
        "skills":         {"weight": 15, "label": "Skills",                "required": True},
        "projects":       {"weight": 8,  "label": "Projects",              "required": False},
        "certifications": {"weight": 5,  "label": "Certifications",        "required": False},
        "achievements":   {"weight": 2,  "label": "Achievements/Awards",   "required": False},
    }
    # Redistribute experience weight for freshers
    if is_fresher:
        weights["projects"]["weight"] = 20
        weights["projects"]["required"] = True

    sections_result = {}
    total_weight = earned_weight = 0
    for key, config in weights.items():
        present = find_section(text, SECTION_PATTERNS.get(key, []))
        sections_result[key] = {
            "label": config["label"], "present": present,
            "required": config["required"], "weight": config["weight"]
        }
        total_weight += config["weight"]
        if present: earned_weight += config["weight"]

    score = int((earned_weight / max(total_weight, 1)) * 100)
    return score, sections_result


def score_keywords(text, job_description=""):
    text_lower = normalize(text)
    detected_roles = detect_roles(text)
    relevant_keywords = []
    for role in detected_roles:
        for kw in ROLE_KEYWORDS.get(role, []):
            if kw not in relevant_keywords: relevant_keywords.append(kw)

    found_keywords, missing_keywords = [], []
    for kw in relevant_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            found_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    target = max(1, int(len(relevant_keywords) * 0.40))
    keyword_score = min(100, int((len(found_keywords) / target) * 100))

    jd_keywords = extract_keywords_from_jd(job_description)
    jd_found, jd_missing = [], []
    for kw in jd_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            jd_found.append(kw)
        else:
            jd_missing.append(kw)

    if jd_keywords:
        jd_score = int((len(jd_found) / max(len(jd_keywords), 1)) * 100)
        keyword_score = int(keyword_score * 0.40 + jd_score * 0.60)

    return keyword_score, {
        "found": found_keywords[:25],
        "missing_suggestions": missing_keywords[:15],
        "jd_found": jd_found,
        "jd_missing": jd_missing[:10],
        "detected_roles": detected_roles
    }


def score_formatting(text):
    issues = []
    score = 100
    for pattern, message in ATS_RED_FLAGS:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(message); score -= 15

    date_pattern = r'\b(19|20)\d{2}\b|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b'
    if not re.search(date_pattern, text, re.IGNORECASE):
        issues.append("No dates found — add dates to your Education and Experience sections")
        score -= 10

    word_count = count_words(text)
    if word_count < 200:
        issues.append(f"Resume is too short ({word_count} words) — aim for 400–800 words")
        score -= 20
    elif word_count > 1200:
        issues.append(f"Resume may be too long ({word_count} words) — consider trimming to 1–2 pages")
        score -= 5

    if not re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', text):
        issues.append("No email address detected — add your email to the contact section")
        score -= 10
    if not re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text):
        issues.append("No phone number detected — add your phone number")
        score -= 5

    return max(0, score), issues


def score_language(text):
    text_lower = normalize(text)
    issues = []
    score = 100

    found_weak = [p for p in WEAK_PHRASES if re.search(r'\b' + re.escape(p) + r'\b', text_lower)]
    if found_weak:
        score -= min(30, len(found_weak) * 5)
        issues.append({"type": "weak_phrases", "message": f"Found {len(found_weak)} weak/overused phrase(s)", "items": found_weak})

    found_strong = [v for v in STRONG_VERBS if re.search(r'\b' + re.escape(v) + r'\b', text_lower)]
    if len(found_strong) < 3:
        score -= 15
        issues.append({"type": "no_action_verbs", "message": "Too few strong action verbs — start bullets with: Built, Led, Optimized, Delivered", "items": STRONG_VERBS[:10]})

    quant_count = check_quantification(text)
    if quant_count == 0:
        score -= 20
        issues.append({"type": "no_metrics", "message": "No quantified achievements found — add numbers (e.g. '↑35% efficiency', '$2M pipeline', '10-person team')", "items": []})
    elif quant_count < 3:
        score -= 10
        issues.append({"type": "few_metrics", "message": f"Only {quant_count} quantified achievement(s) — aim for 4+ metrics across your experience", "items": []})

    repeated = detect_repeated_words(text)
    if repeated:
        top_repeated = sorted(repeated.items(), key=lambda x: x[1], reverse=True)[:5]
        score -= min(15, len(repeated) * 3)
        issues.append({"type": "repeated_words", "message": f"Overused words: {', '.join([w for w, _ in top_repeated])}", "items": [f"'{w}' ({c}x)" for w, c in top_repeated]})

    return max(0, score), issues, {
        "strong_verbs_found": found_strong,
        "quantification_count": quant_count,
        "word_count": count_words(text)
    }


# ──────────────────────────────────────────────────
#  SUGGESTION ENGINE
# ──────────────────────────────────────────────────

def generate_suggestions(sections, keyword_data, formatting_issues, language_issues, lang_stats, is_fresher=False):
    suggestions = []

    for key, data in sections.items():
        if not data["present"] and data["required"]:
            suggestions.append({"priority": "high", "category": "Section Missing",
                "suggestion": f"Add a '{data['label']}' section — ATS systems expect this"})
        elif not data["present"] and not data["required"]:
            suggestions.append({"priority": "medium", "category": "Section Missing",
                "suggestion": f"Consider adding a '{data['label']}' section to strengthen your profile"})

    if keyword_data.get("jd_missing"):
        suggestions.append({"priority": "high", "category": "Job Description Match",
            "suggestion": f"Add these keywords from the job description: {', '.join(keyword_data['jd_missing'][:7])}"})

    if keyword_data.get("missing_suggestions"):
        suggestions.append({"priority": "medium", "category": "Role Keywords",
            "suggestion": f"Add relevant skills for your role: {', '.join(keyword_data['missing_suggestions'][:7])}"})

    for issue in formatting_issues:
        suggestions.append({"priority": "high", "category": "Formatting", "suggestion": issue})

    for issue in language_issues:
        if issue["type"] == "weak_phrases":
            for phrase in issue["items"][:3]:
                suggestions.append({"priority": "medium", "category": "Language",
                    "suggestion": f"Replace '{phrase}' with a strong action verb like 'Delivered', 'Optimized', or 'Built'"})
        elif issue["type"] in ("no_action_verbs", "no_metrics", "few_metrics"):
            suggestions.append({"priority": "high", "category": "Impact", "suggestion": issue["message"]})
        elif issue["type"] == "repeated_words":
            suggestions.append({"priority": "low", "category": "Language Variety",
                "suggestion": f"Vary your vocabulary — {issue['message']}"})

    if is_fresher:
        suggestions.append({"priority": "medium", "category": "Fresher Tip",
            "suggestion": "As a fresher, emphasize academic projects, internships, online courses, and certifications to compensate for work experience."})

    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order[x["priority"]])
    return suggestions[:20]


# ──────────────────────────────────────────────────
#  MAIN ANALYSIS FUNCTION
# ──────────────────────────────────────────────────

def analyze_resume(resume_text, job_description=""):
    """
    Full ATS analysis with work experience deep-dive and fresher detection.
    Weights: Sections 30% | Keywords 30% | Formatting 20% | Language 20%
    """
    is_fresher = detect_fresher(resume_text)

    section_score, sections         = score_sections(resume_text, is_fresher)
    keyword_score, keyword_data     = score_keywords(resume_text, job_description)
    format_score, formatting_issues = score_formatting(resume_text)
    language_score, language_issues, lang_stats = score_language(resume_text)
    experience_analysis             = analyze_experience_section(resume_text)

    final_score = int(
        section_score  * 0.30 +
        keyword_score  * 0.30 +
        format_score   * 0.20 +
        language_score * 0.20
    )

    if final_score >= 80:   grade, grade_color = "Excellent", "green"
    elif final_score >= 60: grade, grade_color = "Good", "blue"
    elif final_score >= 40: grade, grade_color = "Needs Work", "orange"
    else:                   grade, grade_color = "Poor", "red"

    suggestions = generate_suggestions(
        sections, keyword_data, formatting_issues, language_issues, lang_stats, is_fresher
    )

    return {
        "score": final_score,
        "grade": grade,
        "grade_color": grade_color,
        "is_fresher": is_fresher,
        "detected_roles": keyword_data.get("detected_roles", []),
        "breakdown": {
            "sections":   {"score": section_score,  "weight": "30%", "label": "Section Completeness"},
            "keywords":   {"score": keyword_score,  "weight": "30%", "label": "Keyword Optimization"},
            "formatting": {"score": format_score,   "weight": "20%", "label": "ATS Formatting"},
            "language":   {"score": language_score, "weight": "20%", "label": "Language & Impact"},
        },
        "sections": sections,
        "keywords": keyword_data,
        "experience_analysis": experience_analysis,
        "formatting_issues": formatting_issues,
        "language_issues": language_issues,
        "language_stats": lang_stats,
        "suggestions": suggestions,
        "word_count": lang_stats["word_count"],
        "has_job_description": bool(job_description)
    }
