import pytest

from debate.simulator import DebateSimulator


class MockLLM:
    def __init__(self, responses):
        self._responses = responses

    def completion(self, *, model, messages, temperature=0.7):
        # Return next response shaped like litellm's return value
        text = self._responses.pop(0)
        class Msg:
            def __init__(self, content):
                self.content = content

        return {"choices": [type("C", (), {"message": Msg(text)})()]}


def test_simulate_basic():
    responses = [
        "תשובת ימין ראשונה",
        "תשובת שמאל ראשונה",
        "תשובת ימין שנייה",
    ]
    mock = MockLLM(responses.copy())
    sim = DebateSimulator(llm_client=mock)
    out = sim.simulate("האם צריך?", rounds=3)
    assert len(out) == 3
    assert out[0].startswith("ימין:")
    assert out[1].startswith("שמאל:")
