import os
import sys
import re
from pathlib import Path
import random
import time

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


def run_pacman():
    """A tiny, terminal-based Pacman-like mini-game with simple levels and improved ghost AI.
    Controls: W/A/S/D to move, q to quit. Player has a limited number of lives.
    """

    # Level presets
    levels = {
        1: {'rows': 10, 'cols': 20, 'ghosts': 1},
        2: {'rows': 12, 'cols': 26, 'ghosts': 2},
        3: {'rows': 14, 'cols': 32, 'ghosts': 3},
    }

    print("Choose Pacman level (1-easy, 2-medium, 3-hard). Default is 1.")
    try:
        lvl = int(input("Level: ").strip() or 1)
        if lvl not in levels:
            lvl = 1
    except Exception:
        lvl = 1

    cfg = levels[lvl]
    rows, cols = cfg['rows'], cfg['cols']
    grid = [['.' for _ in range(cols)] for _ in range(rows)]

    # place walls at borders and a simple inner ring for variety
    for r in range(rows):
        grid[r][0] = grid[r][cols-1] = '#'
    for c in range(cols):
        grid[0][c] = grid[rows-1][c] = '#'
    # inner ring
    for c in range(2, cols-2):
        grid[2][c] = grid[rows-3][c] = '#'

    player = [rows // 2, cols // 2]

    # place ghosts near corners
    ghosts = []
    corners = [(1,1), (1, cols-2), (rows-2, 1), (rows-2, cols-2)]
    for i in range(cfg['ghosts']):
        ghosts.append([corners[i][0], corners[i][1]])

    lives = 3
    score = 0

    def draw():
        os.system('cls' if os.name == 'nt' else 'clear')
        for r in range(rows):
            row = ''
            for c in range(cols):
                if [r,c] == player:
                    row += 'P'
                elif [r,c] in ghosts:
                    row += 'G'
                else:
                    row += grid[r][c]
            print(row)
        print(f"Score: {score}  Lives: {lives}")

    print("Welcome to enhanced Pacman! Eat dots (.) and avoid ghosts (G).")
    input("Press Enter to start...")

    max_turns = 2000
    turns = 0

    while turns < max_turns and lives > 0:
        draw()
        remaining = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] == '.')
        move = input("Move (W/A/S/D, q to quit): ").strip().lower()
        if move == 'q':
            print("Exiting Pacman.")
            break
        dr = dc = 0
        if move == 'w': dr = -1
        elif move == 's': dr = 1
        elif move == 'a': dc = -1
        elif move == 'd': dc = 1
        nr, nc = player[0] + dr, player[1] + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#':
            player[0], player[1] = nr, nc
            if grid[nr][nc] == '.':
                grid[nr][nc] = ' '
                score += 1

        # improved ghost AI: greedy toward player but avoid walls and sometimes move randomly
        for gi, g in enumerate(ghosts):
            gr, gc = g
            best_move = (gr, gc)
            best_dist = abs(gr - player[0]) + abs(gc - player[1])
            candidates = [(gr-1, gc), (gr+1, gc), (gr, gc-1), (gr, gc+1), (gr, gc)]
            random.shuffle(candidates)
            for cr, cc in candidates:
                if 0 <= cr < rows and 0 <= cc < cols and grid[cr][cc] != '#':
                    d = abs(cr - player[0]) + abs(cc - player[1])
                    # bias toward lower distance
                    if d < best_dist or (random.random() < 0.15 and d <= best_dist):
                        best_move = (cr, cc)
                        best_dist = d
            ghosts[gi][0], ghosts[gi][1] = best_move

        # collisions
        if player in ghosts:
            lives -= 1
            if lives > 0:
                print("A ghost got you! Lost a life. Respawning...")
                # reset player to center
                player = [rows // 2, cols // 2]
                input("Press Enter to continue...")
                turns += 1
                continue
            else:
                draw()
                print("Oh no — a ghost caught you and you have no lives left! Game over.")
                break

        if remaining == 0:
            draw()
            print("You cleared all dots — you win this level! Congrats!")
            break

        turns += 1
    else:
        if lives > 0:
            print("Time's up — thanks for playing!")


def run_mario():
    """A simple terminal 'runner' where Mario jumps over obstacles.
    Press 'j' then Enter to jump; Enter to tick without jumping. 'q' to quit.
    """
    width = 30
    mario_y = 0  # 0 = on ground, >0 = in air
    jump_ticks = 0
    obstacles = []
    score = 0
    print("Tiny Mario Runner! Press 'j' to jump at a step, 'q' to quit. Survive as long as you can.")
    input("Press Enter to start...")
    for tick in range(1, 1000):
        # spawn obstacle occasionally
        if random.random() < 0.2:
            obstacles.append(width - 1)

        # draw
        os.system('cls' if os.name == 'nt' else 'clear')
        line = [' ']*width
        for x in obstacles:
            if 0 <= x < width:
                line[x] = '|'  # obstacle
        # Mario position is always near left
        mpos = 2
        line[mpos] = 'M' if mario_y == 0 else 'm'
        print(''.join(line))
        print('-' * width)
        print(f"Score: {score}")
        cmd = input("Step (j=jump, q=quit, Enter=wait): ").strip().lower()
        if cmd == 'q':
            print("Quitting Mario. Thanks for playing!")
            break
        if cmd == 'j' and mario_y == 0:
            jump_ticks = 2
            mario_y = 1

        # update obstacles
        obstacles = [x-1 for x in obstacles if x-1 >= 0]

        # update jump state
        if jump_ticks > 0:
            jump_ticks -= 1
            if jump_ticks == 0:
                mario_y = 0

        # check collision
        if 2 in obstacles and mario_y == 0:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(''.join(line))
            print("Oh no — you hit an obstacle! Game over.")
            break

        score += 1
        time.sleep(0.05)


def run_pop_quiz():
    """Run an expanded pop quiz with subject, grade, and adaptive difficulty.

    Features:
    - Multiple subjects, grade levels and difficulty tiers (easy/medium/hard)
    - Adaptive difficulty: if the user does well the quiz offers harder questions next
    - Explanations after incorrect answers and tailored study tips
    """

    # Question bank organized as: banks[subject][grade][difficulty] -> list of (q, opts, ans, expl)
    banks = {
        'math': {
            'primary': {
                'easy': [
                    ("2 + 3 = ?", ['3','4','5','6'], 2, "Add the two numbers: 2+3=5."),
                    ("Which is even?", ['3','7','8','5'], 2, "Even numbers are divisible by 2."),
                ],
                'medium': [
                    ("What is 7 * 6?", ['42','36','48','40'], 0, "Multiply: 7 times 6 is 42."),
                    ("Solve 2x+3=7. x = ?", ['1','2','3','4'], 1, "2x = 4, so x = 2."),
                ],
                'hard': [
                    ("What is 12*12?", ['144','154','124','124'], 0, "12 times 12 is 144."),
                ],
            },
            'secondary': {
                'easy': [
                    ("What is 5*6?", ['11','30','56','20'], 1, "5 times 6 is 30."),
                ],
                'medium': [
                    ("Solve 3x - 4 = 11. x = ?", ['3','5','2','4'], 1, "3x = 15, x = 5."),
                ],
                'hard': [
                    ("What is the derivative of x^2?", ['2x','x','x^2','1'], 0, "d/dx x^2 = 2x."),
                ],
            }
        },
        'science': {
            'primary': {
                'easy': [
                    ("What do plants need to grow?", ['Sun','Sugar','Plastic','Iron'], 0, "Plants need sunlight, water and nutrients."),
                ],
                'medium': [
                    ("Which gas do plants produce during photosynthesis?", ['Oxygen','Carbon Dioxide','Nitrogen','Helium'], 0, "Plants release oxygen as a byproduct."),
                ],
                'hard': [
                    ("What is the primary pigment used in photosynthesis?", ['Chlorophyll','Carotene','Melanin','Hemoglobin'], 0, "Chlorophyll captures light energy."),
                ],
            },
            'secondary': {
                'easy': [
                    ("Water boils at what Celsius temperature?", ['90','100','110','120'], 1, "Water boils at 100°C at sea level."),
                ],
                'medium': [
                    ("What is the chemical symbol for water?", ['H2O','HO2','O2H','HHO'], 0, "Water has two hydrogens and one oxygen: H2O."),
                ],
                'hard': [
                    ("Which balances the pH in a buffer solution?", ['Acid/base pair','Salt','Sugar','Water'], 0, "Buffers use a conjugate acid/base pair."),
                ],
            }
        },
        'history': {
            'primary': {
                'easy': [
                    ("Who discovered America?", ['Columbus','Einstein','Newton','Gutenberg'], 0, "Christopher Columbus reached the Americas in 1492."),
                ],
                'medium': [
                    ("Which ancient civilization built pyramids in Egypt?", ['Romans','Egyptians','Greeks','Aztecs'], 1, "The Egyptians built the pyramids."),
                ],
                'hard': [
                    ("What year did the Berlin Wall fall?", ['1989','1991','1980','1979'], 0, "The Berlin Wall fell in 1989."),
                ],
            },
            'secondary': {
                'easy': [
                    ("In which year did WW2 end?", ['1945','1939','1918','1960'], 0, "World War II ended in 1945."),
                ],
                'medium': [
                    ("Who was the first President of the United States?", ['Lincoln','Washington','Jefferson','Adams'], 1, "George Washington was the first president."),
                ],
                'hard': [
                    ("Which treaty ended WW1?", ['Versailles','Paris','Vienna','Geneva'], 0, "The Treaty of Versailles ended WWI."),
                ],
            }
        }
    }

    print("Welcome to the Pop Quiz & Tutor!")
    subject = input("Choose a subject (math/science/history): ").strip().lower()
    if subject not in banks:
        print("Subject not available. Returning to menu.")
        return
    grade = input("Choose grade level (primary/secondary): ").strip().lower()
    if grade not in banks[subject]:
        print("Grade level not available for this subject. Returning to menu.")
        return

    # Ask how many questions
    try:
        qcount = int(input("How many questions would you like? (default 3): ").strip() or 3)
        qcount = max(1, min(10, qcount))
    except Exception:
        qcount = 3

    # Start at medium difficulty and adapt
    difficulty_order = ['easy', 'medium', 'hard']
    cur_idx = 1  # start at medium

    def pick_questions(difficulty, n):
        pool = banks[subject][grade].get(difficulty, [])[:]
        random.shuffle(pool)
        return pool[:n]

    total_correct = 0
    total_asked = 0

    for round_num in range(1, 3 + 1):  # allow up to 3 adaptive rounds (user can stop early)
        diff = difficulty_order[max(0, min(len(difficulty_order)-1, cur_idx))]
        questions = pick_questions(diff, qcount)
        if not questions:
            print(f"No questions available at {diff} difficulty — trying another level.")
            # try to find any available
            found = False
            for d in difficulty_order:
                if banks[subject][grade].get(d):
                    questions = pick_questions(d, qcount)
                    found = True
                    break
            if not found:
                print("No questions available for this subject/grade. Returning to menu.")
                return

        correct = 0
        for i, (q, opts, ans, expl) in enumerate(questions, 1):
            print(f"\n[Difficulty: {diff}] Question {i}: {q}")
            for idx, opt in enumerate(opts):
                print(f"  {idx+1}. {opt}")
            try:
                pick = int(input("Your answer (1-4): ").strip()) - 1
            except Exception:
                pick = -1
            if pick == ans:
                print("Correct! ✅")
                correct += 1
            else:
                print(f"Incorrect. Explanation: {expl}")

        # Round results
        round_pct = int(100 * correct / len(questions))
        print(f"\nRound score: {correct}/{len(questions)} ({round_pct}%) at {diff} difficulty.")
        total_correct += correct
        total_asked += len(questions)

        # Adaptive adjustment
        if round_pct >= 80 and cur_idx < len(difficulty_order)-1:
            print("Great — you performed well. I'll try a harder level next round.")
            cur_idx += 1
        elif round_pct < 50 and cur_idx > 0:
            print("Let's try an easier level to build confidence and fundamentals.")
            cur_idx -= 1
        else:
            print("Maintaining current difficulty for the next round.")

        # Ask if user wants another round (unless we've already done multiple)
        if round_num < 3:
            again = input("Do you want another round to continue learning? (y/n): ").strip().lower()
            if again != 'y':
                break

    # Final results and tailored teaching
    score_pct = int(100 * total_correct / total_asked) if total_asked else 0
    print(f"\nFinal score: {total_correct}/{total_asked} ({score_pct}%).")

    if score_pct >= 80:
        print("Excellent! You're ready for more challenging topics in this subject.")
        print("Tip: Try higher difficulty questions or explore applied problems.")
    elif score_pct >= 50:
        print("Good job — you have the basics. Review the explanations above and try again.")
    else:
        print("No problem — let's strengthen the fundamentals. A few suggestions:")
        if subject == 'math':
            print(" - Practice arithmetic and show each step when solving problems.")
            print(" - Use online exercises for repeated practice on basic operations.")
        elif subject == 'science':
            print(" - Review simple definitions and watch short demo videos for concepts.")
        elif subject == 'history':
            print(" - Create a timeline of main events and read short summaries to reinforce facts.")

    print("Thanks for using the Pop Quiz & Tutor — repeat quizzes anytime to improve!")


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
    print("10. Play Pacman (tiny)")
    print("11. Play Mario Runner (tiny)")
    print("12. Pop Quiz & Tutor")
    print("9. Exit")


def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-12): ").strip()
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
        elif choice == '10':
            run_pacman()
        elif choice == '11':
            run_mario()
        elif choice == '12':
            run_pop_quiz()
        elif choice == '9':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option between 1 and 12.")
        input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt. Goodbye!")
