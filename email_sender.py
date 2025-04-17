from flask import Blueprint, current_app
from flask_mail import Mail, Message
import os
import logging
import traceback

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('email_sender')

# Инициализация почтового сервера
mail = Mail()

# Blueprint для обработки email
email_blueprint = Blueprint("email_service", __name__)

# Настройки почтового сервера
def init_mail(app):
    # Принудительно устанавливаем SMTP-сервер Mail.ru
    app.config['MAIL_SERVER'] = 'smtp.mail.ru'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'biznes.prilozheniye@mail.ru'
    app.config['MAIL_PASSWORD'] = 'mzV9zVHhQCsgd9g4CL4E'
    app.config['MAIL_DEFAULT_SENDER'] = ('Бизнес Конструктор', 'biznes.prilozheniye@mail.ru')
    
    # Включаем отладку почты
    app.config['MAIL_DEBUG'] = True
    
    logger.info(f"Почтовый сервер настроен: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    logger.info(f"Использование TLS: {app.config['MAIL_USE_TLS']}, SSL: {app.config['MAIL_USE_SSL']}")
    
    mail.init_app(app)

def send_email(to_email, subject, message, from_email='biznes.prilozheniye@mail.ru'):
    """
    Отправляет email-сообщение указанному получателю.
    
    Args:
        to_email (str): Email получателя
        subject (str): Тема письма
        message (str): Текст сообщения (может содержать HTML)
        from_email (str, optional): Email отправителя. По умолчанию используется DEFAULT_FROM.
    
    Returns:
        bool: True если отправка успешна, False в случае ошибки
    """
    try:
        # Создаем сообщение
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=message,
            sender=('Бизнес Конструктор', from_email)
        )
        
        # Используем current_app вместо mail.app
        logger.info(f"Отправка сообщения на {to_email} через SMTP-сервер Mail.ru")
        
        # Отправляем сообщение
        mail.send(msg)
        
        logger.info(f"Email успешно отправлен на адрес {to_email}")
        return True
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Ошибка при отправке email: {e}")
        logger.error(f"Полный traceback: {error_traceback}")
        return False

def send_response_to_message(message_id, user_email, user_name, subject, response_text):
    """
    Отправляет ответ на сообщение пользователя.
    
    Args:
        message_id (int): ID сообщения в базе данных
        user_email (str): Email пользователя
        user_name (str): Имя пользователя
        subject (str): Тема письма
        response_text (str): Текст ответа
    
    Returns:
        bool: True если отправка успешна, False в случае ошибки
    """
    # Формируем HTML-шаблон письма
    html_message = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4e73df; color: white; padding: 10px 20px; }}
                .content {{ padding: 20px; }}
                .footer {{ font-size: 12px; color: #777; margin-top: 30px; }}
                .message-id {{ font-size: 10px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Ответ на ваше обращение</h2>
                </div>
                <div class="content">
                    <p>Здравствуйте, {user_name}!</p>
                    <p>Благодарим вас за обращение в службу поддержки Бизнес Конструктора.</p>
                    <p>Ваш запрос: <strong>{subject}</strong></p>
                    <div style="margin: 20px 0; padding: 10px; background-color: #f5f5f5; border-left: 4px solid #4e73df;">
                        {response_text.replace(chr(10), '<br>')}
                    </div>
                    <p>С уважением,<br>Команда Бизнес Конструктора</p>
                </div>
                <div class="footer">
                    <p>Это автоматическое сообщение, пожалуйста, не отвечайте на него.</p>
                    <div class="message-id">ID обращения: {message_id}</div>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Отправляем письмо
    return send_email(
        to_email=user_email,
        subject=f"Ответ на ваше обращение: {subject}",
        message=html_message
    ) 