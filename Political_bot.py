import os
import json
from litellm import completion

# נגדיר מפריד ייחודי בין התורות
TURN_SEPARATOR = "---DEBATE_TURN_SEPARATOR---"


# Import GUI libraries - prioritize PyQt5, fallback to Tkinter
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
    from PyQt5.QtCore import Qt
    import sys
    _has_pyqt = True
except ImportError:
    import tkinter as tk
    from tkinter import scrolledtext, font as tkfont
    _has_pyqt = False

# --- Configuration Loading ---
def load_config(filename="config.json"):
    """Loads configuration settings from a JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please create it with your model configuration.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filename}. Check file format.")
        exit(1)

def load_keys(filename="keys.json"):
    """Loads API keys from a JSON file and sets them as environment variables."""
    try:
        with open(filename, 'r') as file:
            keys = json.load(file)
            os.environ["OPENAI_API_KEY"] = keys.get("OPENAI_API_KEY", "")
            os.environ["ANTHROPIC_API_KEY"] = keys.get("ANTHROPIC_API_KEY", "")
            os.environ["GEMINI_API_KEY"] = keys.get("GEMINI_API_KEY", "")
            # Add other keys as needed
    except FileNotFoundError:
        print(f"Error: {filename} not found. Please create it with your API keys.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filename}. Check file format.")
        exit(1)

# Load configurations and keys at the start
config = load_config()
_model = config.get("model")
if not _model:
    print("Error: 'model' not specified in config.json. Please ensure it's set.")
    exit(1)

load_keys() # This will set the necessary environment variables for litellm

# --- GUI Utility Functions ---
def display_in_window(text: str, title: str = "תוצאה") -> None:
    """
    Displays the given text in a new window with proper Hebrew support and colors.
    Prioritizes PyQt5 for better RTL support, falls back to Tkinter.
    """
    # Define colors for debate roles
    COLOR_RIGHT = "#0000FF"  # Blue
    COLOR_LEFT = "#FF0000"   # Red
    COLOR_SEPARATOR = "#808080" # Grey - for separation lines and the subject title

    # Define the same unique separator used in main()
    TURN_SEPARATOR = "---DEBATE_TURN_SEPARATOR---"

    if _has_pyqt:
        # --- PyQt5 Implementation ---
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        window = QWidget()
        window.setWindowTitle(title)
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Set base font and crucial RTL properties for the QTextEdit widget
        text_edit.setFontFamily("Arial") # Good general font for Hebrew
        text_edit.setFontPointSize(14)
        text_edit.setLayoutDirection(Qt.RightToLeft) # Overall layout direction
        text_edit.setAlignment(Qt.AlignRight) # Align text to the right within the widget
        # text_edit.setTextOption(QTextOption(Qt.RightToLeft)) # Re-add if your PyQt5 supports it, for comprehensive RTL control. It was commented out due to previous AttributeError.

        # Process the input text block by block using the custom separator
        blocks = text.split(TURN_SEPARATOR) # **** IMPORTANT CHANGE HERE ****

        for i, block_content in enumerate(blocks): # Renamed 'block' to 'block_content' for clarity
            if not block_content.strip(): # Skip any empty blocks resulting from split
                continue
            
            # --- PARSING THE ROLE AND CONTENT ---
            role_indicator_key = "Unknown" # Internal key like "Right", "Left", "Subject"
            display_prefix = "" # The Hebrew prefix like "ימין:" or "נושא הדיבייט:"
            content_to_display = block_content # The actual text content after the role prefix

            # Check for specific role prefixes
            if block_content.startswith("ימין:"): # Checking for Hebrew role name
                role_indicator_key = "Right" 
                display_prefix = "ימין:"
                content_to_display = block_content[len("ימין:"):].strip()
            elif block_content.startswith("שמאל:"): # Checking for Hebrew role name
                role_indicator_key = "Left" 
                display_prefix = "שמאל:"
                content_to_display = block_content[len("שמאל:"):].strip()
            elif block_content.startswith("Subject:"): # Checking for English "Subject:" prefix from main()
                role_indicator_key = "Subject"
                display_prefix = "נושא הדיבייט:" # Display in Hebrew
                content_to_display = block_content[len("Subject:"):].strip()
            else:
                # If no known prefix, treat the whole block as content (e.g., if there's an error)
                content_to_display = block_content

            # Apply HTML formatting based on the identified role
            if role_indicator_key == "Right":
                text_edit.append(f"<span style='color: {COLOR_RIGHT}; font-weight: bold;'>{display_prefix}</span> <span style='color: black;'>{content_to_display}</span>")
            elif role_indicator_key == "Left":
                text_edit.append(f"<span style='color: {COLOR_LEFT}; font-weight: bold;'>{display_prefix}</span> <span style='color: black;'>{content_to_display}</span>")
            elif role_indicator_key == "Subject": 
                text_edit.append(f"<span style='color: {COLOR_SEPARATOR}; font-weight: bold;'>{display_prefix}</span> <span style='color: black;'>{content_to_display}</span>")
            else:
                # Default styling for any other unexpected text that didn't match a role
                text_edit.append(f"<span style='color: black;'>{content_to_display}</span>")

            # Add a dashed horizontal separator line between turns (but not after the very last block)
            if i < len(blocks) - 1: # This condition ensures separators are only BETWEEN blocks
                text_edit.append(f"<hr style='border: 1px dashed {COLOR_SEPARATOR}; margin-top: 10px; margin-bottom: 10px;'>")
        
        # --- Finalize PyQt5 Window ---
        layout.addWidget(text_edit)
        btn = QPushButton("סגור")
        btn.clicked.connect(window.close)
        layout.addWidget(btn)
        window.setLayout(layout)
        window.resize(900, 600) # Set a reasonable default size
        window.show()
        sys.exit(app.exec_()) # Use sys.exit to ensure proper application exit
    else:
        # --- Tkinter Fallback Implementation ---
        print("PyQt5 not available, falling back to Tkinter.") # Indicate fallback in console
        root = tk.Tk()
        root.title(title)
        
        # Define fonts for Tkinter tags
        mono_font = tkfont.Font(family="Consolas", size=14)
        bold_mono_font = tkfont.Font(family="Consolas", size=14, weight="bold")

        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=mono_font, width=90, height=28)
        text_area.pack(expand=True, fill='both')
        
        # Configure text tags for different roles and styles
        text_area.tag_configure('RightTag', foreground=COLOR_RIGHT, font=bold_mono_font)
        text_area.tag_configure('LeftTag', foreground=COLOR_LEFT, font=bold_mono_font)
        text_area.tag_configure('SeparatorTag', foreground=COLOR_SEPARATOR, font=mono_font)
        text_area.tag_configure('DefaultContentTag', foreground='black', font=mono_font) # For content
        text_area.tag_configure('SubjectTag', foreground=COLOR_SEPARATOR, font=bold_mono_font) # For Subject title

        # Attempt to set justification for RTL (Tkinter's RTL support is more basic)
        try:
            text_area.configure(justify='right')
        except Exception:
            pass # Not all tkinter versions/systems support 'justify' for ScrolledText

        # Process text block by block for Tkinter
        blocks = text.split(TURN_SEPARATOR) # **** IMPORTANT CHANGE HERE ****

        for i, block_content in enumerate(blocks):
            if not block_content.strip():
                continue

            # --- PARSING THE ROLE AND CONTENT ---
            role_indicator_key = "Unknown"
            display_prefix = ""
            content_to_display = block_content

            if block_content.startswith("ימין:"): # Checking for Hebrew role name
                role_indicator_key = "Right"
                display_prefix = "ימין:"
                content_to_display = block_content[len("ימין:"):].strip()
            elif block_content.startswith("שמאל:"): # Checking for Hebrew role name
                role_indicator_key = "Left"
                display_prefix = "שמאל:"
                content_to_display = block_content[len("שמאל:"):].strip()
            elif block_content.startswith("Subject:"): # Checking for English "Subject:" prefix from main()
                role_indicator_key = "Subject"
                display_prefix = "נושא הדיבייט:"
                content_to_display = block_content[len("Subject:"):].strip()
            else:
                content_to_display = block_content

            # Apply Unicode Bidirectional Override to Hebrew content
            rtl_content = '\u202B' + content_to_display if any(0x590 <= ord(c) <= 0x5FF for c in content_to_display) else content_to_display

            # Insert text with appropriate tags
            if role_indicator_key == "Right":
                text_area.insert(tk.END, display_prefix + " ", 'RightTag') # Insert prefix with role tag
                text_area.insert(tk.END, rtl_content + '\n', 'DefaultContentTag') # Insert content with default tag
            elif role_indicator_key == "Left":
                text_area.insert(tk.END, display_prefix + " ", 'LeftTag')
                text_area.insert(tk.END, rtl_content + '\n', 'DefaultContentTag')
            elif role_indicator_key == "Subject":
                text_area.insert(tk.END, display_prefix + " ", 'SubjectTag')
                text_area.insert(tk.END, rtl_content + '\n', 'DefaultContentTag')
            else:
                # If no specific role prefix, insert the block as is
                text_area.insert(tk.END, '\u202B' + block_content + '\n', 'DefaultContentTag')

            # Add separator between turns (but not after the last one)
            if i < len(blocks) - 1: # This condition ensures separators are only BETWEEN blocks
                text_area.insert(tk.END, '-'*80 + '\n', 'SeparatorTag')
                text_area.insert(tk.END, '\n') # Add an extra newline for spacing

        text_area.configure(state='disabled') # Make text area read-only
        root.resizable(True, True) # Allow window resizing
        root.mainloop()


# --- Model Response Handling ---
def get_response_content(response: dict) -> str:
    """
    Extracts the content from the model response.
    Raises ValueError if the response is invalid.
    """
    if not response or "choices" not in response or not response["choices"]:
        raise ValueError("No response from model or invalid response format.")
    
    msg = response["choices"][0].message
    if not msg or not hasattr(msg, "content") or not msg.content:
        raise ValueError("Response does not contain valid 'content'.")
        
    return msg.content

# --- Topic Generation ---
def get_title_subject() -> str:
    """
    Gets a current and significant topic in Israeli public discourse,
    formulated as a single question suitable for a debate between right and left positions.
    """
    system_message = (
        "אתה מומחה לנושאים פוליטיים וחברתיים בישראל.\n"
        "תפקידך הוא לזהות נושא אקטואלי ומשמעותי הנמצא במרכז השיח הציבורי בישראל.\n"
        "עליך לנסח את הנושא **בצורה של שאלה אחת בלבד**,\n"
        "שתוכל לשמש כנקודת מוצא לדיון מעמיק.\n"
        "השאלה צריכה לאפשר טיעונים חזקים משני צידי המפה הפוליטית (ימין ושמאל)\n"
        "וצריכה להיות מורכבת מספיק כדי לאפשר דיון מעמיק, ולא חד משמעי."
    )
    content = (
        "נסח שאלה אחת בלבד, אקטואלית ומשמעותית,\n"
        "שתשמש כנושא לדיבייט בין עמדות ימין ושמאל בישראל.\n"
        "השאלה צריכה לעסוק בסוגיה פוליטית או חברתית מרכזית שנמצאת כרגע בכותרות."
    )
    
    messages_payload = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": content}
    ]
    
    try:
        model_response = completion(model=_model, messages=messages_payload, temperature=0.7)
        response = get_response_content(model_response)
        return response
    except Exception as e:
        print(f"Error getting debate subject from model: {e}")
        return "נושא הדיבייט לא הוגדר עקב שגיאה." # Fallback subject

# --- Debate System Messages ---
# These are constant messages defining the AI's persona and debate rules.
GLOBAL_DEBATE_RULES = """
אתה משתתף בדיבייט מובנה.
מטרתך היא לשכנע בצדקתך ולהגיב באופן חד ורלוונטי לטיעוני היריב.

כללי הדיבייט הם:
1.  היצמד לנושא הדיון.
2.  תגובותיך צריכות להיות תמציתיות וענייניות (עד 2-3 פסקאות).
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

# --- Debate Simulation ---
def simulate_debate(subject: str, rounds: int = 5):
    """
    Simulates a debate between right and left positions on a given subject.
    Args:
        subject (str): The debate subject, formatted as a question.
        rounds (int): Number of debate rounds to simulate (each round is one turn per side).
    Returns:
        list: A list of strings, where each string represents a full turn of a speaker
              formatted as "Role: Content" (e.g., "ימין: זו התגובה שלי").
    """
    debate_history_for_llm = [] # Stores full message history for LLM (includes system/user/assistant roles)
    debate_display_history = []  # Stores formatted strings for display (e.g., "ימין: תוכן")
    
    # Initial prompt for the first speaker (ימין)
    initial_user_message = f"הצג את עמדתך בנושא: {subject}"
    
    print(f"\n--- הדיבייט מתחיל: {subject} ---") # Updated print message
    
    for i in range(rounds):
        current_speaker_role = "ימין" if i % 2 == 0 else "שמאל"
        current_system_message = SYSTEM_MESSAGE_RIGHT if current_speaker_role == "ימין" else SYSTEM_MESSAGE_LEFT

        print(f"\nסיבוב {i + 1} - תור של {current_speaker_role}:") # Updated print message

        # Build messages payload for litellm
        messages_for_completion = [
            {"role": "system", "content": current_system_message}
        ]
        
        # Add the existing conversation history for context
        messages_for_completion.extend(debate_history_for_llm) 

        # Determine the user's prompt for this turn
        if i == 0:
            user_prompt = initial_user_message
        else:
            # The last message in debate_history_for_llm should be the opponent's response
            last_opponent_message = debate_history_for_llm[-1]["content"] if debate_history_for_llm else ""
            user_prompt = f"הגב לטיעון האחרון של הצד השני: {last_opponent_message}"

        messages_for_completion.append({"role": "user", "content": user_prompt})

        try:
            model_response = completion(model=_model, messages=messages_for_completion)
            response_content = get_response_content(model_response)
        except Exception as e:
            print(f"שגיאה במהלך תור של {current_speaker_role}: {e}") # Updated print message
            response_content = f"הצד {current_speaker_role} נתקל בשגיאה ולא יכול להמשיך את הדיבייט."
            # Store error message for display and break
            debate_display_history.append(f"{current_speaker_role}: {response_content}")
            break

        print(f"{current_speaker_role}: {response_content}\n")
        
        # Append the current turn's user prompt and assistant response to the history for the LLM
        debate_history_for_llm.append({"role": "user", "content": user_prompt})
        debate_history_for_llm.append({"role": "assistant", "content": response_content})
        
        # Store the full "Role: Content" string for display history
        debate_display_history.append(f"{current_speaker_role}: {response_content}") 

    print("--- הדיבייט הסתיים ---") # Updated print message
    return debate_display_history


# --- Main Execution ---
def main():
    """Main function to run the AI debate simulation."""
    print("Fetching debate subject...")
    subject = get_title_subject()
    print(f"Selected subject for debate:")
    print(subject)

    debate_messages = simulate_debate(subject, rounds=5) # Simulate 5 rounds (5 turns per side)
    

    # נבנה את רשימת הטקסטים לתצוגה, כולל הנושא והתורות
    display_items = []

    for message_content in debate_messages:
        display_items.append(message_content) # כבר מכיל "ימין: תוכן" או "שמאל: תוכן"

    formatted_debate_history = TURN_SEPARATOR.join(display_items)
    display_in_window(formatted_debate_history, title="תוצאות הדיבייט")

if __name__ == "__main__":
    main()