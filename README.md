---
title: Clinical Deidentify
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---

# 🏥 Clinical-Deidentify: Secure PHI Removal

[![CI](https://github.com/sarvanithin/clinical-deidentify/actions/workflows/ci.yml/badge.svg)](https://github.com/sarvanithin/clinical-deidentify/actions)

Fast, regex + transformer hybrid PHI removal for clinical text and documents. Protect patient privacy with clinical-grade accuracy.

![UI Mockup](/Users/nithinsarva/.gemini/antigravity/brain/b50698cd-8087-453a-be22-ce45586e1767/ui_demo_mockup_1773587336810.png)

## 🚀 Features
- **Hybrid Pipeline**: Combines deterministic regex for structured PHI (dates, IDs, phones) with state-of-the-art transformers for contextual PHI (patient names, locations).
- **Expanded Document Support**: De-identify **PDFs**, **Word (.docx)**, and **TXT** files with a unified interface.
- **Download Feature**: Instantly download de-identified results as a `.txt` file for safe storage.
- **Premium Dashboard**: A sleek, dark-mode web UI for real-time de-identification and file uploads.
- **HIPAA Compliant**: Docker-native service ensuring all data stays on your infrastructure.
- **Active Learning**: Built-in feedback loop for clinical correction storage.

## 🚀 Quick Start (Docker)
1. **Build**:
   ```bash
   docker build -t clinical-deidentify .
   ```
2. **Run**:
   ```bash
   docker run -d -p 8001:8000 --name clinical-deid-service clinical-deidentify
   ```
   *Dashboard available at: [http://localhost:8001](http://localhost:8001)*

## Local Installation
1. **Clone & Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
### De-identify Single Note
```bash
curl -X POST "http://localhost:8000/deidentify" \
     -H "Content-Type: application/json" \
     -d '{"text": "Patient John Doe was admitted on 01/01/2023."}'
```
**Response**:
```json
{
  "original": "Patient John Doe was admitted on 01/01/2023.",
  "deidentified": "Patient [PATIENT] was admitted on [DATE].",
  "entities": [...]
}
```

## Evaluation
Run the mock benchmarking script:
```bash
python eval/evaluate.py
```

## Dataset Benchmarking
The pipeline is designed to be compatible with the **2014 i2b2 de-identification shared task** format. You can load i2b2 XML files and map them to the `EvalRequest` schema within `eval/evaluate.py`.
