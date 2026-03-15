from typing import List, Dict, Optional
from .regex_rules import RegexDetector
from .transformer_ner import TransformerDetector

class DeidPipeline:
    """
    Hybrid pipeline combining Regex and Transformer detectors.
    """
    def __init__(self, transformer_model: Optional[str] = None):
        self.regex_detector = RegexDetector()
        if transformer_model:
            self.transformer_detector = TransformerDetector(model_name=transformer_model)
        else:
            self.transformer_detector = TransformerDetector()

    def deidentify(self, text: str, mode: str = "mask") -> Dict:
        """
        De-identify text by merging results from both detectors.
        Modes:
            "mask": Replace PHI with [LABEL]
            "synth": (TBD) Replace with synthetic data
        """
        regex_entities = self.regex_detector.detect(text)
        # Add default confidence for regex
        for ent in regex_entities:
            ent["confidence"] = 1.0
            
        transformer_entities = self.transformer_detector.detect(text)
        # Ensure confidence key exists for transformers (from 'score')
        for ent in transformer_entities:
            ent["confidence"] = ent.get("score", 0.0)
        
        # Merge entities, resolving overlaps and nesting
        merged_entities = self._merge_entities(regex_entities, transformer_entities)
        
        # Sort by start position descending to replace without messing up indices
        sorted_entities = sorted(merged_entities, key=lambda x: x["start"], reverse=True)
        
        deidentified_text = text
        for ent in sorted_entities:
            label = ent["label"]
            start = ent["start"]
            end = ent["end"]
            
            if mode == "mask":
                replacement = f"[{label}]"
                deidentified_text = deidentified_text[:start] + replacement + deidentified_text[end:]
        
        return {
            "original": text,
            "deidentified": deidentified_text,
            "entities": merged_entities
        }

    def _merge_entities(self, e1: List[Dict], e2: List[Dict]) -> List[Dict]:
        """
        Merge two lists of entities and handle overlaps/nesting.
        Algorithm:
        1. Combine and sort by start (asc), then by end (desc) so longer spans come first.
        2. Iterate and keep spans that are not contained within or overlap significantly
           with already accepted spans, unless the new span has significantly higher priority.
        """
        combined = e1 + e2
        if not combined:
            return []
            
        # Sort by start asc, then by length desc (longer first for same start)
        combined.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))
        
        merged = []
        for next_ent in combined:
            if not merged:
                merged.append(next_ent)
                continue
                
            last = merged[-1]
            
            # If next_ent is completely inside last (nested)
            if next_ent["start"] >= last["start"] and next_ent["end"] <= last["end"]:
                # If nested is regex and outer is transformer, keep the regex (more specific)
                # But actually, often the outer span is the more contextually correct one 
                # (e.g., "John Doe" vs regex "Doe" if Doe was a date?). 
                # For HIPAA, we usually want the union or the most specific.
                # Here we prefer the outer span if it's already there, unless outer is low confidence.
                continue
            
            # If they overlap
            elif next_ent["start"] < last["end"]:
                # Priority: Regex (source='regex') > Transformer
                if last["source"] == "regex" and next_ent["source"] == "transformer":
                    continue # Keep last
                elif last["source"] == "transformer" and next_ent["source"] == "regex":
                    # Replace last with next_ent if next_ent starts roughly close
                    # For simplicity, we'll just extend last if it's longer or merge
                    # But if they overlap, and next is regex, it's safer to take the regex.
                    # Or take the union.
                    last["end"] = max(last["end"], next_ent["end"])
                    last["label"] = next_ent["label"] # Prefer regex label
                    last["source"] = "merged"
                else:
                    # Both same source, take union
                    last["end"] = max(last["end"], next_ent["end"])
            else:
                merged.append(next_ent)
                
        return merged
