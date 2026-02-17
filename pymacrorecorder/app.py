"""Tkinter application entry point for PyMacroRecorder."""

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Dict, List, Optional

from .config import DEFAULT_HOTKEYS, load_config, save_config
from .hotkeys import HotkeyManager, capture_hotkey_blocking
from .models import Macro
from .player import Player
from .recorder import Recorder
from .storage import load_macros_from_csv, save_macro_to_csv
from .utils import format_combo


class App(tk.Tk):
    """Main Tkinter window that orchestrates recording, playback, and storage."""

    def __init__(self) -> None:
        """Initialize the application window, services, and global hotkeys.

        :return: Nothing.
        :rtype: None
        """
        super().__init__()
        self.title("PyMacroRecorder")
        self.geometry("900x600")
        self._set_icon()

        cfg = load_config()
        self.hotkeys: Dict[str, List[str]] = cfg.get("hotkeys", DEFAULT_HOTKEYS)
        self.recorder = Recorder(self._log)
        self.player = Player(self._log)
        self.current_macro: Optional[Macro] = None

        self._build_ui()
        self._refresh_hotkey_labels()
        self.hotkey_manager = HotkeyManager(self.hotkeys, self._dispatch_hotkey)
        self.hotkey_manager.start()

    def _set_icon(self) -> None:
        """Set the window icon from the `assets` folder.

        :return: Nothing.
        :rtype: None
        """
        try:
            # Determine the base path (works for both script and PyInstaller)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                # noinspection PyProtectedMember
                base_path = Path(sys._MEIPASS)
            else:
                # Running as script
                base_path = Path(__file__).parent.parent
                print(base_path)

            icon_path = base_path / "assets" / "logo.png"
            if icon_path.exists():
                icon = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon)
            else:
                # Fallback to .ico if .png not found
                icon_ico_path = base_path / "assets" / "logo.ico"
                if icon_ico_path.exists():
                    self.iconbitmap(str(icon_ico_path))
        except Exception as e:
            # Silently fail if icon cannot be loaded
            print(f"Warning: Could not load icon: {e}")

    def _build_ui(self) -> None:
        """Build the control bar, preview tree, log area, and hotkey editor.

        :return: Nothing.
        :rtype: None
        """
        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=10, pady=5)

        self.start_rec_btn = ttk.Button(controls, text="Start Record", command=self.start_recording)
        self.stop_rec_btn = ttk.Button(controls, text="Stop Record", command=self.stop_recording,
                                       state="disabled")
        self.start_play_btn = ttk.Button(controls, text="Start Macro", command=self.start_playback)
        self.stop_play_btn = ttk.Button(controls, text="Stop Macro", command=self.stop_playback,
                                        state="disabled")
        self.save_btn = ttk.Button(controls, text="Save Macro", command=self.save_macro)
        self.load_btn = ttk.Button(controls, text="Load Macro", command=self.load_macro)
        self.delete_btn = ttk.Button(controls, text="Delete Selected",
                                     command=self._delete_selected_events)

        self.start_rec_btn.grid(row=0, column=0, padx=5, pady=2)
        self.stop_rec_btn.grid(row=0, column=1, padx=5, pady=2)
        self.start_play_btn.grid(row=0, column=2, padx=5, pady=2)
        self.stop_play_btn.grid(row=0, column=3, padx=5, pady=2)
        self.save_btn.grid(row=0, column=4, padx=5, pady=2)
        self.load_btn.grid(row=0, column=5, padx=5, pady=2)
        self.delete_btn.grid(row=0, column=6, padx=5, pady=2)

        repeat_frame = ttk.Frame(self)
        repeat_frame.pack(fill="x", padx=10, pady=2)
        ttk.Label(repeat_frame, text="Repeats (0 = infinite):").pack(side="left")
        self.repeat_var = tk.StringVar(value="1")
        self.repeat_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_var, width=6)
        self.repeat_entry.pack(side="left", padx=5)

        preview_frame = ttk.LabelFrame(self, text="Event preview")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        columns = ("#", "type", "details", "delay")
        self.preview = ttk.Treeview(preview_frame, columns=columns, show="headings", height=12)
        self.preview.heading("#", text="#")
        self.preview.heading("type", text="Type")
        self.preview.heading("details", text="Details")
        self.preview.heading("delay", text="Delay (ms)")
        for col in columns:
            self.preview.column(col, width=150, anchor="w")
        self.preview.pack(fill="both", expand=True)
        self.preview.bind("<Delete>", lambda e: self._delete_selected_events())

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_text = tk.Text(log_frame, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True)

        hotkey_frame = ttk.LabelFrame(self, text="Hotkeys")
        hotkey_frame.pack(fill="x", padx=10, pady=5)
        self.hotkey_labels: Dict[str, tk.Label] = {}
        row = 0
        for action, label in [
            ("start_record", "Start Record"),
            ("stop_record", "Stop Record"),
            ("start_macro", "Start Macro"),
            ("stop_macro", "Stop Macro"),
            ("save_macro", "Save Macro"),
            ("load_macro", "Load Macro"),
        ]:
            ttk.Label(hotkey_frame, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            hotkey_label = tk.Label(hotkey_frame, text="", relief="solid", borderwidth=1,
                                    padx=4, pady=2, cursor="hand2")
            hotkey_label.grid(row=row, column=1, sticky="w", padx=4, pady=2)
            hotkey_label.bind("<Button-1>", lambda _e, act=action: self._start_hotkey_capture(act))
            self.hotkey_labels[action] = hotkey_label
            row += 1

    def _log(self, msg: str) -> None:
        """Append a log line to the log text widget.

        :param msg: Message to display.
        :type msg: str
        :return: Nothing.
        :rtype: None
        """
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _refresh_hotkey_labels(self) -> None:
        """Refresh hotkey label text to reflect current mappings.

        :return: Nothing.
        :rtype: None
        """
        for action, label in self.hotkey_labels.items():
            combo = self.hotkeys.get(action, [])
            label.configure(text=format_combo(combo) if combo else "(none)")

    def _dispatch_hotkey(self, action: str) -> None:
        """Dispatch a captured hotkey action onto the Tkinter event loop.

        :param action: Action key to perform.
        :type action: str
        :return: Nothing.
        :rtype: None
        """
        self.after(0, self._handle_hotkey, action)

    def _handle_hotkey(self, action: str) -> None:
        """Handle hotkey actions by invoking the matching command.

        :param action: Action identifier from the hotkey map.
        :type action: str
        :return: Nothing.
        :rtype: None
        """
        if action == "start_record":
            self.start_recording()
        elif action == "stop_record":
            self.stop_recording()
        elif action == "start_macro":
            self.start_playback()
        elif action == "stop_macro":
            self.stop_playback()
        elif action == "save_macro":
            self.save_macro()
        elif action == "load_macro":
            self.load_macro()

    def start_recording(self) -> None:
        """Begin recording input events and update control states.

        :return: Nothing.
        :rtype: None
        """
        if self.recorder:
            self.start_rec_btn.configure(state="disabled")
            self.stop_rec_btn.configure(state="normal")
            self.recorder.start(list(self.hotkeys.values()))

    def stop_recording(self) -> None:
        """Stop recording and populate preview with recorded events.

        :return: Nothing.
        :rtype: None
        """
        self.start_rec_btn.configure(state="normal")
        self.stop_rec_btn.configure(state="disabled")
        events = self.recorder.stop()
        if events:
            self.current_macro = Macro(name="macro", events=events)
            self._populate_preview(self.current_macro)
        else:
            self._populate_preview(None)

    def _populate_preview(self, macro: Optional[Macro]) -> None:
        """Fill the preview tree with macro events.

        :param macro: Macro to preview or ``None`` to clear.
        :type macro: Macro | None
        :return: Nothing.
        :rtype: None
        """
        for item in self.preview.get_children():
            self.preview.delete(item)
        if not macro:
            return
        for idx, evt in enumerate(macro.events, start=1):
            detail = ", ".join(f"{k}={v}" for k, v in evt.payload.items())
            self.preview.insert("", "end", values=(idx, evt.event_type, detail,
                                                   evt.delay_ms))

    def _delete_selected_events(self, _event: Optional[tk.Event] = None) -> None:
        """Delete selected events from the current macro and update preview.

        :param _event: Optional Tk event when triggered from key binding.
        :type _event: tk.Event | None
        :return: Nothing.
        :rtype: None
        """
        if not self.current_macro or self.current_macro.is_empty():
            self._log("No macro to edit")
            return
        selection = list(self.preview.selection())
        if not selection:
            self._log("No rows selected for deletion")
            return
        # Remove events in reverse order to keep indexes stable while popping
        indexes = sorted((self.preview.index(item) for item in selection), reverse=True)
        for idx in indexes:
            if 0 <= idx < len(self.current_macro.events):
                self.current_macro.events.pop(idx)
        if self.current_macro.is_empty():
            self._log("All events deleted from macro")
        else:
            self._log(f"Deleted {len(indexes)} event(s) from macro")
        self._populate_preview(self.current_macro if not self.current_macro.is_empty() else None)

    def start_playback(self) -> None:
        """Start macro playback with the configured repeat count.

        :return: Nothing.
        :rtype: None
        """
        if not self.current_macro or self.current_macro.is_empty():
            messagebox.showwarning("Macro", "No macro loaded")
            return
        try:
            repeats = int(self.repeat_var.get())
        except ValueError:
            messagebox.showerror("Macro", "Repeat count must be an integer")
            return
        if repeats < 0:
            messagebox.showerror("Macro", "Repeat count must be >= 0")
            return
        self.start_play_btn.configure(state="disabled")
        self.stop_play_btn.configure(state="normal")
        self.player.play(self.current_macro, repeats)

    def stop_playback(self) -> None:
        """Stop macro playback and restore control states.

        :return: Nothing.
        :rtype: None
        """
        self.player.stop()
        self.start_play_btn.configure(state="normal")
        self.stop_play_btn.configure(state="disabled")

    def save_macro(self) -> None:
        """Prompt for a file name and persist the current macro to CSV.

        :return: Nothing.
        :rtype: None
        """
        if not self.current_macro or self.current_macro.is_empty():
            messagebox.showwarning("Save", "No macro to save")
            return
        name = simpledialog.askstring("Name", "Macro name",
                                      initialvalue=self.current_macro.name)
        if not name:
            return
        self.current_macro.name = name
        path_str = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV", "*.csv")], title="Save macro")
        if not path_str:
            return
        save_macro_to_csv(Path(path_str), self.current_macro)
        self._log(f"Macro '{name}' saved to {path_str}")

    def load_macro(self) -> None:
        """Load a macro from CSV and update preview and current state.

        :return: Nothing.
        :rtype: None
        """
        path_str = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")], title="Load macro")
        if not path_str:
            return
        macros = load_macros_from_csv(Path(path_str))
        if not macros:
            messagebox.showerror("Load", "No macro found")
            return
        macro = macros[0]
        if len(macros) > 1:
            names = [m.name for m in macros]
            choice = simpledialog.askstring(
                "Selection",
                f"Available macros: {', '.join(names)}\nName to load:"
            )
            if choice:
                for m in macros:
                    if m.name == choice:
                        macro = m
                        break
        self.current_macro = macro
        self._populate_preview(macro)
        self._log(f"Macro '{macro.name}' loaded")

    def _start_hotkey_capture(self, action: str) -> None:
        """Start capturing a new hotkey combination for a specific action.

        :param action: Action identifier being rebound.
        :type action: str
        :return: Nothing.
        :rtype: None
        """
        self._log(f"Capturing hotkey for {action}...")
        self.hotkey_manager.stop()

        def worker() -> None:
            combo = capture_hotkey_blocking()
            self.after(0, self._finish_capture, action, combo)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_capture(self, action: str, combo: Optional[List[str]]) -> None:
        """Finalize hotkey capture, persist configuration, and restart listener.

        :param action: Action identifier being updated.
        :type action: str
        :param combo: Captured key combination or ``None`` if invalid.
        :type combo: list[str] | None
        :return: Nothing.
        :rtype: None
        """
        if not combo or len(combo) < 2:
            self._log("Hotkey ignored (minimum 2 keys)")
        else:
            self.hotkeys[action] = combo
            save_config({"hotkeys": self.hotkeys})
            self.hotkey_manager.update(self.hotkeys)
            self._refresh_hotkey_labels()
            self._log(f"Hotkey '{action}' updated: {format_combo(combo)}")
        self.hotkey_manager.start()


def main() -> None:
    """Run the application in standalone mode.

    :return: Nothing.
    :rtype: None
    """
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
