from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# Load model
model = pickle.load(open('model.pkl', 'rb'))
tfidf = pickle.load(open('tfidf.pkl', 'rb'))

red_flags = [
    "earn money fast","no experience required","registration fee",
    "work from home","urgent hiring","limited seats","pay to apply",
    "easy money","instant joining","pay verification charges",
    "confirm your position","selected for job","click here","congratulations"
]

# ------------------- URL TEXT EXTRACTION -------------------
def extract_text_from_url(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text()
    except:
        return ""

# ------------------- DETECTION -------------------
def detect_red_flags(text):
    text = text.lower()
    return [flag for flag in red_flags if flag in text]

def check_email(text):
    return re.findall(r'\S+@\S+', text)

def check_url(text):
    urls = re.findall(r'(https?://\S+)', text)
    issues = []
    for url in urls:
        if "bit.ly" in url or "tinyurl" in url:
            issues.append(f"Shortened URL: {url}")
        if not any(d in url for d in [".com",".org",".in",".net"]):
            issues.append(f"Unusual domain: {url}")
    return issues

# ------------------- COMPANY VALIDATION -------------------
def validate_company(text, emails):
    known = ["infosys","tcs","wipro","google","amazon","microsoft"]
    text_lower = text.lower()

    # 🔥 Email domain check (IMPORTANT FIX)
    if emails:
        domain = emails[0].split("@")[-1]
        if "gmail" in domain or "yahoo" in domain:
            return "Unverified Company ⚠️", "Free email domain used"

    for c in known:
        if c in text_lower:
            if any(e.endswith(f"@{c}.com") for e in emails):
                return f"{c.capitalize()} (Verified Company)", "Official domain email detected"
            else:
                return f"{c.capitalize()} mentioned but suspicious ⚠️", "Domain mismatch detected"

    return "Unknown Company ⚠️", "Company not found in trusted database"

# ------------------- EXPLANATION -------------------
def generate_explanation(flags, emails, urls):
    reasons = []

    for f in flags:
        if "no experience" in f:
            reasons.append("Unrealistic job requirement (no experience needed)")
        elif "registration" in f or "verification" in f:
            reasons.append("Payment request detected → strong scam signal")
        elif "work from home" in f:
            reasons.append("Common scam pattern: work-from-home offers")
        elif "congratulations" in f:
            reasons.append("Emotional trigger used to trap users")
        else:
            reasons.append(f"Suspicious phrase detected: {f}")

    for e in emails:
        if "gmail" in e or "yahoo" in e:
            reasons.append(f"Unofficial email used: {e}")

    for u in urls:
        reasons.append("Suspicious or shortened URL detected")

    return reasons

# ------------------- ML -------------------
def predict_job(text):
    vec = tfidf.transform([text]).toarray()
    res = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0][1]
    return res, prob

# ------------------- HOME -------------------
@app.route('/')
def home():
    return "✅ API Running Successfully"

# ------------------- MAIN -------------------
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    text = data.get("text", "")
    url = data.get("url", "")

    # 🔥 URL SUPPORT
    if not text and url:
        text = extract_text_from_url(url)

    result, prob = predict_job(text)

    flags = detect_red_flags(text)
    emails = check_email(text)
    urls = check_url(text)

    explanations = generate_explanation(flags, emails, urls)
    company_status, company_reason = validate_company(text, emails)

    # 🔥 IMPROVED EMAIL LOGIC
    suspicious_email = any(("gmail" in e or "yahoo" in e) for e in emails)

    # 🔥 BALANCED RISK (ML DOMINANT)
    risk_score = min(
        (prob * 0.6) +
        (len(flags) * 0.15) +
        (1 if suspicious_email else 0) * 0.15 +
        (len(urls) * 0.1),
        0.95
    )

    # 🔥 BETTER DECISION LOGIC
    if risk_score > 0.7:
        prediction = "Fake"
    elif risk_score > 0.4:
        prediction = "Suspicious"
    else:
        prediction = "Real"

    # Risk level
    if risk_score > 0.7:
        risk_level = "High Risk 🚨"
    elif risk_score > 0.4:
        risk_level = "Medium Risk ⚠️"
    else:
        risk_level = "Low Risk ✅"

    # 🔥 FIXED BREAKDOWN (NO OVERWEIGHT)
    breakdown = {
        "ml": prob * 100,
        "keyword": len(flags) * 10,
        "email": (1 if suspicious_email else 0) * 10,
        "url": (1 if len(urls) > 0 else 0) * 10
    }

    total = sum(breakdown.values()) or 1

    percent_breakdown = {
        "ml": round((breakdown["ml"]/total)*100, 2),
        "keyword": round((breakdown["keyword"]/total)*100, 2),
        "email": round((breakdown["email"]/total)*100, 2),
        "url": round((breakdown["url"]/total)*100, 2)
    }

    primary_reason = explanations[0] if explanations else "No strong risk"

    # 🔥 CONSISTENCY LOGIC (VERY IMPORTANT)
    confidence_note = ""
    if prob < 0.3 and risk_score > 0.8:
        confidence_note = "⚠ Rule-based system dominates decision"

    return jsonify({
        "prediction": prediction,
        "risk_score": round(risk_score * 100, 2),
        "risk_level": risk_level,

        "red_flags": flags,
        "suspicious_emails": emails,
        "url_flags": urls,

        "explanations": explanations,
        "primary_reason": primary_reason,
        "confidence_note": confidence_note,

        "risk_breakdown": percent_breakdown,

        "company_status": company_status,
        "company_reason": company_reason
    })

import os

@app.route('/')
def home():
    return "API Running Successfully"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)