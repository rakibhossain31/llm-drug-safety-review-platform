#!/usr/bin/env python
import argparse
from safetyreview_ai.pv.literature import screen_literature

parser = argparse.ArgumentParser()
parser.add_argument("text")
parser.add_argument("--id", default="CLI-ABSTRACT")
parser.add_argument("--architecture", choices=["rule_based", "single_step", "multi_step", "agentic"], default="multi_step")
parser.add_argument("--prompt-id", default="literature_evidence_first_v1")
parser.add_argument("--use-optional-llm", action="store_true")
args = parser.parse_args()
print(screen_literature(args.id, args.text, args.architecture, args.prompt_id, args.use_optional_llm).model_dump_json(indent=2))
