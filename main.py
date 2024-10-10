from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# Вопросы теста Спилбергера-Ханина
questions = [
    "Я чувствую себя спокойно",
    "Я испытываю напряжение",
    "Я чувствую внутреннее удовлетворение",
    "Я нахожусь в состоянии нервного возбуждения",
    "Я чувствую себя расслабленным"
]


# Функция для показа главного меню с кнопками
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Проблемы на работе", callback_data='work_issues'),
            InlineKeyboardButton("Проблемы в семье", callback_data='family_issues')
        ],
        [
            InlineKeyboardButton("Подавленное состояние", callback_data='depression'),
            InlineKeyboardButton("Проблемы со сном", callback_data='sleep_issues')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Выберите категорию, с которой у вас возникли сложности:',
                                        reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text('Выберите категорию, с которой у вас возникли сложности:',
                                                      reply_markup=reply_markup)


# Функция для запуска теста Спилбергера-Ханина
async def start_test(update: Update, context: CallbackContext) -> None:
    context.user_data['current_question'] = 0  # Индекс текущего вопроса
    context.user_data['answers'] = []  # Сбросим ответы
    await ask_question(update, context)


# Функция для задания вопроса
async def ask_question(update: Update, context: CallbackContext) -> None:
    question_index = context.user_data['current_question']
    question = questions[question_index]

    keyboard = [
        [InlineKeyboardButton("1", callback_data=f'answer_{question_index}_1')],
        [InlineKeyboardButton("2", callback_data=f'answer_{question_index}_2')],
        [InlineKeyboardButton("3", callback_data=f'answer_{question_index}_3')],
        [InlineKeyboardButton("4", callback_data=f'answer_{question_index}_4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(text=question, reply_markup=reply_markup)


# Обработка ответа на вопрос
async def handle_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Извлекаем индекс вопроса и ответ
    _, question_index, answer_value = query.data.split('_')
    question_index = int(question_index)
    answer_value = int(answer_value)

    # Сохраняем ответ пользователя
    context.user_data['answers'].append(answer_value)

    # Переходим к следующему вопросу
    context.user_data['current_question'] += 1

    # Проверяем, есть ли еще вопросы
    if context.user_data['current_question'] < len(questions):
        await ask_question(update, context)
    else:
        await finish_test(update, context)  # Завершить тест


# Подсчет результатов и завершение теста
async def finish_test(update: Update, context: CallbackContext) -> None:
    total_score = sum(map(int, context.user_data['answers']))

    # Определяем уровень тревожности
    if total_score < 10:
        level = "низкий"
        result_text = f"Ваш уровень тревожности: {level}. Общий балл: {total_score}"
        advice = "1. Постарайтесь больше отдыхать и сохранять позитивный настрой.\n2. Занимайтесь физической активностью и практикуйте расслабление."
    elif 10 <= total_score <= 20:
        level = "средний"
        result_text = f"Ваш уровень тревожности: {level}. Общий балл: {total_score}"
        advice = "1. Подумайте о том, чтобы сделать небольшие изменения в своей жизни для снижения стресса.\n2. Используйте техники управления тревогой, такие как дыхательные упражнения и медитация.\n3. Не бойтесь обращаться за поддержкой к близким или профессионалам."
    else:
        level = "высокий"
        result_text = f"Ваш уровень тревожности: {level}. Общий балл: {total_score}"
        advice = "1. Постарайтесь обратиться к психологу или консультанту для получения помощи.\n2. Используйте расслабляющие техники, такие как глубокое дыхание и прогрессивная мышечная релаксация.\n3. Следите за здоровым образом жизни — сон, правильное питание и физическая активность могут помочь."

    # Объединяем результат и советы
    result_text += f"\n\nСоветы для вашего уровня тревожности:\n{advice}"

    # Кнопка для возврата к главному меню
    keyboard = [[InlineKeyboardButton("Назад", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(text=result_text, reply_markup=reply_markup)


# Функция для обработки нажатий кнопок
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'depression':
        await start_test(update, context)  # Начинаем тест
    elif query.data.startswith('answer'):
        await handle_answer(update, context)  # Обрабатываем ответ на вопрос
    elif query.data == 'work_issues':
        text = "Проблемы на работе:\n\n1. Попробуйте установить четкие границы между работой и отдыхом.\n2. Общайтесь с коллегами для поиска решений проблем.\n3. Управляйте временем для снижения стресса."
        keyboard = [[InlineKeyboardButton("Назад", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data == 'family_issues':
        text = "Проблемы в семье:\n\n1. Поговорите с близкими о ваших чувствах.\n2. Найдите компромиссы в решении конфликтов.\n3. Если нужно, обратитесь за консультацией к специалисту."
        keyboard = [[InlineKeyboardButton("Назад", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data == 'sleep_issues':
        text = "Проблемы со сном:\n\n1. Установите постоянный режим сна.\n2. Избегайте использования электронных устройств перед сном.\n3. Расслабляйтесь перед сном с помощью дыхательных техник или медитации."
        keyboard = [[InlineKeyboardButton("Назад", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data == 'start':
        await start(update, context)  # Возвращаемся к начальному меню


def main():
    TOKEN = '7844617805:AAG34PmY4fdrEeNHPWwbGUm9sA9sDNvW6aY'

    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик для нажатий на кнопки
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
