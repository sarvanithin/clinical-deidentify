from transformers import pipeline
from typing import List, Dict
import torch

class TransformerDetector:
    """
    Transformer-based detector for contextual PHI (Names, Locations, Organizations).
    Uses a robust NER model from HuggingFace.
    """
    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        device = 0 if torch.cuda.is_available() else -1
        # mps support for mac if needed, but -1 is safe for cpu
        self.nlp = pipeline("token-classification", model=model_name, aggregation_strategy="simple", device=device)

    def detect(self, text: str) -> List[Dict]:
        """
        Detect PHI using the transformer model.
        Returns a list of dictionaries with start, end, label, and text.
        """
        results = self.nlp(text)
        entities = []
        for res in results:
            entities.append({
                "start": res["start"],
                "end": res["end"],
                "label": res["entity_group"],
                "text": res["word"],
                "score": float(res["score"]),
                "source": "transformer"
            })
        return entities
