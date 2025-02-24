import time
import random
import pynput
import nltk
from nltk.corpus import brown, words

def load_word_frequencies():
    """Loads word frequencies from the Brown corpus, with handling for missing words."""
    try:
        nltk.data.find('corpora/brown')
        nltk.data.find('corpora/words')
    except LookupError:
        print("Downloading necessary NLTK corpora...")
        nltk.download('brown')
        nltk.download('words')

    word_list = words.words()  # For checking if a word exists
    word_freq = nltk.FreqDist(w.lower() for w in brown.words()) #from brown corpus

    # Create a dictionary with frequencies, handling words not in Brown
    freq_dict = {}
    for word in set(word_list): #use english word dictionary
        freq_dict[word] = word_freq.get(word, 1)  # Default freq of 1 for unknown words

    return freq_dict

def calculate_sentence_complexity(sentence):
    """Calculates a simple sentence complexity score based on length and punctuation."""
    words = sentence.split()
    num_words = len(words)
    num_commas = sentence.count(',')
    num_periods = sentence.count('.')
    num_colons_semicolons = sentence.count(':') + sentence.count(';')

    # A very basic complexity metric:
    complexity = num_words + 2 * num_commas + 3 * num_periods + 2.5 * num_colons_semicolons
    return complexity

def type_word(word, keyboard, word_freq, typo_prob, backspace_prob, capitalization_error_prob):
    """Types a single word, with potential for typos, capitalization errors, and speed variation."""

    original_word = word  # Store the original word

    # --- CAPITALIZATION ERRORS ---
    if random.random() < capitalization_error_prob:
        if 'a' <= word[0] <= 'z':  # If it should be capitalized
            correct_char = word[0].upper()
            incorrect_char = word[0].lower()  # Incorrect capitalization
        elif 'A' <= word[0] <= 'Z':  # If it should be lowercase
            correct_char = word[0].lower()
            incorrect_char = word[0].upper() # Incorrect capitalization
        else:
            correct_char = word[0]  #  handles edge cases like numbers/symbols.
            incorrect_char = word[0]

        # Only apply to the FIRST character
        if incorrect_char != correct_char: # Only if a change is needed
            keyboard.press(incorrect_char)  # Type the incorrect capitalization
            keyboard.release(incorrect_char)
            time.sleep(random.uniform(0.03, 0.1))  # Short delay
            keyboard.press(pynput.keyboard.Key.backspace)  # Backspace
            keyboard.release(pynput.keyboard.Key.backspace)
            time.sleep(random.uniform(0.05, 0.15))
            word = correct_char + word[1:] #rebuild word with correct capitalization



    for i, char in enumerate(word):
        # --- TYPO SIMULATION ---
        if random.random() < typo_prob:
            # 1. Wrong Key (adjacent key)
            if random.random() < 0.6:
                typo = get_adjacent_key(char)
                if typo:
                    keyboard.press(typo)
                    keyboard.release(typo)
                    time.sleep(random.uniform(0.03, 0.1))

                    # Immediate Correction
                    keyboard.press(pynput.keyboard.Key.backspace)
                    keyboard.release(pynput.keyboard.Key.backspace)
                    time.sleep(random.uniform(0.05, 0.15))
                    keyboard.press(char)  # Type the correct key
                    keyboard.release(char)
                    time.sleep(random.uniform(0.03, 0.1))


            # 2. Omitted Key
            elif random.random() < 0.2:
                # Immediate Correction (type the omitted key)
                keyboard.press(char)
                keyboard.release(char)
                time.sleep(random.uniform(0.03, 0.1))

            # 3. Repeated Key
            else:
                keyboard.press(char)
                keyboard.release(char)
                time.sleep(random.uniform(0.01, 0.05))
                keyboard.press(char)
                keyboard.release(char)
                #Immediate correction
                time.sleep(random.uniform(0.1, 0.4))
                keyboard.press(pynput.keyboard.Key.backspace)
                keyboard.release(pynput.keyboard.Key.backspace)
                time.sleep(random.uniform(0.05, 0.15))


        else: #if no typo
            keyboard.press(char)
            keyboard.release(char)

        # --- WORD-LEVEL TIMING ---
        word_frequency = word_freq.get(original_word.lower(), 1)  # Use original word for freq
        base_delay = 0.2
        frequency_factor = 1 / (word_frequency ** 0.2)
        char_delay = random.uniform(0.03, base_delay * frequency_factor)
        time.sleep(char_delay)



def type_sentence(sentence, keyboard, word_freq, typo_prob=0.03, backspace_prob=0.4,
                  burst_prob=0.5, burst_length_min=2, burst_length_max=5,
                  grammatical_error_prob=0.02, punctuation_error_prob = 0.02, capitalization_error_prob = 0.05):
    """Types a sentence with burst mode, errors, and complexity-based pacing."""

    words = sentence.split()
    sentence_complexity = calculate_sentence_complexity(sentence)
    # --- GRAMMATICAL ERRORS ---
    if random.random() < grammatical_error_prob:
        error_type = random.choice(["tense", "plural", "article"])

        if error_type == "tense" and len(words)> 3:
            #Simple past/present swap. Very basic, and could be improved.
            verb_index = random.randint(1, len(words) - 2)  # Avoid first/last word.
            words[verb_index] = words[verb_index] + "ed"  # Not robust!

        elif error_type == "plural" and len(words) > 2:
            noun_index = random.randint(1, len(words)-1)
            if words[noun_index].endswith('s'):
                words[noun_index] = words[noun_index][:-1] #remove the s
            else:
                words[noun_index] = words[noun_index] + "s" #add s
        elif error_type == "article" and len(words)>2:
            #remove article
            if words[0].lower() in ["a", "an", "the"]:
                words.pop(0)

    # --- PUNCTUATION ERRORS ---
    if random.random() < punctuation_error_prob:
        error_type = random.choice(["remove_comma", "add_comma", "wrong_end"])
        if error_type == "remove_comma":
            sentence = sentence.replace(",", "", 1) #remove 1 comma
        elif error_type == "add_comma" and len(words) > 3:
            add_index = random.randint(1, len(words)-2)
            words.insert(add_index, ",")  #add comma in random place.
        elif error_type == "wrong_end":
            if sentence.endswith("."):
                sentence = sentence[:-1] + random.choice(["!", "?", "..."]) #change ending punctuation

    # --- END GRAMMATICAL/PUNCTUATION ERRORS ---
    words = sentence.split() #redo split after punctuation edits and modifications
    i = 0
    while i < len(words):
        # --- BURST MODE ---
        if random.random() < burst_prob:
            burst_length = random.randint(burst_length_min, burst_length_max)
            burst_end = min(i + burst_length, len(words))
            for j in range(i, burst_end):
                type_word(words[j], keyboard, word_freq, typo_prob, backspace_prob, capitalization_error_prob)
                if j < burst_end - 1:  # This check *is* needed for burst mode
                    keyboard.press(pynput.keyboard.Key.space)
                    keyboard.release(pynput.keyboard.Key.space)
            i = burst_end  # Move index past the burst
            #short pause AFTER burst
            time.sleep(random.uniform(0.1,0.4))
        # --- END BURST ---

        else:  # Non-burst word
            type_word(words[i], keyboard, word_freq, typo_prob, backspace_prob, capitalization_error_prob)
            i += 1  # increment index

        # --- ALWAYS ADD SPACE (and pause) AFTER TYPING A WORD ---Outside burst loop
        if i < len(words):  # Don't add a space after the very last word
            # Adjust pause based on sentence complexity. More complex = longer pause.
            keyboard.press(pynput.keyboard.Key.space) #correctly adds spaces after all words.
            keyboard.release(pynput.keyboard.Key.space)
            pause_time = random.uniform(0.4, 1.0) * (1 + sentence_complexity / 50)  # Adjust scaling
            time.sleep(pause_time)



def get_adjacent_key(char):
    """Returns a random adjacent key on a QWERTY keyboard."""
    keyboard_layout = {
        'q': ['w', 'a'], 'w': ['q', 'e', 'a', 's'], 'e': ['w', 'r', 's', 'd'],
        'r': ['e', 't', 'd', 'f'], 't': ['r', 'y', 'f', 'g'], 'y': ['t', 'u', 'g', 'h'],
        'u': ['y', 'i', 'h', 'j'], 'i': ['u', 'o', 'j', 'k'], 'o': ['i', 'p', 'k', 'l'],
        'p': ['o', 'l'],
        'a': ['q', 'w', 's', 'z'], 's': ['w', 'e', 'a', 'd', 'z', 'x'],
        'd': ['e', 'r', 's', 'f', 'x', 'c'], 'f': ['r', 't', 'd', 'g', 'c', 'v'],
        'g': ['t', 'y', 'f', 'h', 'v', 'b'], 'h': ['y', 'u', 'g', 'j', 'b', 'n'],
        'j': ['u', 'i', 'h', 'k', 'n', 'm'], 'k': ['i', 'o', 'j', 'l', 'm'],
        'l': ['o', 'p', 'k'],
        'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'], 'c': ['x', 'd', 'f', 'v'],
        'v': ['c', 'f', 'g', 'b'], 'b': ['v', 'g', 'h', 'n'], 'n': ['b', 'h', 'j', 'm'],
        'm': ['n', 'j', 'k']

    }
    char = char.lower()
    if char in keyboard_layout:
        return random.choice(keyboard_layout[char])
    else:
        return None

def falsify_google_docs_history(text, word_freq, min_interval=1, max_interval=5,
                                 min_break=60, max_break=180,
                                 min_sentences_per_session=3, max_sentences_per_session=7,
                                 long_break_prob=0.1, long_break_min=900, long_break_max=2700,
                                 typo_prob=0.015, backspace_prob=0.2, burst_prob=0.5,
                                 burst_length_min=2, burst_length_max=5, grammatical_error_prob=0.01,
                                 punctuation_error_prob= 0.01, capitalization_error_prob = 0.025):
    """
    Simulates typing text, with all the enhanced features.
    """

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading punkt tokenizer...")
        nltk.download('punkt')
    # sentences = nltk.sent_tokenize(text) #DELTED
    paragraphs = text.split("\n") # Split into paragraphs by new line

    keyboard = pynput.keyboard.Controller()

    # Give the user time to switch
    print("You have 5 seconds to switch to the Google Docs document...")
    time.sleep(5)
    print("Starting to type...")


    # sentences_typed = 0 # DELETED
    for paragraph in paragraphs:
        sentences = nltk.sent_tokenize(paragraph) # Sentence tokenization within each paragraph
        sentences_typed = 0 #reset sentences_typed counter at the start of each paragraph
        while sentences_typed < len(sentences):
            # --- TYPING SESSION ---
            num_sentences_this_session = random.randint(min_sentences_per_session, max_sentences_per_session)
            sentences_to_type = min(num_sentences_this_session, len(sentences) - sentences_typed)

            for _ in range(sentences_to_type):
                type_sentence(sentences[sentences_typed], keyboard, word_freq, typo_prob, backspace_prob,
                              burst_prob, burst_length_min, burst_length_max, grammatical_error_prob,
                              punctuation_error_prob, capitalization_error_prob)
                sentences_typed += 1
                # --- INTER-SENTENCE INTERVAL ---
                if sentences_typed < len(sentences):  # Only pause if there are more sentences
                    interval = random.uniform(min_interval, max_interval)
                    time.sleep(interval)


            # --- BREAKS ---
            if sentences_typed < len(sentences):
                # --- LONG BREAK ---
                if random.random() < long_break_prob:
                    break_duration = random.uniform(long_break_min, long_break_max)
                    print(f"Taking a loooooooooong break for {break_duration:.2f} seconds...")
                    time.sleep(break_duration)

                # --- REGULAR BREAK ---
                else:
                    break_duration = random.uniform(min_break, max_break)
                    print(f"Taking a break for {break_duration:.2f} seconds...")
                    time.sleep(break_duration)
        #Paragraph handling
        if paragraph != "": #check if paragraph isn't empty.
            keyboard.press(pynput.keyboard.Key.enter) #press enter after each paragraph
            keyboard.release(pynput.keyboard.Key.enter)
            time.sleep(random.uniform(0.5,1.5)) #pause after enter


    print("Typing complete.")



def main():
    # Get text input
    text = ""
    print("Enter the text (type 'END' on a new line to finish):")
    while True:
        line = input()
        if line == "END":
            break
        text += line + "\n"

    # Default Parameters - Reduced Error Rates
    min_interval = 3
    max_interval = 17
    min_break = 60
    max_break = 180
    min_sentences = 3
    max_sentences = 7
    long_break_prob = 0.05
    long_break_min = 300
    long_break_max = 600
    typo_prob = 0.015  # Reduced by half
    backspace_prob = 0.2  # Reduced by half (backspace prob. is tied to typo prob.)
    burst_prob = 0.5
    burst_length_min = 2
    burst_length_max = 5
    grammatical_error_prob = 0.01  # Reduced by half
    punctuation_error_prob = 0.01  # Reduced by half
    capitalization_error_prob = 0.025  # Reduced by half

    # Ask if the user wants custom parameters
    customize = input("Do you want to customize the typing parameters? (y/n, default n): ").strip().lower()

    if customize == 'y':
        # Get user input for parameters (ONLY if they chose to customize)
        while True:
            try:
                min_interval = int(input(f"Enter minimum sentence interval in seconds (default {min_interval}): ") or min_interval)
                max_interval = int(input(f"Enter maximum sentence interval in seconds (default {max_interval}): ") or max_interval)
                if min_interval < 0 or max_interval < min_interval:
                    raise ValueError("Invalid interval valuues.")

                min_break = int(input(f"Enter minimum short break duration in seconds (default {min_break}): ") or min_break)
                max_break = int(input(f"Enter maximum short break duration in seconds (default {max_break}): ") or max_break)
                if min_break < 0 or max_break < min_break:
                    raise ValueError("Invalid break durration valuues.")

                min_sentences = int(input(f"Enter the minimum number of sentences per session (default {min_sentences}):") or min_sentences)
                max_sentences = int(input(f"Enter the maximum number of sentences per session(default {max_sentences}):") or max_sentences)
                if min_sentences <= 0 or max_sentences < min_sentences:
                    raise ValueError("Invalid sentences per session valuues.")

                long_break_prob = float(input(f"Enter the probability of a long break (0.0 to 1.0, default {long_break_prob}): ") or long_break_prob)
                if not 0.0 <= long_break_prob <= 1.0:
                    raise ValueError("Long break probability must be between 0.0 and 1.0.")

                long_break_min = int(input(f"Enter minimum long break duration in seconds (default {long_break_min}): ") or long_break_min)
                long_break_max = int(input(f"Enter maximum long break duration in seconds (default {long_break_max}): ") or long_break_max)
                if long_break_min < 0 or long_break_max < long_break_min:
                    raise ValueError("Invalid long break duration values.")

                typo_prob = float(input(f"Enter probability of a typo (0.0 to 1.0, default {typo_prob}): ") or typo_prob)
                if not 0.0 <= typo_prob <= 1.0:
                    raise ValueError("Typo probability must be between 0.0 and 1.0.")

                backspace_prob = float(input(f"Enter probability of correcting a typo with backspace (0.0 to 1.0, default {backspace_prob}): ") or backspace_prob)
                if not 0.0 <= backspace_prob <= 1.0:
                    raise ValueError("Backspace probability must be between 0.0 and 1.0.")

                burst_prob = float(input(f"Enter probability of a typing burst (0.0 to 1.0, default {burst_prob}): ") or burst_prob)
                if not 0.0 <= burst_prob <= 1.0:
                    raise ValueError("Burst probability must be between 0.0 and 1.0.")

                burst_length_min = int(input(f"Enter minimum burst length (words, default {burst_length_min}): ") or burst_length_min)
                burst_length_max = int(input(f"Enter maximum burst length (words, default {burst_length_max}): ") or burst_length_max)
                if burst_length_min <= 0 or burst_length_max < burst_length_min:
                    raise ValueError("Invalid burst length values.")

                grammatical_error_prob = float(input(f"Enter probability of a grammatical error (0.0 to 1.0, default {grammatical_error_prob}): ") or grammatical_error_prob)
                if not 0.0 <= grammatical_error_prob <= 1.0:
                    raise ValueError("grammatical error probability must be between 0.0 and 1.0")

                punctuation_error_prob = float(input(f"Enter probability of a punctuation error (0.0 to 1.0, default {punctuation_error_prob}): ") or punctuation_error_prob)
                if not 0.0 <= punctuation_error_prob <= 1.0:
                    raise ValueError("Punctuation error probability must be between 0.0 and 1.0.")

                capitalization_error_prob = float(input(f"Enter probability of a capitalization error (0.0 to 1.0, default {capitalization_error_prob}): ") or capitalization_error_prob)
                if not 0.0 <= capitalization_error_prob <= 1.0:
                    raise ValueError("Capitalization error probability must be between 0.0 and 1.0.")

                break  # Exit input loop after successful custom input

            except ValueError as e:
                print(f"Invalid input: {e}.  Please enter valid values.")

    # Load word frequencies (do this *after* getting user input, but *before* typing)
    word_freq = load_word_frequencies()

    # Call falsify_google_docs_history (OUTSIDE the if statement)
    falsify_google_docs_history(text, word_freq, min_interval, max_interval, min_break, max_break,
                                 min_sentences, max_sentences, long_break_prob, long_break_min,
                                 long_break_max, typo_prob, backspace_prob, burst_prob,
                                 burst_length_min, burst_length_max, grammatical_error_prob,
                                 punctuation_error_prob, capitalization_error_prob)

if __name__ == "__main__":
    main()