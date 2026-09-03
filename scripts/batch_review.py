#!/usr/bin/env python
import json
from safetyreview_ai.workflow.safety_review_graph import SafetyReviewGraph, load_synthetic_cases

graph = SafetyReviewGraph()
for case in load_synthetic_cases():
    result = graph.run(case["narrative"], case["case_id"])
    print(json.dumps({"case_id": result.case_id, "status": result.status, "valid": result.minimum_valid_case.is_valid}))
