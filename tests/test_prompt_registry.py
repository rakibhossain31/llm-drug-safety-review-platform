from safetyreview_ai.prompts.registry import PromptRegistry


def test_prompt_registry_loads_experiment_variants():
    prompts = PromptRegistry().list()
    assert len(prompts) >= 4
    assert {p.strategy for p in prompts} >= {"zero_shot", "few_shot", "evidence_first", "self_check"}
