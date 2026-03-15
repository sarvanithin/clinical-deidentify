import pytest
import os

# Redirect HF Cache to a writable directory
os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".hf_cache")

from app.pipeline.regex_rules import RegexDetector
from app.pipeline.hybrid import DeidPipeline

def test_regex_dates():
    detector = RegexDetector()
    text = "Admitted on 01/15/2023 and Jan '24"
    results = detector.detect(text)
    labels = [r["label"] for r in results]
    assert "DATE" in labels
    assert len(results) >= 2

def test_regex_age():
    detector = RegexDetector()
    text = "The patient is 92 years old and another is age: 95."
    results = detector.detect(text)
    assert len(results) == 2
    assert all(r["label"] == "AGE" for r in results)

def test_regex_mrn():
    detector = RegexDetector()
    text = "MRN: A1B2C3D4E5. EHR# 99887766."
    results = detector.detect(text)
    assert len(results) == 2
    assert all(r["label"] == "MRN" for r in results)

def test_hybrid_merging_overlaps():
    # Mocking transformer output for unit test
    class MockTransformer:
        def detect(self, text):
            # transformer catches "John Doe"
            return [{"start": 0, "end": 8, "label": "PERSON", "text": "John Doe", "source": "transformer", "score": 0.9}]
    
    pipeline = DeidPipeline()
    pipeline.transformer_detector = MockTransformer()
    
    # Text where regex and transformer might overlap
    text = "John Doe born 01/01/1980" 
    # Regex will catch 01/01/1980
    result = pipeline.deidentify(text)
    
    entities = result["entities"]
    # Should have both PERSON and DATE
    labels = [e["label"] for e in entities]
    assert "PERSON" in labels
    assert "DATE" in labels

def test_nested_merging():
    pipeline = DeidPipeline()
    # Mock: outer transformer span "Hospital Room 101", inner regex Zip Code "90210"
    # Wait, 90210 is a zip.
    class MockTransformer:
        def detect(self, text):
            return [{"start": 0, "end": 20, "label": "LOCATION", "text": "Beverly Hills 90210", "source": "transformer", "score": 0.8}]
    
    pipeline.transformer_detector = MockTransformer()
    text = "Beverly Hills 90210"
    # Regex ZIP will catch 90210
    result = pipeline.deidentify(text)
    
    entities = result["entities"]
    # Since zip is inside location, and current logic keeps outer if transformers...
    # Actually if zip is nested in transformer, we currently continue (keep outer).
    # Check if that's what we want. In de-id, masking the whole "Beverly Hills 90210" is fine.
    assert len(entities) == 1
    assert entities[0]["label"] == "LOCATION"

if __name__ == "__main__":
    pytest.main([__file__])
