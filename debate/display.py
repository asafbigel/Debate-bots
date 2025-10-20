from abc import ABC, abstractmethod
from typing import Protocol
import sys

TURN_SEPARATOR = "---DEBATE_TURN_SEPARATOR---"


class DisplayStrategy(Protocol):
    def show(self, text: str, title: str = "תוצאה") -> None:
        ...


class ConsoleDisplay:
    def show(self, text: str, title: str = "תוצאה") -> None:
        print(title)
        print("=" * len(title))
        print(text)


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
