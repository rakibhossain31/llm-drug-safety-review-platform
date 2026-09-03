#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from safetyreview_ai.rag.qa import answer_guidance_question
from safetyreview_ai.workflow.safety_review_graph import SafetyReviewGraph, load_synthetic_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    case = load_synthetic_cases()[0]
    result = SafetyReviewGraph().run(case["narrative"], case["case_id"])
    guidance = answer_guidance_question("What are the minimum criteria for a valid safety case?")
    if args.compact:
        print(
            json.dumps(
                {
                    "case_id": result.case_id,
                    "valid": result.minimum_valid_case.is_valid,
                    "guidance_source": guidance["citations"][0]["source"],
                }
            )
        )
    else:
        print("=== SYNTHETIC CASE REVIEW ===")
        print(result.model_dump_json(indent=2))
        print("\n=== GUIDANCE QA ===")
        print(json.dumps(guidance, indent=2))


if __name__ == "__main__":
    main()
