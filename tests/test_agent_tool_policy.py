from safetyreview_ai.agents.literature_agent import BoundedLiteratureAgent
from safetyreview_ai.agents.policies import AgentPolicy


def test_agent_uses_only_approved_bounded_tools():
    policy = AgentPolicy(max_steps=6)
    result = BoundedLiteratureAgent(policy).run(
        "AGENT-1",
        "A patient treated with Glucorin developed lactic acidosis and required intensive care.",
    )
    assert result.classification == "relevant"
    assert len(result.trace) <= policy.max_steps
    assert all(step["tool"] in policy.allowed_tools for step in result.trace)
    assert "Human reviewer approval required" in result.rationale
