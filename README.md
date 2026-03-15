# Clinical-Deidentify

Fast, regex + transformer hybrid PHI removal for clinical text.

## Features
- **Hybrid Pipeline**: Combines deterministic regex for structured PHI (dates, IDs, phones) with state-of-the-art transformers for contextual PHI (patient names, locations).
- **FastAPI-served**: Lightweight and easy to integrate into clinical workflows.
- **Docker-ready**: Fully local deployment, ensuring HIPAA compliance by keeping data on-premises.
- **Active Learning**: Built-in `/feedback` endpoint for collecting manual corrections.

## Quick Start (Docker)
1. **Build**:
   ```bash
   docker build -t clinical-deidentify .
   ```
2. **Run**:
   ```bash
   docker run -p 8000:8000 clinical-deidentify
   ```

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
