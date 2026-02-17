# Contributing to PyMacroRecorder

Thanks for your interest in improving PyMacroRecorder!

## Getting started

1. Install Python 3.10+. (3.14 is recommended for latest features)
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: `.venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. Run the app locally:
   ```bash
   python main.py
   ```

## Development guidelines

- Keep `main.py` limited to application bootstrap; place logic inside `pymacrorecorder/`.
- Prefer small, focused classes and functions with clear responsibilities.
- Ensure new features work on both Windows and Linux.
- When adding storage or settings, keep JSON format and update `pymacrorecorder/config.py` as needed.

## Docstrings

- All Python docstrings must use Sphinx reStructuredText (reST) style.
- Include ``:param:``, ``:type:``, ``:return:``, ``:rtype:``, and ``:raises:`` as appropriate.
- Google or NumPy docstring styles are not allowed.
- Provide docstrings for every module, class, and public function/method.

## Submitting changes

- Create a feature branch for your work.
- Add or update documentation for new behavior.
- Open a pull request summarizing the change, testing performed, and any platform-specific notes.
