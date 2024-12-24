
import sqlite3
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext


class Question(ABC):
    def __init__(self, question_id, question_text, options, correct_answer):
        self.question_id = question_id
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer

    @abstractmethod
    def get_question_text(self):
        pass

    @abstractmethod
    def get_options(self):
        pass

    @abstractmethod
    def check_answer(self, user_answer):
        pass


class MultipleChoiceQuestion(Question):
    def __init__(self, question_id, question_text, option_a, option_b, option_c, option_d, correct_answer):
        options = [option_a, option_b, option_c, option_d]
        super().__init__(question_id, question_text, options, correct_answer)

    def get_question_text(self):
        return self.question_text

    def get_options(self):
        return "\n".join([f"A. {self.options[0]}", f"B. {self.options[1]}", 
                          f"C. {self.options[2]}", f"D. {self.options[3]}"])

    def check_answer(self, user_answer):
        return user_answer.upper() == self.correct_answer.upper()


class Database:
    def __init__(self, db_name="quiz_bot.db"):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def get_random_questions(self, num_questions=10):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (num_questions,))
        questions = cursor.fetchall()
        conn.close()
        return questions

    def save_user(self, name, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, user_id) VALUES (?, ?)", (name, user_id))
        conn.commit()
        conn.close()

    def delete_user(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM answers WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def save_answer(self, user_id, question_id, user_answer):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO answers (user_id, question_id, user_answer) VALUES (?, ?, ?)", 
                       (user_id, question_id, user_answer))
        conn.commit()
        conn.close()

    def get_correct_answer(self, question_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT correct_answer FROM questions WHERE id=?", (question_id,))
        correct_answer = cursor.fetchone()[0]
        conn.close()
        return correct_answer


class QuizBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
      
        self.db = Database()

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text("مرحباً! من فضلك، أدخل اسمك لبدء الاختبار.")
        return "WAITING_NAME"

    async def save_user_name(self, update: Update, context: CallbackContext):
        name = update.message.text
        user_id = update.message.from_user.id
        self.db.delete_user(user_id)
        self.db.save_user(name, user_id)
        await update.message.reply_text(f"مرحباً {name}! سيتم اختيار 10 أسئلة عشوائية لك.")
        return await self.ask_question(update, context)

    async def ask_question(self, update: Update, context: CallbackContext, question_index=0, score=0):
        questions_data = self.db.get_random_questions()
        question_data = questions_data[question_index]

        # تحويل البيانات من قاعدة البيانات إلى كائنات من فئة MultipleChoiceQuestion
        question = MultipleChoiceQuestion(
            question_data[0], question_data[1], question_data[2], question_data[3], 
            question_data[4], question_data[5], question_data[6]
        )

        await update.message.reply_text(f"السؤال {question_index + 1}: {question.get_question_text()}\n{question.get_options()}")
        context.user_data['questions'] = questions_data
        context.user_data['score'] = score
        context.user_data['question_index'] = question_index
        return "WAITING_ANSWER"

    def check_answer(self, update: Update, context: CallbackContext):
        user_answer = update.message.text.upper()
        question_index = context.user_data['question_index']
        questions_data = context.user_data['questions']
        question_data = questions_data[question_index]

        question = MultipleChoiceQuestion(
            question_data[0], question_data[1], question_data[2], question_data[3], 
            question_data[4], question_data[5], question_data[6]
        )

        if question.check_answer(user_answer):
            context.user_data['score'] += 1
        self.db.save_answer(update.message.from_user.id, question_data[0], user_answer)

        # Check if we have more questions
        if question_index + 1 < len(questions_data):
            return self.ask_question(update, context, question_index + 1, context.user_data['score'])
        else:
            return self.show_result(update, context)

    async def show_result(self, update: Update, context: CallbackContext):
        score = context.user_data['score']
        await update.message.reply_text(f"لقد أكملت الاختبار! لقد أجبت بشكل صحيح على {score} من أصل 10 أسئلة.")
        await update.message.reply_text("شكراً للمشاركة! نتمنى لك يوم سعيد.")
        return ConversationHandler.END

    def main(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                "WAITING_NAME": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_user_name)],
                "WAITING_ANSWER": [MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_answer)],
            },
            fallbacks=[],
        )

        self.application.add_handler(conv_handler)
        self.application.run_polling()
        self.application.idle()


if __name__ == '__main__':
    token ="Your Token"
    quiz_bot = QuizBot(token)
    quiz_bot.main()
