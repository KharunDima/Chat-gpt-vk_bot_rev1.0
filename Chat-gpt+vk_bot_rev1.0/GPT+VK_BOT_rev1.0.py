import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import asyncio
import openai
import time

openai.api_key = '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'  # ключ API от OpenAI

# Инициализация VK API
vk_session = vk_api.VkApi(token='vk1.a.DO6_MgqBTskT8VRmjM_sDo2DnoRmXw9-sz2OM94lWa_F5dhWQPMv0cjUTCWkzKTRmo-6cZJ1YssXJmzeSWNbzA5vS5QiqkRHYOzhbMuPPgk-s9rKZDg_-Q59zq90XAuGwx8vjgxka38yuBYVqyaAME6eBKdhLR_VDwKgnJzqFxw44KIpJXiYd1cQcA2nK7rAHej6fzqX76ehjKACXuiYug')  #  токен доступа VK API
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

last_request_time = 0  # Время последнего запроса

# Функция для отправки сообщений в чат пользователя ВКонтакте
def send_message(user_id, message):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=0
    )

# Функция для получения ответа от чат-бота
async def ask_chat_gpt(question):
    global last_request_time

    if not question:  # Проверка на пустое сообщение
        return 'Пожалуйста, введите вопрос.'  # Отправим сообщение об ошибке, если вопрос пустой

    current_time = time.time()
    time_elapsed = current_time - last_request_time

    if time_elapsed >= 10:
        try:
            response = openai.Completion.create(
                engine='text-davinci-003',  # Выбор модели GPT-3 (другие варианты: 'davinci' или 'curie')
                prompt=question,  # Ваш вопрос
                max_tokens=2000,  # Максимальное количество символов в ответе
                temperature=0.7,  # "Температура" генерации (чем выше, тем более неожиданные ответы)
                n=1,  # Количество вариантов ответа
                stop=None,  # Условие остановки генерации (если нужно)
                echo=False  # Возвращать только сгенерированный текст
            )

            last_request_time = current_time  # Обновляем время последнего запроса

            if response and response.choices:
                return response.choices[0].text.strip()
            else:
                return 'Ошибка при вызове API'
        except openai.error.RateLimitError:
            return ''  # Возвращаем пустой ответ, чтобы не повторять сообщение об ошибке
        except openai.error.ServiceUnavailableError:
            return 'Сервер перегружен. Попробуйте повторить запрос позже.'
    else:
        return ''  # Возвращаем пустой ответ, чтобы не повторять сообщение об ошибке

# Функция для обработки сообщений от пользователя
async def handle_message(event):
    if event.type == VkEventType.MESSAGE_NEW:
        # Получаем текст сообщения от пользователя
        question = event.text

        # Генерируем ответ от чат-бота
        response = await ask_chat_gpt(question)

        if response:
            # Отправляем ответ пользователю
            send_message(event.user_id, response)

async def main():
    # Ожидаем и обрабатываем сообщения от пользователя
    for event in longpoll.listen():
        await handle_message(event)

# Запуск асинхронной программы
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())