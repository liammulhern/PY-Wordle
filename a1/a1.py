"""
Wordle
Assignment 1
Semester 1, 2022
CSSE1001/CSSE7030
"""

from string import ascii_lowercase
from typing import Optional

from a1_support import (
    load_words,
    choose_word,
    VOCAB_FILE,
    ANSWERS_FILE,
    CORRECT,
    MISPLACED,
    INCORRECT,
    UNSEEN,
)

__author__ = "Liam Mulhern, 47428748"
__email__ = "l.mulhern@uqconnect.edu.au"

# Global Constants
MAX_USER_TURNS = 6
WORD_SIZE = 6
PRINT_BREAK_15 = "-"*15
PRINT_BREAK_12 = "-"*12

def has_won(guess: str, answer: str) -> bool:
    """ Determines if the user's guess is correct.  

    Parameters:
        guess (str): Parsed input from the user.
        answer (str): Correct word chosen from word list.

    Returns:
        bool: True if the guess matches answer exactly. Otherwise, False.
    """

    return guess == answer

def has_lost(guess_number: int) -> bool:
    """ Determines if the user's total guesses exceeds the constant limit.  

    Parameters:
        guess_number (int): Additive count of user's turns.

    Returns:
        bool: True if guess_number is equal to or greater than the maximum number of allowed guesses. Otherwise, False.
    """
    return guess_number >= MAX_USER_TURNS

def remove_word(words: tuple[str, ...], word: str) -> tuple[str, ...]:
    """ Removes a string from a tuple<str>.

    Parameters:
        words (tuple<str>): List of valid vocab words imported from a1_support.
        word (str): Single word that will be removed from words.

    Returns:
        tuple<str>: Returns a tuple<str> copy of words with word removed.
    """

    words_copied = list(words)  # Casts immutable tuple<str> to mutable list<str> so it can be modified. Can be bad practice for memory management with large tuples, but in this case the impact is insignificant.
    words_copied.remove(word)

    return tuple(words_copied)  # Re-casts list<str> to tuple<str>

def prompt_user(guess_number: int, words: tuple[str, ...]) -> str:
    """ Prompts the user for the next guess, reprompting until either a valid guess is entered, or a selection for help, keyboard, or quit is made.

        Parameters:
            guess_number (int): Additive count of user's turns.
            words (tuple<str>): List of valid vocab words imported from a1_support.

        Returns: 
            str: String message representing the valid guess or request for help, keyboard, or quit.
    """

    guess = input(f"Enter guess {guess_number}: ")

    while not valid_guess(guess, words):
        if len(guess) == WORD_SIZE:  
            print("Invalid! Unknown word")
        else:
            print(f"Invalid! Guess must be of length {WORD_SIZE}")
        guess = input(f"Enter guess {guess_number}: ")

    return guess.lower()

def process_guess(guess: str, answer: str) -> str:
    """ Examines the guess string and compares it with answer, creating a new guess_representation string in which each letter of guess is replaced by:
            A green square if that letter occurs in the same position in answer;
            A yellow square if that letter occurs in a different position in answer; or
            A black square if that letter does not occur in answer.
    
    Note:
        The guess string may contain duplicate characters, but in the processed string only one character can have a non-black square. 
        The function prioritises duplicate characters in the correct position by replacing them with a green square; 
        if no duplicate characters meet this criteria the first different position is replaced with a yellow square.

    Parameters:
        guess (str): Parsed guess input from the user.
        answer (str): Correct word chosen from answer list.
        guess_representation (list<str>): List of coloured squares representing the position of characters when guess is compared to answer; Created with a length of WORD_SIZE and all elements as black squares.
        answer_duplicates (list<str>): Contains characters already iterated and shared by guess and answer.
    
    Returns:
        str: Modified string representation of guess, in which each letter is replace by green, yellow, or black squares depending on occurence.
    """

    guess_representation = [INCORRECT]*WORD_SIZE  # Mutable list used rather than immutable string so index replacement can occur
    answer_duplicates = []

    for i, a in enumerate(answer): 
        for j, g in enumerate(guess):
            if a is g and g not in answer_duplicates:
                if i is j:  # Same character position in a and g, therefore green square.
                    guess_representation[j] = CORRECT
                    answer_duplicates.append(a)
                    break
                elif answer[i] is guess[i]:  # Same character position in answer and guess with priority for correct duplicate, therefore green square.
                    guess_representation[i] = CORRECT
                    answer_duplicates.append(a)
                    break
                elif i is not j:  # Same character but different position, therefore yellow square.
                    guess_representation[j] = MISPLACED
                    answer_duplicates.append(a)
                    break

    return ''.join(guess_representation)  # Flatten list<str> to string

def update_history(history: tuple[tuple[str, str], ...], guess: str, answer: str ) -> tuple[tuple[str, str], ...]:
    """ Appends updates to the game history to include the latest guess and it processed form.

    Parameters:
        history (tuple<tuple<str, str>,...>): Current tuple of game history containing a tuple<str, str> with the first string representing the guess and second representing its processed form.
        guess (str): Parsed guess input from the user.
        answer (str): Correct word chosen from answer list.

    Returns:
        tuple<tuple<str, str>,...> : Appended game history which includes the lastest guess and its processed form.

    """

    processed_guess = process_guess(guess, answer)

    history_element = (guess, processed_guess)

    updated_history = history + (history_element,)

    return updated_history

def print_history(history: tuple[tuple[str, str], ...]) -> None:
    """ Prints the guess history in a user friendly way.

    Parameters:
        history (tuple<tuple<str, str>,...>): Current tuple of game history containing a tuple<str, str> with the first string representing the guess and second representing its processed form.

    Returns:
        None
    """

    for i, history_entry in enumerate(history):
        print(PRINT_BREAK_15)
        
        formatted_guess = f"Guess {i+1}:  {UNSEEN.join(history_entry[0])}" # Format history guess so that each character is followed by space. I.e: hello -> h e l l o
        formatted_processed_guess = UNSEEN*9 + history_entry[1]  # UNSEEN*9 used for element formatting using white space.

        print(formatted_guess)
        print(formatted_processed_guess)

    print(PRINT_BREAK_15)
    print()

def print_keyboard(history: tuple[tuple[str, str], ...]) -> None:
    """ Prepares the information currently known about each letter to be printed in print_dictionary() function.

    Parameters:
        history (tuple<tuple<str, str>,...>): Current tuple of game history containing a tuple<str, str> with the first string representing the guess and second representing its processed form.

    Returns:
        None
    """

    keyboard_history = {}.fromkeys(ascii_lowercase, " ")  # Create dictionary with letters a -> z as keys and white space as default entry for easier print formating.

    for history_entry in history:
        for g, guess in enumerate(history_entry[1]):
            if keyboard_history[history_entry[0][g]] not in (CORRECT, MISPLACED):
                keyboard_history[history_entry[0][g]] = guess
            elif keyboard_history[history_entry[0][g]] == MISPLACED and guess == CORRECT:
                keyboard_history[history_entry[0][g]] = guess

    print("\nKeyboard information")
    print(PRINT_BREAK_12)
    print_dictionary(keyboard_history, 2)
    print()

def print_stats(stats: tuple[int, ...]) -> None:
    """ Prints player stats in a user friendly way.

    Parameters:
        stats(tuple<int>): Seven elements which are the number of rounds won in 1 -> 6 guesses, and the number of rounds lost respectively.

    Returns:
        None
    """

    print("\nGames won in:")

    for i, stat in enumerate(stats):
        if i < (len(stats) - 1):
            print(f"{i+1} moves: {stat}")
        else:
            print(f"Games lost: {stat}")

def valid_guess(guess: str, words: tuple[str, ...]) -> bool:
    """ Ensure that the user's guess input meets the prerequisites required for a guess to be valid.

    Parameters:
        guess (str): Parsed input from the user.
        words (tuple<str>): List of valid vocab words imported from a1_support.
        
    Returns:
        bool: True if guess meets length, and valid vocab requirments. Otherwise, False.
    """

    return ((len(guess) == WORD_SIZE) and (guess in words)) or (guess.lower() in ('k', 'h', 'q', 'y'))

def valid_command(command: str, history: tuple[tuple[str, str], ...]) -> bool:
    """ Tests if user input is a valid command rather than a guess.

    Parameters:
        command (str): Parsed input from the user.
        history (tuple<tuple<str, str>,...>): Current tuple of game history containing a tuple<str, str> with the first string representing the guess and second representing its processed form.

    Returns:
        bool: True if the user input is a valid command. Otherwise, False.
    """

    if command.lower() == 'k':
        print_keyboard(history)
    elif command.lower() == 'h':
        print("Ah, you need help? Unfortunate.")
    
    return command.lower() in ('k', 'h', 'q')

def command_restart() -> bool:
    """ Prompts the user if they want to restart the game.

    Return:
        bool: True if user input is 'Y' or 'y'. Otherwise, False.
    """

    return input("Would you like to play again (y/n)? ").lower() == 'y'

def print_dictionary(dictionary: dict[str, str], columns: int = 2) -> None:
    """ Prints a dictionary in n columns in a user-friendly way. By default there are 2 veritcal columns.

    Parameters:
        keyboard_print_row (str): Appended string that contains each rows formatted information and is reset for each new line.

    Return:
        None.

    """

    keyboard_print_row = ''

    for i, (k, v) in enumerate(dictionary.items()):
        if not (i+1) % columns or (i + 1) >= len(dictionary): 
            keyboard_print_row += f"{k}: {v}"
            print(keyboard_print_row)
            keyboard_print_row = ''
        else:
            keyboard_print_row += f"{k}: {v}\t"

def main(): 
    """ Main game function that coordinates overall gameplay. 

    Parameters:
        vocab (tuple<str>): list of all possible words the user can submit
        possible_answers (tuple<str>): list of all possible answers the game can select.
        stats(tuple<int>): Seven elements which are the number of rounds won in 1 -> 6 guesses, and the number of rounds lost respectively.
    """

    ############## Initialised Game Variables ###############

    vocab = load_words(VOCAB_FILE)
    possible_answers = load_words(ANSWERS_FILE)
    stats = (0, 0, 0, 0, 0, 0, 0)

    ####################### Game Loop #######################

    while True:
        ############## Local Game Variables #################
        count = 1
        guess = ''
        history = ()
        answer = choose_word(possible_answers)

        ##################### Guess Loop ####################

        while not (has_won(guess, answer) or has_lost(count-1)):
            guess = prompt_user(count, vocab)

            if not valid_command(guess, history):
                history = update_history(history, guess, answer)
                print_history(history)
                count += 1

            elif guess.lower() == 'q':
                break  # Exit Guess Loop

        ################# Post Game Sequence #################

        if guess.lower() == 'q':
            break  # Exit Game Loop

        if has_won(guess, answer):
            print(f"Correct! You won in {count-1} guesses!")
        else:
            print(f"You lose! The answer was: {answer}")
            count += 1

        stats_copied = list(stats)
        stats_copied[count-2] += 1
        stats = tuple(stats_copied)

        print_stats(stats)
        remove_word(possible_answers, answer)

        ##################### Restart Game #####################

        if not command_restart():
            break

if __name__ == "__main__":
    main()