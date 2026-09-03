#!/usr/bin/env python
import argparse
from safetyreview_ai.workflow.safety_review_graph import SafetyReviewGraph

parser = argparse.ArgumentParser()
parser.add_argument("narrative")
parser.add_argument("--case-id")
args = parser.parse_args()
print(SafetyReviewGraph().run(args.narrative, args.case_id).model_dump_json(indent=2))
