import re
from typing import List, Dict

class RegexDetector:
    """
    Regex-based detector for HIPAA Safe Harbor PHI categories.
    """
    def __init__(self):
        # Patterns for common PHI with word boundaries and clinical variants
        self.patterns = {
            # Dates: MM/DD/YYYY, YYYY-MM-DD, Month DD, YYYY, clinical abbreviations like Jan '24 or Jan 2024
            "DATE": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:\d{1,2}(?:st|nd|rd|th)?(?:,?\s+[']?\d{2,4})?|[']?\d{2,4}))\b",
            # Phone numbers: various formats including country codes and extensions
            "PHONE": r"(?:\b|\()(?:\+?\d{1,2}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?:\s*(?:x|ext)\.?\s*\d{1,5})?\b",
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            # Zip codes: 5 digits or 5+4
            "ZIP": r"\b\d{5}(?:-\d{4})?\b",
            # Medical Record Numbers: clinical variants with prefixes
            "MRN": r"\b(?:MRN|EHR|HCN)\s*#?\s*[:\-]?\s*([A-Z0-9]{6,12})\b",
            "URL": r"https?://(?:[-\w.]|(?:%[\da-f_A-F]{2}))+",
            "IP_ADDR": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            # HIPAA: Ages >= 90 must be masked.
            "AGE": r"\b(?:age|Age)\s*[:\-]?\s*(?:[9][0-9]|1[0-9]{2})\b|\b(?:9[0-9]|1[0-9]{2})\s*(?:years?|y/o|yo|-year-old)\b",
            # Device identifiers/Serial numbers
            "DEVICE_ID": r"\b(?:SN|S/N|Serial)\s*[:\-]?\s*([A-Z0-9\-]{6,20})\b",
            # Biometric identifiers
            "BIO_ID": r"\b(?:Fingerprint|Retina|Voiceprint)\b"
        }
        self.compiled_patterns = {label: re.compile(pattern, re.IGNORECASE) for label, pattern in self.patterns.items()}

    def detect(self, text: str) -> List[Dict]:
        """
        Detect PHI using regex patterns.
        Returns a list of dictionaries with start, end, label, and text.
        """
        entities = []
        for label, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                entities.append({
                    "start": match.start(),
                    "end": match.end(),
                    "label": label,
                    "text": match.group(),
                    "source": "regex"
                })
        return entities
