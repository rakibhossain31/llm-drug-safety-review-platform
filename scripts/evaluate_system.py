#!/usr/bin/env python
import json
from safetyreview_ai.evaluation.evaluate import evaluate_system

if __name__ == "__main__":
    print(json.dumps(evaluate_system(), indent=2))
