#!/usr/bin/env python
import argparse, json
from safetyreview_ai.rag.qa import answer_guidance_question

parser = argparse.ArgumentParser()
parser.add_argument("question")
args = parser.parse_args()
print(json.dumps(answer_guidance_question(args.question), indent=2))
