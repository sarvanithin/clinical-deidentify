import random
from typing import List, Dict

def generate_mock_note() -> Dict:
    """
    Generates a mock clinical note with realistic PHI for testing.
    """
    names = ["John Doe", "Alice Smith", "Robert Johnson", "Maria Garcia"]
    dates = ["01/01/2023", "2022-12-15", "March 4th, 2024"]
    phones = ["(555) 123-4567", "555-987-6543", "123.456.7890"]
    ids = ["12345678", "MRN987654", "SSN: 000-00-0000"]
    
    name = random.choice(names)
    date = random.choice(dates)
    phone = random.choice(phones)
    mrn = random.choice(ids)
    
    note = f"""
    Discharge Summary
    Patient Name: {name}
    Date of Birth: {date}
    Contact: {phone}
    Medical Record Number: {mrn}
    
    The patient was admitted on {date} for acute chest pain. 
    Follow up with Dr. {random.choice(names)} at the main clinic.
    """
    
    # Simple "Gold Standard" extraction for mock eval
    phi = [
        {"text": name, "label": "PATIENT"},
        {"text": date, "label": "DATE"},
        {"text": phone, "label": "PHONE"},
        {"text": mrn, "label": "MRN"}
    ]
    
    return {"text": note, "phi": phi}

if __name__ == "__main__":
    sample = generate_mock_note()
    print("Mock Note:")
    print(sample["text"])
    print("\nGold PHI:")
    for p in sample["phi"]:
        print(f"- {p['label']}: {p['text']}")
