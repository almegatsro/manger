import os
import sys
import re
from pathlib import Path

# Keep all file operations inside this directory
BASE_DIR = Path(__file__).parent.resolve()

VALID_NAME_RE = re.compile(r"^[\w\-. ]+$")


def safe_path(filename: str) -> Path:
    """Return a safe Path inside BASE_DIR for a filename. Raises ValueError on invalid names."""
    if not filename:
        raise ValueError("Filename cannot be empty")
    if ".." in filename or filename.startswith(('/', '\\')):
        raise ValueError("Invalid filename")
    if not VALID_NAME_RE.match(filename):
        raise ValueError("Filename contains invalid characters")
    return (BASE_DIR / filename).resolve()


def ensure_in_base(path: Path):
    if not str(path).startswith(str(BASE_DIR)):
        raise ValueError("Operation outside allowed directory")


def list_files():
    files = [p.name for p in BASE_DIR.iterdir() if p.is_file()]
    if not files:
        print("No files found in the project directory.")
        return
    print("Files in project directory:")
    for f in files:
        print(" -", f)


def create_file():
    try:
        name = input("Enter new filename (e.g. notes.txt): ").strip()
        path = safe_path(name)
        ensure_in_base(path)
        if path.exists():
            print("File already exists. Use write/append options to modify it.")
            return
        path.write_text("")
        print(f"Created file: {path.name}")
    except Exception as e:
        print("Error:", e)


def view_file():
    try:
        name = input("Enter filename to view: ").strip()
        path = safe_path(name)
        ensure_in_base(path)
        if not path.exists():
            print("File does not exist.")
            return
        content = path.read_text()
        print("\n--- File content start ---\n")
        print(content)
        print("\n--- File content end ---\n")
    except Exception as e:
        print("Error:", e)


def write_file():
    try:
        name = input("Enter filename to write (will overwrite): ").strip()
        path = safe_path(name)
        ensure_in_base(path)
        print("Enter the content. Finish input with a single line containing only: EOF")
        lines = []
        while True:
            line = input()
            if line == "EOF":
                break
            lines.append(line)
        path.write_text("\n".join(lines))
        print(f"Wrote {len(lines)} lines to {path.name}")
    except Exception as e:
        print("Error:", e)


def append_file():
    try:
        name = input("Enter filename to append to: ").strip()
        path = safe_path(name)
        ensure_in_base(path)
        if not path.exists():
            create = input("File doesn't exist. Create it? (y/n): ").lower()
            if create != 'y':
                return
        print("Enter lines to append. Finish input with a single line containing only: EOF")
        with path.open("a", encoding="utf-8") as fh:
            while True:
                line = input()
                if line == "EOF":
                    break
                fh.write(line + "\n")
        print(f"Appended to {path.name}")
    except Exception as e:
        print("Error:", e)


def erase_file():
    try:
        name = input("Enter filename to erase (truncate): ").strip()
        path = safe_path(name)
        ensure_in_base(path)
        if not path.exists():
            print("File does not exist.")
            return
        confirm = input(f"Are you sure you want to erase all content of '{path.name}'? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        path.write_text("")
        print(f"Erased content of {path.name}")
    except Exception as e:
        print("Error:", e)


def delete_file():
    try:
        name = input("Enter filename to delete: ").strip()
        path = safe_path(name)
        ensure_in_base(path)
        if not path.exists():
            print("File does not exist.")
            return
        confirm = input(f"Are you sure you want to DELETE '{path.name}'? This cannot be undone. (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            return
        path.unlink()
        print(f"Deleted {path.name}")
    except Exception as e:
        print("Error:", e)


def run_animation():
    """Run a fun animation imported from animton.py if available."""
    try:
        # Import locally so this script still runs if animton.py is missing
        import animton
        print("Launching a short animation for fun...\n")
        # Call a simple non-interactive animation function
        try:
            animton.text_animation("Have fun! This is a small typing animation.", delay=0.03)
            animton.progress_bar_animation(2)
        except Exception:
            # If animton API changes, fallback to a simple spinner
            spinner = ['|', '/', '-', '\\']
            import time
            for i in range(20):
                print(f"\r{spinner[i % len(spinner)]} Enjoy!", end="", flush=True)
                time.sleep(0.1)
            print()
    except ImportError:
        print("No animation module found (animton.py). Create it or place it in the same folder to enable animations.")


def show_menu():
    print("=" * 60)
    print(" FILE MANAGER — Create, Read, Write, Erase, Delete files")
    print(" Working directory:", BASE_DIR)
    print("=" * 60)
    print("1. List files")
    print("2. Create new file")
    print("3. View file")
    print("4. Write/Overwrite file")
    print("5. Append to file")
    print("6. Erase (truncate) file")
    print("7. Delete file")
    print("8. Fun animation")
    print("9. Exit")


def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-9): ").strip()
        if choice == '1':
            list_files()
        elif choice == '2':
            create_file()
        elif choice == '3':
            view_file()
        elif choice == '4':
            write_file()
        elif choice == '5':
            append_file()
        elif choice == '6':
            erase_file()
        elif choice == '7':
            delete_file()
        elif choice == '8':
            run_animation()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select between 1 and 9.")
        input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt. Goodbye!")
