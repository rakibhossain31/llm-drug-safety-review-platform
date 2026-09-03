#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from safetyreview_ai.benchmark.runner import run_comparison

parser = argparse.ArgumentParser(description="Compare rule, single-step, multi-step, and agentic literature screening.")
parser.add_argument("--split", choices=["train", "dev", "test", "all"], default="test")
args = parser.parse_args()
print(json.dumps(run_comparison(args.split), indent=2))
