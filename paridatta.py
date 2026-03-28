#!/usr/bin/env python3
import sys

def main():
    """Main entry point for Paridatta."""
    # Launch GUI directly
    try:
        import gui.main_gui
        gui.main_gui.main()
    except Exception as e:
        print(f"Error launching Paridatta GUI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
