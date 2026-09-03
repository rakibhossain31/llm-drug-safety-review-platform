#!/usr/bin/env python
from __future__ import annotations

import argparse

from safetyreview_ai.benchmark.runner import write_reports

parser = argparse.ArgumentParser(description="Generate reproducible literature benchmark reports.")
parser.add_argument("--split", choices=["train", "dev", "test", "all"], default="all")
args = parser.parse_args()
for name, path in write_reports(args.split).items():
    print(f"{name}: {path}")
