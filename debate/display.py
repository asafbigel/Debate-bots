from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
import sys

TURN_SEPARATOR = "---DEBATE_TURN_SEPARATOR---"


from typing import List, Protocol


class DisplayStrategy(Protocol):
    def show(self, text: str, title: str = "תוצאה") -> None:
        ...

    def get_user_selection(self, options: List[str], prompt: str) -> Optional[str]:
        ...


class ConsoleDisplay:
    def show(self, text: str, title: str = "תוצאה") -> None:
        print(title)
        print("=" * len(title))
        print(text)

    def get_user_selection(self, options: List[str], prompt: str) -> Optional[str]:
        print(prompt)
        for i, option in enumerate(options):
            print(f"{i + 1}. {option}")
        while True:
            try:
                choice = input("בחר נושא לדיבייט (הכנס מספר): ")
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return options[index]
                else:
                    print("בחירה לא חוקית. נסה שוב.")
            except ValueError:
                print("קלט לא חוקי. אנא הכנס מספר.")


def _has_pyqt() -> bool:
    try:
        import PyQt5  # noqa: F401
        return True
    except Exception:
        return False


class GUIDisplay:
    """A GUI display that prefers PyQt5 and falls back to Tkinter.

    Keeps UI code separate from business logic (Single Responsibility).
    """

    def __init__(self):
        self._pyqt_available = _has_pyqt()

    def show(self, text: str, title: str = "תוצאה") -> None:
        if self._pyqt_available:
            self._show_pyqt(text, title)
        else:
            self._show_tk(text, title)

    def _show_pyqt(self, text: str, title: str) -> None:
        from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
        from PyQt5.QtCore import Qt
        import sys as _sys

        app = QApplication.instance()
        if app is None:
            app = QApplication(_sys.argv)

        window = QWidget()
        window.setWindowTitle(title)
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFontFamily("Arial")
        text_edit.setFontPointSize(14)
        text_edit.setLayoutDirection(Qt.RightToLeft)
        text_edit.setAlignment(Qt.AlignRight)

        # Enhanced split and formatting using TURN_SEPARATOR
        blocks = text.split(TURN_SEPARATOR)
        for i, block in enumerate(blocks):
            if not block.strip():
                continue
            
            # Assuming block starts with "Speaker: Content"
            if ":" in block:
                speaker, content = block.split(":", 1)
                # Assign colors based on speaker, e.g., "ימין" (Right) and "שמאל" (Left)
                if "ימין" in speaker:
                    speaker_color = "blue"
                elif "שמאל" in speaker:
                    speaker_color = "red"
                else:
                    speaker_color = "black" # Default color

                formatted_block = f"<p><strong style='color:{speaker_color};'>{speaker}:</strong>{content}</p>"
            else:
                formatted_block = f"<p>{block}</p>" # Fallback for unexpected format

            text_edit.append(formatted_block)
            if i < len(blocks) - 1:
                text_edit.append("<hr>") # Horizontal rule as a separator

        layout.addWidget(text_edit)
        btn = QPushButton("סגור")
        btn.clicked.connect(window.close)
        layout.addWidget(btn)
        window.setLayout(layout)
        window.resize(900, 600)
        window.show()
        _sys.exit(app.exec_())

    def _show_tk(self, text: str, title: str) -> None:
        import tkinter as tk
        from tkinter import scrolledtext, font as tkfont

        root = tk.Tk()
        root.title(title)
        mono_font = tkfont.Font(family="Consolas", size=14)
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=mono_font, width=90, height=28)
        text_area.pack(expand=True, fill='both')

        text_area.tag_config('right', foreground='blue', font=(mono_font.cget('family'), mono_font.cget('size'), 'bold'))
        text_area.tag_config('left', foreground='red', font=(mono_font.cget('family'), mono_font.cget('size'), 'bold'))
        text_area.tag_config('separator', foreground='gray', font=(mono_font.cget('family'), mono_font.cget('size'), 'normal'))

        blocks = text.split(TURN_SEPARATOR)
        for i, block in enumerate(blocks):
            if not block.strip():
                continue
            
            if ":" in block:
                speaker, content = block.split(":", 1)
                if "ימין" in speaker:
                    text_area.insert(tk.END, speaker + ":", 'right')
                    text_area.insert(tk.END, content + '\n')
                elif "שמאל" in speaker:
                    text_area.insert(tk.END, speaker + ":", 'left')
                    text_area.insert(tk.END, content + '\n')
                else:
                    text_area.insert(tk.END, block + '\n')
            else:
                text_area.insert(tk.END, block + '\n')

            if i < len(blocks) - 1:
                text_area.insert(tk.END, '-'*80 + '\n', 'separator')

        text_area.configure(state='disabled')
        root.resizable(True, True)
        root.mainloop()

    def get_user_selection(self, options: List[str], prompt: str) -> Optional[str]:
        if self._pyqt_available:
            return self._get_user_selection_pyqt(options, prompt)
        else:
            return self._get_user_selection_tk(options, prompt)

    def _get_user_selection_pyqt(self, options: List[str], prompt: str) -> Optional[str]:
        from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QDialog
        from PyQt5.QtCore import Qt
        import sys as _sys

        app = QApplication.instance()
        if app is None:
            app = QApplication(_sys.argv)

        dialog = QDialog()
        dialog.setWindowTitle("בחירת נושא דיבייט")
        layout = QVBoxLayout()

        label = QLabel(prompt)
        label.setAlignment(Qt.AlignRight)
        layout.addWidget(label)

        list_widget = QListWidget()
        list_widget.setLayoutDirection(Qt.RightToLeft)
        for i, option in enumerate(options):
            list_widget.addItem(f"{i + 1}. {option}")
        layout.addWidget(list_widget)

        select_button = QPushButton("בחר")
        select_button.clicked.connect(dialog.accept)
        layout.addWidget(select_button)

        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_items = list_widget.selectedItems()
            if selected_items:
                selected_text = selected_items[0].text()
                # Extract the topic text by removing the numbering
                return ". ".join(selected_text.split(". ")[1:])
        return None

    def _get_user_selection_tk(self, options: List[str], prompt: str) -> Optional[str]:
        import tkinter as tk
        from tkinter import simpledialog, messagebox

        class SelectionDialog(simpledialog.Dialog):
            def body(self, master):
                tk.Label(master, text=prompt).pack()
                self.listbox = tk.Listbox(master)
                for i, option in enumerate(options):
                    self.listbox.insert(tk.END, f"{i + 1}. {option}")
                self.listbox.pack()
                return self.listbox # initial focus

            def apply(self):
                selection_index = self.listbox.curselection()
                if selection_index:
                    selected_text = self.listbox.get(selection_index[0])
                    self.result = ". ".join(selected_text.split(". ")[1:])
                else:
                    self.result = None

        root = tk.Tk()
        root.withdraw() # Hide the main window
        dialog = SelectionDialog(root, "בחירת נושא דיבייט")
        root.destroy() # Destroy the hidden main window
        return dialog.result
