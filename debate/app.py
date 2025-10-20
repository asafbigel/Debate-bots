from typing import Optional

from .config import ConfigLoader, KeysLoader
from .llm_adapter import LiteLLMAdapter
from .display import GUIDisplay, ConsoleDisplay
from .simulator import DebateSimulator


class AppFactory:
    """Factory to create application components.

    Demonstrates Factory pattern and centralizes wiring so callers remain simple.
    """

    @staticmethod
    def create(config_path: str = "config.json", keys_path: str = "keys.json", gui: bool = True):
        cfg_loader = ConfigLoader(config_path)
        config = cfg_loader.load()

        keys_loader = KeysLoader(keys_path)
        keys_loader.load()

        model = config.get("model")
        if not model:
            raise RuntimeError("Model not specified in configuration")

        llm = LiteLLMAdapter(model=model)

        display = GUIDisplay() if gui else ConsoleDisplay()

        simulator = DebateSimulator(llm_client=llm)

        return {
            "config": config,
            "llm": llm,
            "display": display,
            "simulator": simulator,
        }


def run_app(gui: bool = True, rounds: int = 5):
    components = AppFactory.create(gui=gui)
    simulator: DebateSimulator = components["simulator"]
    display = components["display"]

    # Use the LLM to get the debate title subject, but keep this logic small here
    from .simulator import GLOBAL_DEBATE_RULES
    # The original project provided a dedicated function to get title - keep minimal approach
    # Reuse the model to query for a subject
    messages = [
        {"role": "system", "content": "אתה מומחה לנושאים פוליטיים וחברתיים בישראל."},
        {"role": "user", "content": "נסח 3-5 שאלות אקטואליות ומשמעותיות, שכל אחת מהן יכולה לשמש כנושא דיבייט בין ימין לשמאל בישראל. הצג כל שאלה ברשימה ממוספרת."},
    ]

    try:
        response = components["llm"].completion(model=None, messages=messages)
        topics_raw = response["choices"][0].message.content
        topics = [line.strip() for line in topics_raw.split('\n') if line.strip() and line[0].isdigit()]
        
        if not topics:
            subject_text = "נושא הדיבייט לא הוגדר עקב שגיאה."
        else:
            subject_text = display.get_user_selection(topics, "בחר נושא לדיבייט:")
            if not subject_text:
                subject_text = "נושא הדיבייט לא נבחר, מתחיל עם נושא ברירת מחדל." # Fallback if user cancels
                print("User cancelled topic selection. Starting with a default topic.")
                subject_text = topics[0] # Use the first topic as default if user cancels
    except Exception:
        subject_text = "נושא הדיבייט לא הוגדר עקב שגיאה."

    debate_messages = components["simulator"].simulate(subject_text, rounds=rounds)

    # Format for display
    formatted = "\n".join(debate_messages)
    display.show(formatted, title="תוצאות הדיבייט")
