"""
Legacy entry point - redirects to main.py

For new usage, please use:
  python main.py --ui web      # For web UI
  python main.py --ui gradio   # For Gradio UI

This file is kept for backward compatibility.
"""
import sys

from main import main

if __name__ == "__main__":
    # Default to web UI for legacy compatibility
    sys.argv.append("--ui")
    sys.argv.append("web")
    main()
