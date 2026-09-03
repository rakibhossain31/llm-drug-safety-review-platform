from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean

from sklearn.metrics import accuracy_score, cohen_kappa_score, precision_recall_fscore_support

from safetyreview_ai.benchmark.schemas import ArchitecturePrediction, LiteratureBenchmarkRecord
from safetyreview_ai.benchmark.statistical_tests import bootstrap_interval

LABELS = ["relevant", "possibly relevant", "not relevant"]
SIGNAL_MAP = {
    "product_exposure": "product_exposure",
    "adverse_event": "adverse_event_present",
    "patient_population": "patient_population_present",
    "seriousness_signal": "seriousness_signal",
    "individual_case": "individual_case_present",
}


def _round(value: float | None) -> float | None:
    return None if value is None else round(float(value), 4)


def calculate_metrics(
    records: list[LiteratureBenchmarkRecord],
    predictions: list[ArchitecturePrediction],
) -> tuple[dict, dict, dict]:
    by_id = {prediction.document_id: prediction for prediction in predictions}
    aligned = [(record, by_id[record.document_id]) for record in records if record.document_id in by_id]
    gold = [record.adjudicated_label for record, _ in aligned]
    pred = [prediction.classification for _, prediction in aligned]

    precision, recall, f1, support = precision_recall_fscore_support(
        gold, pred, labels=LABELS, zero_division=0
    )
    class_metrics = {
        label: {
            "precision": _round(precision[i]),
            "recall": _round(recall[i]),
            "f1": _round(f1[i]),
            "support": int(support[i]),
        }
        for i, label in enumerate(LABELS)
    }
    macro_f1 = float(mean(f1))

    gold_include = [record.gold_labels.requires_full_text_review for record, _ in aligned]
    pred_include = [prediction.requires_full_text_review for _, prediction in aligned]
    tp = sum(g and p for g, p in zip(gold_include, pred_include))
    tn = sum((not g) and (not p) for g, p in zip(gold_include, pred_include))
    fp = sum((not g) and p for g, p in zip(gold_include, pred_include))
    fn = sum(g and (not p) for g, p in zip(gold_include, pred_include))
    sensitivity = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0

    signal_metrics = {}
    for predicted_key, gold_key in SIGNAL_MAP.items():
        signal_gold = [bool(getattr(record.gold_labels, gold_key)) for record, _ in aligned]
        signal_pred = [bool(prediction.signals.get(predicted_key, False)) for _, prediction in aligned]
        p, r, signal_f1, _ = precision_recall_fscore_support(
            signal_gold, signal_pred, average="binary", zero_division=0
        )
        signal_metrics[predicted_key] = {"precision": _round(p), "recall": _round(r), "f1": _round(signal_f1)}

    evidence_expected = []
    evidence_supported = []
    for record, prediction in aligned:
        gold_labels = {span.label for span in record.evidence_spans}
        predicted_labels = {label for label, spans in prediction.evidence.items() if spans}
        evidence_expected.append(len(gold_labels))
        evidence_supported.append(len(gold_labels & predicted_labels))
    evidence_recall = sum(evidence_supported) / sum(evidence_expected) if sum(evidence_expected) else 1.0

    metrics = {
        "records_evaluated": len(aligned),
        "accuracy": _round(accuracy_score(gold, pred) if gold else 0.0),
        "macro_f1": _round(macro_f1),
        "class_metrics": class_metrics,
        "screening_sensitivity": _round(sensitivity),
        "screening_specificity": _round(specificity),
        "false_negative_rate": _round(fn / (tp + fn) if tp + fn else 0.0),
        "false_positives": fp,
        "false_negatives": fn,
        "signal_metrics": signal_metrics,
        "evidence_label_recall": _round(evidence_recall),
        "schema_validity_rate": 1.0,
        "average_confidence": _round(mean(prediction.confidence for _, prediction in aligned) if aligned else 0.0),
        "average_latency_ms": _round(mean(prediction.latency_ms for _, prediction in aligned) if aligned else 0.0),
        "simulated_reviewer_kappa": _round(cohen_kappa_score(
            [record.simulated_reviewer_1_label for record, _ in aligned],
            [record.simulated_reviewer_2_label for record, _ in aligned],
            labels=LABELS,
        ) if aligned else 0.0),
    }

    pairs = [(record.adjudicated_label, prediction.classification) for record, prediction in aligned]
    _, macro_low, macro_high = bootstrap_interval(
        pairs,
        lambda items: mean(precision_recall_fscore_support(
            [x[0] for x in items], [x[1] for x in items], labels=LABELS, zero_division=0
        )[2]),
    )
    _, sens_low, sens_high = bootstrap_interval(
        [(g, p) for g, p in zip(gold_include, pred_include)],
        lambda items: (
            sum(g and p for g, p in items) / sum(g for g, _ in items)
            if sum(g for g, _ in items) else 0.0
        ),
    )
    intervals = {
        "macro_f1": {"estimate": _round(macro_f1), "lower_95": macro_low, "upper_95": macro_high},
        "screening_sensitivity": {"estimate": _round(sensitivity), "lower_95": sens_low, "upper_95": sens_high},
    }

    error_types = Counter()
    examples = defaultdict(list)
    for record, prediction in aligned:
        if record.adjudicated_label != prediction.classification:
            key = f"{record.adjudicated_label} -> {prediction.classification}"
            error_types[key] += 1
            if len(examples[key]) < 3:
                examples[key].append({
                    "document_id": record.document_id,
                    "difficulty": record.difficulty,
                    "title": record.title,
                    "rationale": prediction.rationale,
                })
    error_analysis = {
        "error_counts": dict(error_types),
        "examples": dict(examples),
        "difficulty_distribution": dict(Counter(record.difficulty for record, _ in aligned)),
    }
    return metrics, intervals, error_analysis
