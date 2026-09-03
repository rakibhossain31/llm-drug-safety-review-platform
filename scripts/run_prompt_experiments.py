#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from safetyreview_ai.benchmark.runner import run_prompt_experiments

parser = argparse.ArgumentParser(description="Compare literature-screening prompt strategies.")
parser.add_argument("--split", choices=["train", "dev", "test", "all"], default="test")
args = parser.parse_args()
print(json.dumps(run_prompt_experiments(args.split), indent=2))
