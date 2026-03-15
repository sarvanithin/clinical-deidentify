from typing import List, Dict
from dataclasses import dataclass

@dataclass
class EvalMetrics:
    precision: float
    recall: float
    f1: float

def calculate_token_f1(gold_entities: List[Dict], pred_entities: List[Dict]) -> EvalMetrics:
    """
    Simplified token-level F1 calculation.
    Counts exact span matches for simplicity in this version.
    """
    if not gold_entities and not pred_entities:
        return EvalMetrics(1.0, 1.0, 1.0)
    
    if not gold_entities:
        return EvalMetrics(0.0, 1.0, 0.0)
    
    if not pred_entities:
        return EvalMetrics(1.0, 0.0, 0.0)

    # Convert to sets of (start, end, label) for exact match
    gold_set = set((e["start"], e["end"], e["label"].upper()) for e in gold_entities)
    pred_set = set((e["start"], e["end"], e["label"].upper()) for e in pred_entities)
    
    tp = len(gold_set.intersection(pred_set))
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return EvalMetrics(precision, recall, f1)

def run_benchmark(pipeline, data: List[Dict]):
    """
    Runs the pipeline over a dataset and reports metrics.
    """
    all_metrics = []
    for item in data:
        prediction = pipeline.deidentify(item["text"])
        # In a real I2B2 eval, we'd need to map labels carefully
        # Here we just use the simplified span match
        # Note: pipeline entities already have start, end, label
        metrics = calculate_token_f1(item["phi"], prediction["entities"])
        all_metrics.append(metrics)
    
    avg_p = sum(m.precision for m in all_metrics) / len(all_metrics)
    avg_r = sum(m.recall for m in all_metrics) / len(all_metrics)
    avg_f1 = sum(m.f1 for m in all_metrics) / len(all_metrics)
    
    print(f"Benchmark Results (N={len(data)}):")
    print(f"Precision: {avg_p:.4f}")
    print(f"Recall:    {avg_r:.4f}")
    print(f"F1 Score:  {avg_f1:.4f}")

if __name__ == "__main__":
    # Example usage (skipping actual pipeline instantiation due to heavy model load)
    print("Evaluation script ready.")
