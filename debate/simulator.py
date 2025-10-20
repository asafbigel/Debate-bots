from typing import List, Protocol

from .llm_adapter import LLMClientProtocol
from .display import TURN_SEPARATOR


GLOBAL_DEBATE_RULES = """
אתה משתתף בדיבייט מובנה.
מטרתך היא לשכנע בצדקתך ולהגיב באופן חד ורלוונטי לטיעוני היריב.

כללי הדיבייט הם:
1.  היצמד לנושא הדיון.
2.  תגובותיך צריכות להיות תמציתיות ו Eagious (עד 2-3 פסקאות).
3.  שמור על טון מכובד אך תקיף. תקוף את הטיעונים, לא את האדם שמולך.
4.  התגובה שלך חייבת להתייחס ישירות לטיעון האחרון שהציג היריב שלך.
"""

SYSTEM_MESSAGE_RIGHT = GLOBAL_DEBATE_RULES + """
להלן פרטי הדמות שאתה מגלם:
אתה גבר ישראלי בעל עמדות ימין. השנה היא 2025.
עליך לייצג נאמנה את השקפת העולם הימנית הרווחת בישראל.
"""

SYSTEM_MESSAGE_LEFT = GLOBAL_DEBATE_RULES + """
להלן פרטי הדמות שאתה מגלם:
את אישה ישראלית בעלת עמדות שמאל. השנה היא 2025.
עליך לייצג נאמנה את השקפת העולם השמאלית הרווחת בישראל.
"""


class DebateSimulator:
    """Simulates a debate between two personas using an LLM client.

    - Depends on an LLMClientProtocol (Dependency Inversion)
    - Returns structured strings ready for display
    """

    def __init__(self, llm_client: LLMClientProtocol):
        self.llm = llm_client

    def _extract_content(self, response: dict) -> str:
        if not response or "choices" not in response or not response["choices"]:
            raise ValueError("No response from model or invalid response format.")
        msg = response["choices"][0].message
        if not msg or not hasattr(msg, "content") or not msg.content:
            raise ValueError("Response does not contain valid 'content'.")
        return msg.content

    def simulate(self, subject: str, rounds: int = 5) -> List[str]:
        debate_history_for_llm = []
        debate_display_history: List[str] = []

        initial_user_message = f"הצג את עמדתך בנושא: {subject}"

        for i in range(rounds):
            current_speaker_role = "ימין" if i % 2 == 0 else "שמאל"
            current_system_message = SYSTEM_MESSAGE_RIGHT if current_speaker_role == "ימין" else SYSTEM_MESSAGE_LEFT

            messages_for_completion = [{"role": "system", "content": current_system_message}]
            messages_for_completion.extend(debate_history_for_llm)

            if i == 0:
                user_prompt = initial_user_message
            else:
                last_opponent_message = debate_history_for_llm[-1]["content"] if debate_history_for_llm else ""
                user_prompt = f"הגב לטיעון האחרון של הצד השני: {last_opponent_message}"

            messages_for_completion.append({"role": "user", "content": user_prompt})

            try:
                model_response = self.llm.completion(model=None, messages=messages_for_completion)
                response_content = self._extract_content(model_response)
            except Exception as exc:
                response_content = f"{current_speaker_role} נתקל בשגיאה: {exc}"
                debate_display_history.append(f"{current_speaker_role}: {response_content}")
                break

            debate_history_for_llm.append({"role": "user", "content": user_prompt})
            debate_history_for_llm.append({"role": "assistant", "content": response_content})
            debate_display_history.append(f"{current_speaker_role}: {response_content}")
            if i < rounds - 1:
                debate_display_history.append(TURN_SEPARATOR)

        return debate_display_history
