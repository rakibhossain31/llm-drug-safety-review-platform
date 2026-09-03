#!/usr/bin/env python
import json

from safetyreview_ai.core.config import PROJECT_ROOT
from safetyreview_ai.monitoring.monitor import build_monitoring_report


if __name__ == "__main__":
    report = build_monitoring_report()
    output = PROJECT_ROOT / "data" / "monitoring_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
