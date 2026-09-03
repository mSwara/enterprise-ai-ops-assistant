import pytest
from app.graph.supervisor import route_request
from tests.routing_dataset import ROUTING_TEST_CASES


@pytest.mark.parametrize("question,expected_agent", ROUTING_TEST_CASES)
def test_routing_matches_expected(question, expected_agent):
    decision = route_request(question)
    assert decision.agent == expected_agent, (
        f"Expected '{expected_agent}' but got '{decision.agent}'. "
        f"Reason given: {decision.reason}"
    )