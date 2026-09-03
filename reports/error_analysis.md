# Error Analysis

Synthetic benchmark error review by architecture.

## rule_based

Errors: `{"possibly relevant -> relevant": 30, "not relevant -> relevant": 24, "not relevant -> possibly relevant": 16}`

## single_step

Errors: `{"relevant -> possibly relevant": 1, "possibly relevant -> relevant": 30}`

## multi_step

Errors: `{"relevant -> possibly relevant": 1, "possibly relevant -> relevant": 20}`

## agentic

Errors: `{"relevant -> possibly relevant": 1, "possibly relevant -> relevant": 30}`
