"""CLI entry point for running the PyMacroRecorder application."""

from pymacrorecorder.app import App


def main() -> None:
    """Launch the Tkinter application window and start the main event loop.

    :return: Nothing.
    :rtype: None
    """
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
