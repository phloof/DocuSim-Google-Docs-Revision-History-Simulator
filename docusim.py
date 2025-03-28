import time
import random
import pynput
import nltk
from nltk.corpus import brown, words
import traceback # For better error reporting
import sys # To use exit()
import datetime # For time formatting

# --- NLTK Data Check and Download ---
# (ensure_nltk_data function remains the same - included for completeness)
def ensure_nltk_data(max_retries=3):
    """
    Downloads necessary NLTK data if not found. Checks all required data,
    attempts to download missing items, and retries the check up to max_retries.
    Exits the script if verification fails after all retries.
    """
    required_data = [
        ('corpora', 'brown'),
        ('corpora', 'words'),
        ('tokenizers', 'punkt')
    ]
    retries = 0

    while retries < max_retries:
        all_found_this_pass = True
        missing_items = []

        print(f"\n--- NLTK Data Check (Attempt {retries + 1}/{max_retries}) ---")
        for dtype, dname in required_data:
            try:
                if dtype == 'corpora':
                    check_file = 'cats.txt' if dname == 'brown' else 'README'
                    nltk.data.find(f'{dtype}/{dname}/{check_file}')
                elif dtype == 'tokenizers':
                    nltk.data.find(f'{dtype}/{dname}')
                else:
                     nltk.data.find(f'{dtype}/{dname}')
                print(f"  [OK] Found: {dname}")
            except LookupError:
                print(f"  [MISSING] Data not found: {dname}")
                all_found_this_pass = False
                if dname not in missing_items: missing_items.append(dname)
            except Exception as find_err:
                 print(f"\nERROR checking NLTK data '{dname}': {find_err}")
                 sys.exit(1)

        if all_found_this_pass:
            print("--- All required NLTK data verified. ---")
            return True

        if missing_items:
            print(f"\nAttempting to download missing items: {', '.join(missing_items)}")
            download_success_all = True
            for dname in missing_items:
                print(f"Downloading '{dname}'...")
                try:
                    success = nltk.download(dname, quiet=False)
                    if not success: raise Exception(f"NLTK download function indicated failure for '{dname}'.")
                    print(f"Completed download attempt for '{dname}'.")
                    time.sleep(0.5)
                except Exception as download_err:
                    print(f"\nERROR: Failed to download NLTK data '{dname}': {download_err}")
                    print(f"Consider manual download: python -m nltk.downloader {dname}")
                    download_success_all = False

            if not download_success_all: print("\nOne or more downloads failed during this attempt.")

        retries += 1
        if retries < max_retries:
            print(f"\nDownloads attempted. Retrying NLTK data verification...")
            time.sleep(1)

    print(f"\nFATAL ERROR: Failed to verify required NLTK data after {max_retries} attempts.")
    print("Required data:", [item[1] for item in required_data])
    print("Please check your internet connection, permissions, and try manual download:")
    for _, dname in required_data: print(f"  python -m nltk.downloader {dname}")
    sys.exit(1)


# --- Utility Functions ---

def format_duration(seconds):
    """Formats a duration in seconds into a human-readable string (e.g., 1h 15m 30s)."""
    if seconds < 0: return "0s"
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    if seconds > 0 or not parts: parts.append(f"{seconds}s")
    return " ".join(parts) if parts else "0s"


def load_word_frequencies():
    """Loads word frequencies from NLTK corpora."""
    try:
        word_list_set = set(w.lower() for w in words.words())
        brown_freq = nltk.FreqDist(w.lower() for w in brown.words())
        freq_dict = {}
        for word, freq in brown_freq.items(): freq_dict[word] = freq
        for word in word_list_set:
            if word not in freq_dict: freq_dict[word] = 1
        if not freq_dict: raise ValueError("Frequency dictionary empty after loading.")
        return freq_dict
    except Exception as e:
        print(f"\nERROR loading word frequencies: {e}")
        return {"the": 1000, "a": 500, "is": 300} # Minimal fallback


def calculate_sentence_complexity(sentence):
    """Calculates a simple sentence complexity score."""
    words = sentence.split()
    num_words = len(words)
    num_commas = sentence.count(',')
    num_periods = sentence.count('.')
    num_colons_semicolons = sentence.count(':') + sentence.count(';')
    complexity = num_words + 2 * num_commas + 1 * num_periods + 1.5 * num_colons_semicolons
    normalized_complexity = min(max(complexity, 5), 100)
    return normalized_complexity

def get_adjacent_key(char):
    """Returns a random adjacent key on a QWERTY keyboard."""
    # QWERTY Layout (US standard)
    keyboard_layout = {
        'q': ['w', 'a', 's', '1', '2'], 'w': ['q', 'e', 'a', 's', 'd', '2', '3'],
        'e': ['w', 'r', 's', 'd', 'f', '3', '4'], 'r': ['e', 't', 'd', 'f', 'g', '4', '5'],
        't': ['r', 'y', 'f', 'g', 'h', '5', '6'], 'y': ['t', 'u', 'g', 'h', 'j', '6', '7'],
        'u': ['y', 'i', 'h', 'j', 'k', '7', '8'], 'i': ['u', 'o', 'j', 'k', 'l', '8', '9'],
        'o': ['i', 'p', 'k', 'l', '9', '0'], 'p': ['o', 'l', '0', '['],
        'a': ['q', 'w', 's', 'z', 'x'], 's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
        'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'], 'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
        'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'], 'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
        'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm'], 'k': ['u', 'i', 'o', 'j', 'l', 'm', ','],
        'l': ['i', 'o', 'p', 'k', '.', ';'],
        'z': ['a', 's', 'x'], 'x': ['a', 's', 'd', 'z', 'c'], 'c': ['s', 'd', 'f', 'x', 'v'],
        'v': ['d', 'f', 'g', 'c', 'b'], 'b': ['f', 'g', 'h', 'v', 'n'], 'n': ['g', 'h', 'j', 'b', 'm'],
        'm': ['h', 'j', 'k', 'n', ','],
        '1': ['2', 'q'], '2': ['1', '3', 'q', 'w'], '3': ['2', '4', 'w', 'e'], '4': ['3', '5', 'e', 'r'],
        '5': ['4', '6', 'r', 't'], '6': ['5', '7', 't', 'y'], '7': ['6', '8', 'y', 'u'],
        '8': ['7', '9', 'u', 'i'], '9': ['8', '0', 'i', 'o'], '0': ['9', 'p', '-'],
        '-': ['0', '=', '[', 'p'], '=': ['-', '['], '[': ['p', ']', '=', '-'], ']': ['[', '\\'], '\\': [']'],
        ',': ['k', 'l', 'm', '.'], '.': [',', 'l', '/', ';'], '/': ['.', ';'], ';': ['l', '.', '/', '\''], '\'': [';', '[', ']']
    }
    char_lower = char.lower()
    if char_lower in keyboard_layout: return random.choice(keyboard_layout[char_lower])
    return None

# --- Core Typing Simulation Functions ---

def type_word(word, keyboard, word_freq, typo_prob, capitalization_error_prob, typing_speed_factor):
    """Types a word char by char with delays, simulating and IMMEDIATELY correcting typos/caps errors."""
    original_word = word
    if not word: return

    first_char_intended = word[0]; corrected_first_char_after_error = False

    # Capitalization Error Simulation
    if random.random() < capitalization_error_prob:
        incorrect = None
        if 'A' <= first_char_intended <= 'Z': incorrect = first_char_intended.lower()
        if incorrect and incorrect != first_char_intended:
            try:
                keyboard.press(incorrect); keyboard.release(incorrect); time.sleep(random.uniform(0.04, 0.12) * typing_speed_factor)
                keyboard.press(pynput.keyboard.Key.backspace); keyboard.release(pynput.keyboard.Key.backspace); time.sleep(random.uniform(0.05, 0.15) * typing_speed_factor)
                corrected_first_char_after_error = True
            except Exception as e: print(f"\nERROR simulating caps error: {e}")

    # Character Typing Loop
    for i, target_char in enumerate(word):
        action_taken = False; typo_corrected = False
        if i == 0 and corrected_first_char_after_error:
            try: keyboard.press(target_char); keyboard.release(target_char); action_taken = True
            except Exception as e: print(f"\nERROR typing corrected first char '{target_char}': {e}")
        else:
            make_typo = random.random() < typo_prob
            if make_typo:
                typo_type = random.random()
                try:
                    if typo_type < 0.6: # Wrong Key
                        typo_char = get_adjacent_key(target_char)
                        if typo_char:
                            keyboard.press(typo_char); keyboard.release(typo_char); time.sleep(random.uniform(0.03, 0.1)*typing_speed_factor)
                            keyboard.press(pynput.keyboard.Key.backspace); keyboard.release(pynput.keyboard.Key.backspace); time.sleep(random.uniform(0.05, 0.15)*typing_speed_factor)
                            keyboard.press(target_char); keyboard.release(target_char); typo_corrected = True; action_taken = True
                    elif typo_type < 0.8: # Omitted Key
                         time.sleep(random.uniform(0.06, 0.25)*typing_speed_factor)
                         keyboard.press(target_char); keyboard.release(target_char); typo_corrected = True; action_taken = True
                    else: # Repeated Key
                         keyboard.press(target_char); keyboard.release(target_char); time.sleep(random.uniform(0.01, 0.05)*typing_speed_factor)
                         keyboard.press(target_char); keyboard.release(target_char); time.sleep(random.uniform(0.05, 0.15)*typing_speed_factor)
                         keyboard.press(pynput.keyboard.Key.backspace); keyboard.release(pynput.keyboard.Key.backspace); typo_corrected = True; action_taken = True
                except Exception as e:
                    print(f"\nERROR during typo sim for '{target_char}': {e}")
                    if not action_taken:
                        try: keyboard.press(target_char); keyboard.release(target_char); action_taken = True
                        except: pass # Best effort fallback
            if not action_taken: # Type Correctly if no typo happened/failed
                 try: keyboard.press(target_char); keyboard.release(target_char); action_taken = True
                 except Exception as e: print(f"\nERROR typing char '{target_char}': {e}")

        # Character Timing
        word_frequency = word_freq.get(original_word.lower(), 1)
        base_delay = 0.15; frequency_factor = max(0.5, min(2.0, 1 / (word_frequency ** 0.1)))
        correction_delay = 1.5 if typo_corrected or corrected_first_char_after_error else 1.0
        char_delay = random.uniform(0.02, base_delay * frequency_factor) * typing_speed_factor * correction_delay
        time.sleep(max(0.005, char_delay))


def type_sentence(sentence, keyboard, word_freq, burst_prob, burst_length_min, burst_length_max,
                  typo_prob, capitalization_error_prob, typing_speed_factor):
    """Types a sentence using word typer, handling bursts and spacing between words."""
    words_to_type = sentence.split();
    if not words_to_type: return
    sentence_complexity = calculate_sentence_complexity(sentence)
    i = 0
    while i < len(words_to_type):
        if i > 0: # Inter-Word Space (before word 1, 2, ...)
            try: keyboard.press(pynput.keyboard.Key.space); keyboard.release(pynput.keyboard.Key.space)
            except Exception as e: print(f"\nERROR typing space: {e}")
            pause = random.uniform(0.2, 0.7) * (1 + sentence_complexity / 80.0) * typing_speed_factor
            time.sleep(max(0.01, pause))
        current_word_index = i; is_burst = False
        if random.random() < burst_prob and (len(words_to_type) - i) >= burst_length_min: # Burst?
            burst_len = random.randint(burst_length_min, burst_length_max); burst_end = min(i + burst_len, len(words_to_type))
            if burst_end > i + 1: is_burst = True
            for j in range(i, burst_end):
                if j > i: # Space within burst
                     try: keyboard.press(pynput.keyboard.Key.space); keyboard.release(pynput.keyboard.Key.space)
                     except Exception as e: print(f"\nERROR typing burst space: {e}")
                     time.sleep(random.uniform(0.015, 0.06) * typing_speed_factor)
                type_word(words_to_type[j], keyboard, word_freq, typo_prob, capitalization_error_prob, typing_speed_factor)
            i = burst_end
        if not is_burst: # Single Word
             if current_word_index < len(words_to_type):
                 type_word(words_to_type[current_word_index], keyboard, word_freq, typo_prob, capitalization_error_prob, typing_speed_factor)
                 i += 1
             else: break


def falsify_google_docs_history(text, word_freq, min_interval=1, max_interval=5, min_break=60, max_break=180,
                                min_sentences_per_session=3, max_sentences_per_session=7, long_break_prob=0.1,
                                long_break_min=900, long_break_max=2700, burst_prob=0.5, burst_length_min=2,
                                burst_length_max=5, typo_prob=0.015, capitalization_error_prob=0.025,
                                typing_speed_factor=1.0):
    """Main simulation loop: paragraphs, sentences, sessions, breaks, estimates."""
    try:
        keyboard = pynput.keyboard.Controller()
    except Exception as e: print(f"\nFATAL ERROR: Keyboard controller init failed: {e}"); sys.exit(1)

    paragraphs = text.split("\n")

    # --- Calculate Estimate ---
    estimated_duration_str = "Unknown"
    formatted_completion_time = "Unknown"
    try:
        total_chars = len(text)
        stripped_paragraphs = [p for p in paragraphs if p.strip()]
        num_paragraphs = len(stripped_paragraphs)
        total_sentences = sum(len(nltk.sent_tokenize(p)) for p in stripped_paragraphs) if stripped_paragraphs else 0

        if total_chars > 0 and total_sentences > 0:
            base_wpm = 50; chars_per_word = 5.5 # Estimation constants
            estimated_typing_time_only = max(0, total_chars * (60 / (base_wpm * chars_per_word)) / typing_speed_factor)
            avg_sentences_per_session = (min_sentences_per_session + max_sentences_per_session) / 2
            num_sessions = total_sentences / avg_sentences_per_session if avg_sentences_per_session > 0 else 0
            num_breaks = max(0, num_sessions - num_paragraphs)
            num_long_breaks = num_breaks * long_break_prob
            num_short_breaks = num_breaks * (1 - long_break_prob)
            estimated_long_break_time = max(0, num_long_breaks * ((long_break_min + long_break_max) / 2) * typing_speed_factor)
            estimated_short_break_time = max(0, num_short_breaks * ((min_break + max_break) / 2) * typing_speed_factor)
            estimated_inter_sentence_time = max(0, total_sentences - num_paragraphs) * ((min_interval + max_interval) / 2) * typing_speed_factor
            total_estimated_duration = (estimated_typing_time_only + estimated_long_break_time +
                                        estimated_short_break_time + estimated_inter_sentence_time)
            estimated_duration_str = format_duration(total_estimated_duration)
            start_timestamp = time.time()
            estimated_completion_timestamp = start_timestamp + total_estimated_duration
            completion_dt = datetime.datetime.fromtimestamp(estimated_completion_timestamp)
            formatted_completion_time = completion_dt.strftime("%Y-%m-%d %H:%M:%S")
        elif total_chars > 0:
            print("Warning: Text found but could not tokenize into sentences for full estimate.")
            base_wpm = 50; chars_per_word = 5.5
            total_estimated_duration = max(0, total_chars * (60 / (base_wpm * chars_per_word)) / typing_speed_factor)
            estimated_duration_str = format_duration(total_estimated_duration) + " (typing only)"
            start_timestamp = time.time()
            estimated_completion_timestamp = start_timestamp + total_estimated_duration
            completion_dt = datetime.datetime.fromtimestamp(estimated_completion_timestamp)
            formatted_completion_time = completion_dt.strftime("%Y-%m-%d %H:%M:%S") + " (typing only)"
        else:
             estimated_duration_str = "0s"
             formatted_completion_time = "N/A (No text)"
    except Exception as est_err:
        print(f"\nWarning: Could not calculate time estimate: {est_err}")
    # --- End Estimate ---

    print(f"\nCurrent Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Estimated Total Duration: ~{estimated_duration_str}")
    print(f"Estimated Completion Time: ~{formatted_completion_time}")
    print("\nYou have 5 seconds to switch to the target window...")
    time.sleep(5)
    actual_start_time = time.time()
    print("Starting typing simulation...")

    # --- Main Typing Loop ---
    for para_index, paragraph in enumerate(paragraphs):
        stripped_paragraph = paragraph.strip()
        if not stripped_paragraph: # Handle blank lines
             if para_index < len(paragraphs) - 1:
                next_para_is_empty = (para_index + 1 < len(paragraphs) and not paragraphs[para_index+1].strip())
                if not next_para_is_empty:
                    try: keyboard.press(pynput.keyboard.Key.enter); keyboard.release(pynput.keyboard.Key.enter); time.sleep(random.uniform(0.4, 1.2)*typing_speed_factor)
                    except Exception as e: print(f"\nERROR typing Enter for blank line: {e}")
             continue

        try: sentences = nltk.sent_tokenize(stripped_paragraph)
        except Exception as e: print(f"\nERROR tokenizing para: '{stripped_paragraph[:50]}...'. {e}. Skipping."); continue
        if not sentences: continue

        num_sentences_in_para = len(sentences); sentences_typed_in_para = 0
        while sentences_typed_in_para < num_sentences_in_para: # Session loop
            num_sentences_this = random.randint(min_sentences_per_session, max_sentences_per_session)
            session_end = min(sentences_typed_in_para + num_sentences_this, num_sentences_in_para)
            for k in range(sentences_typed_in_para, session_end):
                # Type the current sentence
                type_sentence(sentences[k], keyboard, word_freq, burst_prob, burst_length_min, burst_length_max,
                              typo_prob, capitalization_error_prob, typing_speed_factor)
                sentences_typed_in_para += 1

                # === INTER-SENTENCE SPACING FIX ===
                # Add space(s) and pause if not the very last sentence in the paragraph
                if sentences_typed_in_para < num_sentences_in_para:
                    try:
                        # Add TWO spaces after sentence-ending punctuation (common convention)
                        keyboard.press(pynput.keyboard.Key.space); 

                    except Exception as e:
                        print(f"\nERROR typing inter-sentence space: {e}")

                    # Now, apply the longer pause *after* the spaces
                    interval = random.uniform(min_interval, max_interval) * typing_speed_factor
                    time.sleep(max(0.01, interval))
                # === END FIX ===

            # --- Break logic ---
            if session_end < num_sentences_in_para: # Break between sessions
                duration = 0; break_type = "short"
                if random.random() < long_break_prob:
                    duration = random.uniform(long_break_min, long_break_max) * typing_speed_factor; break_type = "long"
                else: duration = random.uniform(min_break, max_break) * typing_speed_factor
                print(f"\nTaking a {break_type} break for {format_duration(duration)}...")
                time.sleep(max(0.1, duration)); print("Resuming typing...")
            # --- End Break Logic ---

        # --- End of Paragraph Enter ---
        if para_index < len(paragraphs) - 1:
            try: keyboard.press(pynput.keyboard.Key.enter); keyboard.release(pynput.keyboard.Key.enter); time.sleep(random.uniform(0.5, 1.5)*typing_speed_factor)
            except Exception as e: print(f"\nERROR typing paragraph Enter: {e}")
        # --- End EOP ---
    # --- End Main Loop ---

    actual_end_time = time.time()
    actual_total_duration = actual_end_time - actual_start_time
    print(f"\nTyping complete.")
    print(f"Actual Total Duration: {format_duration(actual_total_duration)}")
    if formatted_completion_time != "Unknown" and formatted_completion_time != "N/A (No text)":
         print(f"(Original Estimated Completion Time was: ~{formatted_completion_time})")


# --- Main Execution Logic ---

def main():
    # --- Ensure NLTK Data ---
    ensure_nltk_data()

    # --- Get Text Input ---
    text = ""
    print("\nEnter/Paste the text. Press Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) when done.")
    print("Alternatively, type 'END' on a new line to finish:")
    lines = []
    while True:
        try: line = input(); lines.append(line)
        except EOFError: print("\nEOF detected, finishing input."); break
        except KeyboardInterrupt: print("\nInput interrupted. Exiting."); return
        if line.strip().upper() == "END": lines.pop(); break
    text = "\n".join(lines)
    if not text.strip(): print("No text provided. Exiting."); return

    # --- Parameters ---
    min_interval=1.5; max_interval=6; min_break=30; max_break=75; min_sentences=2; max_sentences=5
    long_break_prob=0.07; long_break_min=90; long_break_max=300; burst_prob=0.4; burst_length_min=2
    burst_length_max=4; typo_prob=0.02; capitalization_error_prob=0.03; typing_speed_factor=2

    customize = input("Customize parameters (timing, errors, etc.)? (y/n, default n): ").strip().lower()
    if customize == 'y':
         print("--- Customizing Parameters ---")
         while True: # Input loop for customization
            try:
                min_interval = float(input(f"Min sentence interval sec (def {min_interval}): ") or min_interval)
                max_interval = float(input(f"Max sentence interval sec (def {max_interval}): ") or max_interval)
                min_break = int(input(f"Min short break sec (def {min_break}): ") or min_break)
                max_break = int(input(f"Max short break sec (def {max_break}): ") or max_break)
                min_sentences = int(input(f"Min sentences/session (def {min_sentences}):") or min_sentences)
                max_sentences = int(input(f"Max sentences/session (def {max_sentences}):") or max_sentences)
                long_break_prob = float(input(f"Long break probability (0-1, def {long_break_prob}): ") or long_break_prob)
                long_break_min = int(input(f"Min long break sec (def {long_break_min}): ") or long_break_min)
                long_break_max = int(input(f"Max long break sec (def {long_break_max}): ") or long_break_max)
                burst_prob = float(input(f"Burst probability (0-1, def {burst_prob}): ") or burst_prob)
                burst_length_min = int(input(f"Min burst length words (def {burst_length_min}): ") or burst_length_min)
                burst_length_max = int(input(f"Max burst length words (def {burst_length_max}): ") or burst_length_max)
                typo_prob = float(input(f"Typo probability per char (0-1, def {typo_prob}): ") or typo_prob)
                capitalization_error_prob = float(input(f"Capitalization error prob (0-1, def {capitalization_error_prob}): ") or capitalization_error_prob)
                typing_speed_factor = float(input(f"Typing speed factor (>0, 1=normal, def {typing_speed_factor}): ") or typing_speed_factor)
                # Validations
                if not (0.0 <= long_break_prob <= 1.0 and 0.0 <= burst_prob <= 1.0 and \
                        0.0 <= typo_prob <= 1.0 and 0.0 <= capitalization_error_prob <= 1.0): raise ValueError("Probs must be 0-1")
                if min_interval < 0 or max_interval < min_interval: raise ValueError("Invalid interval")
                if min_break < 0 or max_break < min_break: raise ValueError("Invalid break duration")
                if min_sentences <= 0 or max_sentences < min_sentences: raise ValueError("Invalid sentences/session")
                if long_break_min < 0 or long_break_max < long_break_min: raise ValueError("Invalid long break duration")
                if burst_length_min < 1 or burst_length_max < burst_length_min: raise ValueError("Invalid burst length (min 1)")
                if typing_speed_factor <= 0: raise ValueError("Typing speed factor must be positive")
                break # Exit input loop if all valid
            except ValueError as e: print(f"Invalid input: {e}. Please enter valid values."); continue
            except Exception as e: print(f"An error occurred during input: {e}"); continue

    # --- Load Frequencies ---
    print("\nLoading word frequencies...")
    word_freq = load_word_frequencies()
    if not word_freq or len(word_freq)<10: print("Word freq loading failed. Exiting."); sys.exit(1)
    print("Frequencies loaded.")

    # --- Run Simulation ---
    try:
        falsify_google_docs_history(text, word_freq, min_interval, max_interval, min_break, max_break,
                                    min_sentences, max_sentences, long_break_prob, long_break_min,
                                    long_break_max, burst_prob, burst_length_min, burst_length_max,
                                    typo_prob, capitalization_error_prob, typing_speed_factor)
    except KeyboardInterrupt: print("\nTyping interrupted by user.")
    except Exception as e: print(f"\nUnexpected error during simulation: {e}"); traceback.print_exc()

if __name__ == "__main__":
    main()
