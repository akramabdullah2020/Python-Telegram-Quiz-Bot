**Python Telegram Quiz Bot**

This project is an interactive Python-based quiz and training system that operates within the Telegram messaging app. It provides users with a randomized 10-question multiple-choice quiz to assess their Python knowledge.

**Key Components**

*   **Questions:**
    *   An abstract base class `Question` is defined with fields for `question_id`, `question_text`, `options`, and `correct_answer` to store question information.
    *   A subclass `MultipleChoiceQuestion` is created to specifically handle multiple-choice questions. It formats the options for display in Telegram.
*   **Database:**
    *   The project uses an SQLite database (`quiz_bot.db`) to store the quiz questions.
    *   The database includes a `questions` table with the following columns for each question:
        *   `id` (Question ID)
        *   `question_text` (The question text)
        *   `option_a` to `option_d` (Answer choices)
        *   `correct_answer` (The correct answer)
    *   The `Database` class provides methods for connecting to the database, retrieving random questions, saving a new user, deleting a user (and their answers), and saving a user's answer.
*   **Telegram Bot (QuizBot):**
    *   The project uses the `python-telegram-bot` library to interact with the Telegram Bot API.
    *   The `QuizBot` class handles the following tasks:
        *   Storing the Telegram bot token.
        *   Handling Telegram events and user interactions.
        *   Managing the conversation state to track the user's progress through the quiz.
    *   The `QuizBot` class includes methods to handle various commands and events:
        *   `start`: Greets the user and prompts them to enter their name.
        *   `save_user_name`: Saves the user's name and retrieves a list of 10 random questions from the database.
        *   `ask_question`: Displays a random question from the list to the user.
        *   `check_answer`: Checks the user's answer and updates the score.
        *   `show_result`: Displays the final quiz score to the user.
*   **Conversation Handling:**
    *   The project uses the `ConversationHandler` from `telegram.ext` to manage the quiz conversation flow.
    *   The `ConversationHandler` defines entry points and conversation states:
        *   Entry point: The `/start` command, which calls the `start` method.
        *   `WAITING_NAME` state: Waits for the user to enter their name, handled by `save_user_name`.
        *   `WAITING_ANSWER` state: Waits for the user's answer to a question, handled by `check_answer`.
    *   The user transitions between states based on their input, completing the quiz process.

**Code Structure and Workflow:**

1.  **Initialization:** The `QuizBot` is initialized with a Telegram bot token. A `Database` object is also created.
2.  **`/start` Command:** When a user starts the bot with `/start`, the `start` method asks for their name.
3.  **Name Input:** The `save_user_name` method saves the user's name to the database and retrieves 10 random questions. The first question is then presented.
4.  **Question Answering:** The `ask_question` method sends a question and its options to the user. The `check_answer` method validates the user's response, updates the score, saves the answer to the database, and presents the next question (or the final score if all questions have been answered).
5.  **Result Display:** After all questions are answered, the `show_result` method displays the user's final score.

**Key Improvements and Best Practices:**

*   **Object-Oriented Design:** The use of classes (`Question`, `MultipleChoiceQuestion`, `Database`, `QuizBot`) promotes code organization and reusability.
*   **Database Interaction:** Using SQLite makes the quiz data persistent.
*   **Conversation Handling:** `ConversationHandler` effectively manages the quiz flow.
*   **Error Handling (Suggested):** While not present in the current code, adding error handling (e.g., `try-except` blocks) would make the bot more robust. For example, handle potential database errors or invalid user input.
*   **Input Validation (Suggested):** Validating user input (e.g., ensuring they enter a valid option) would improve the user experience.
*   **Internationalization (Suggested):** If you plan to support multiple languages, consider implementing internationalization (i18n).

**To Run the Bot:**

1.  Replace `"Your Token"` with your actual Telegram bot token obtained from BotFather.
2.  Create the `quiz_bot.db` database and the `questions` table with the appropriate columns. Populate the table with your quiz questions.
3.  Install the required libraries: `pip install python-telegram-bot`.
4.  Run the Python script.
