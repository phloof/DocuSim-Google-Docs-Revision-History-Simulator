# DocuSim: Google Docs/OneNote Version History Simulator

## Overview

**DocuSim** is a Python program designed to demonstrate the potential unreliability of Google Docs/OneNote (etc) revision history as a sole source of truth for determining the creation process of a document.  It simulates human-like typing behavior, complete with realistic pauses, errors, corrections, and variations in typing speed, to generate a plausible revision history within a Google Docs document.  This is *not* intended for malicious use, but rather for educational purposes and to highlight the limitations of relying solely on revision history for forensic analysis or determining authorship attribution.

## Features

DocuSim incorporates several features to mimic human typing patterns:

*   **Realistic Pauses and Timing:**
    *   **Inter-Sentence Intervals:**  Pauses of varying lengths occur between sentences, simulating natural thought processes. The duration of these pauses is influenced by sentence complexity.
    *   **Inter-Word Pauses:** Pauses of varying lengths occur between words, making the output appear less robotic.
    *   **Short Breaks:**  The program simulates taking short breaks (e.g., for thinking or distractions) between typing sessions.
    *   **Long Breaks:**  The program can also simulate longer breaks, mimicking interruptions or periods of inactivity.
    *  **Word Frequency Based Delays:** Pauses between characters are adjusted based upon the frequency of words, rare words will have a greater delay than more common words.

*   **Typing Errors and Corrections:**
    *   **Typos:**  The program introduces common typing errors, such as pressing adjacent keys, omitting keys, or repeating keys.
    *   **Backspace Corrections:**  Typos are often (but not always) immediately corrected using the backspace key, further enhancing realism.
    *   **Capitalization Errors:** The simulation introduces capitalization errors at the beginning of words, which are then backspaced and corrected.

*   **Burst Typing:**  Humans often type in bursts of faster activity followed by slower periods.  DocuSim simulates this "burst mode," typing several words quickly before pausing.

*   **Grammatical and Punctuation Errors:**
    *   **Grammatical Errors:**  The program can introduce simple grammatical errors (e.g., tense inconsistencies, incorrect pluralization, article omission), which are *not* corrected.
    *   **Punctuation Errors:**  Commas may be added or removed, and the ending punctuation of a sentence may be changed. These errors, like grammatical errors, remain in the final text.

*   **Paragraph Handling:**
    *   The program types the provided input text, paragraph by paragraph.
    *   It presses the "Enter" key after typing each paragraph, creating natural paragraph breaks in the document.

*   **Customizable Parameters:**  Almost all aspects of the simulation can be adjusted, allowing you to fine-tune the typing behavior to match different scenarios. (See "Parameters" section below).

## How It Works

DocuSim uses the `pynput` library to simulate keyboard input. It interacts *directly* with your active window (which should be a Google Docs document).  The program uses NLTK (Natural Language Toolkit) for:

1.  **Sentence Tokenization:** Breaking the input text into individual sentences.
2.  **Word Frequency Analysis:**  Using the Brown corpus to determine the relative frequency of words, influencing typing speed (more frequent words are typed faster).

The core logic works as follows:

1.  **Input:** The user provides the text to be "typed."
2.  **Parameter Configuration:** The user can customize various parameters (or use the defaults).
3.  **Initialization:** The program loads word frequencies and prepares for typing.
4.  **Typing Loop:** The program iterates through the text, paragraph by paragraph, and sentence by sentence.
    *   **Burst Mode:**  Randomly enters and exits burst mode, typing multiple words quickly.
    *   **Type Word:**  Simulates typing each word, including potential typos, capitalization errors, and delays.
    *   **Pauses:**  Inserts pauses between words and sentences, with lengths influenced by complexity and randomness.
    *   **Breaks:**  Simulates taking short and long breaks between typing sessions.
5.  **Completion:**  After typing the entire text, the program indicates completion.

## Parameters

DocuSim offers extensive parameter customization:

| Parameter                    | Description                                                                          | Default Value | Data Type | Range/Options        | Notes                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------ | ------------- | --------- | -------------------- | ---------------------------------------------------------------------------------------------------- |
| `min_interval`               | Minimum time (seconds) between sentences.                                          | 10            | int       | >= 0                 | Influenced by sentence complexity.                                                                   |
| `max_interval`               | Maximum time (seconds) between sentences.                                          | 20            | int       | >= `min_interval`     | Influenced by sentence complexity.                                                                   |
| `min_break`                  | Minimum duration (seconds) of a short break.                                       | 60            | int       | >= 0                 |                                                                                                      |
| `max_break`                  | Maximum duration (seconds) of a short break.                                       | 180           | int       | >= `min_break`       |                                                                                                      |
| `min_sentences_per_session` | Minimum number of sentences typed in a single session before a potential break.    | 3             | int       | >= 1                 |                                                                                                      |
| `max_sentences_per_session` | Maximum number of sentences typed in a single session before a potential break.    | 7             | int       | >= `min_sentences`   |                                                                                                      |
| `long_break_prob`           | Probability (0.0 to 1.0) of taking a long break instead of a short break.        | 0.05          | float     | 0.0 to 1.0           |                                                                                                      |
| `long_break_min`            | Minimum duration (seconds) of a long break.                                        | 300           | int       | >= 0                 |                                                                                                      |
| `long_break_max`            | Maximum duration (seconds) of a long break.                                        | 600           | int       | >= `long_break_min`  |                                                                                                      |
| `typo_prob`                 | Probability (0.0 to 1.0) of making a typo while typing a character.                | 0.015         | float     | 0.0 to 1.0           |                                                                                                      |
| `backspace_prob`            | Probability (0.0 to 1.0) of correcting a typo with backspace.                       | 0.2           | float     | 0.0 to 1.0           |                                                                                                      |
| `burst_prob`                | Probability (0.0 to 1.0) of entering "burst mode."                                 | 0.5           | float     | 0.0 to 1.0           |                                                                                                      |
| `burst_length_min`           | Minimum number of words typed in a single burst.                                   | 2             | int       | >= 1                 |                                                                                                      |
| `burst_length_max`           | Maximum number of words typed in a single burst.                                   | 5             | int       | >= `burst_length_min` |                                                                                                      |
| `grammatical_error_prob`    | Probability (0.0 to 1.0) of introducing a grammatical error in a sentence.        | 0.01          | float     | 0.0 to 1.0           | These errors are *not* corrected.                                                                 |
| `punctuation_error_prob`  | Probability (0.0 to 1.0) of introducing a punctuation error in a sentence.        | 0.01          | float     | 0.0 to 1.0           | These errors are *not* corrected.                                                                 |
| `capitalization_error_prob` | Probability (0.0 to 1.0) of making a capitalization error at the start of a word. | 0.025         | float     | 0.0 to 1.0           | These errors *are* corrected with backspace.                                                       |

## Installation and Usage

1.  **Install Dependencies:**
    ```bash
    pip install pynput nltk
    ```

2.  **Download NLTK Data (if needed):**  The first time you run the script, it will attempt to download necessary NLTK corpora (Brown corpus, words, and punkt tokenizer).  You may see prompts for this.

3.  **Save the Code:** Save the Python code (including all functions and the `main` function) as a `.py` file (e.g., `docusim.py`).

4.  **Run the Script:**
    ```bash
    python docusim.py
    ```

5.  **Input Text:** The program will prompt you to enter the text you want to simulate typing.  Type or paste the text, and then type "END" on a new line to signal the end of the input.

6.  **Customize Parameters (Optional):** You'll be asked if you want to customize the typing parameters.  If you choose 'y', you'll be prompted for each parameter.  If you choose 'n' (or just press Enter), the default values will be used.  If you enter an invalid value, you will be re-prompted.

7.  **Switch to Google Docs:**  After providing the text and parameters, you'll have 5 seconds to switch to an open Google Docs document (make sure it's the active window).

8.  **Observe:** The program will then start simulating the typing process in the Google Docs document.

## Fail-Safes and Important Considerations

*   **Active Window:** DocuSim types directly into the *active* window.  **Ensure that your Google Docs document is the active window** before the typing starts.  If a different window is active, the simulated keystrokes will be sent there, potentially causing unintended consequences.
*   **Interrupting the Script:** You can usually interrupt the script by pressing Ctrl+C in the terminal where you ran the Python script. This will stop the simulated typing.
*   **No Undo Functionality:** DocuSim does *not* have any built-in undo functionality.  The changes it makes to your Google Docs document are the same as if you had typed them yourself.  Use Google Docs' built-in revision history to revert changes if necessary.
*   **Ethical Use:** This tool is intended for educational and research purposes only.  Do *not* use it to misrepresent the creation process of documents or to deceive others.

## Limitations

*   **Simplified Error Model:** The grammatical and punctuation error models are relatively basic.  They don't represent the full range of human errors.
*   **No Contextual Awareness:** The typing simulation is not context-aware.  It doesn't understand the meaning of the text it's typing.
* **No Mouse Movements/Clicks:** The current version of the program only emulates keyboard input. It doesn't simulate mouse activity, scrolling, or other interactions with the Google Docs interface.

## Improvement To Be Made
* **AI Writing Mimicing:** In future (if i have spare time o-o) sample text can be provided to the user for them to type, the model will then learn mistakes made, pauses, WPM speed etc for a user, these can be manually tweaked as well --> built in writing style can be added, e.g. fast, slow, average to more simply implment ¯\_(ツ)_/¯
* **Non Focused Window Support:** Currently the program mimics keyboard input using pynput (VERY SIMPLE LUL), tabbed out windows could be generated (not necessary for personal usecase, (will add if I have spare time ¯\_(ツ)_/¯) use selenium
* **Context Awareness:** Text can first be parsed into LLM asking for where to take breaks as a human would, etc e.g. ("Mimic how long it would take for a human to write the following task providing breaks formatted as "300s delay" where logical, etc)
* **Purposefully misspelt word dictionary:** To further mimic writing style words can be added to a dictionary to be purposefully misspelt
* **Integrate in Chrome:** Integrate fucntionality within a chrome extension for ease of use

## Disclaimer

This program is provided as-is, without any warranty.  The author is not responsible for any unintended consequences arising from the use of this software. Use it responsibly and ethically.
