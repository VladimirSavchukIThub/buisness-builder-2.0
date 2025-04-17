$(document).ready(function() {
    // Элементы интерфейса
    const chatTrigger = $('<div class="chat-trigger"><i class="fas fa-comment"></i></div>');
    const chatContainer = $(`
        <div class="chat-container" style="display: none;">
            <div class="chat-header">
                <h4><i class="fas fa-robot me-2"></i>Бизнес-консультант</h4>
                <div class="chat-controls">
                    <button class="chat-control-btn minimize-btn"><i class="fas fa-minus"></i></button>
                    <button class="chat-control-btn close-btn"><i class="fas fa-times"></i></button>
                </div>
            </div>
            <div class="chat-body">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            <div class="chat-footer">
                <input type="text" class="message-input" placeholder="Введите сообщение...">
                <button class="send-btn"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    `);

    // Добавляем элементы в DOM
    $('body').append(chatTrigger).append(chatContainer);

    // Переменные состояния
    let isMinimized = false;
    let chatHistory = [];
    
    // Функции для управления интерфейсом
    function toggleChat() {
        chatContainer.toggle();
        if (chatContainer.is(':visible')) {
            // Если это первое открытие чата (нет истории), запрашиваем приветствие
            if (chatHistory.length === 0) {
                sendMessage('');
            }
            chatTrigger.hide();
        } else {
            chatTrigger.show();
        }
    }
    
    function minimizeChat() {
        if (isMinimized) {
            chatContainer.removeClass('minimized');
            $('.chat-body, .chat-footer').show();
            $('.minimize-btn i').removeClass('fa-expand').addClass('fa-minus');
        } else {
            chatContainer.addClass('minimized');
            $('.chat-body, .chat-footer').hide();
            $('.minimize-btn i').removeClass('fa-minus').addClass('fa-expand');
        }
        isMinimized = !isMinimized;
    }
    
    function closeChat() {
        chatContainer.hide();
        chatTrigger.show();
        if (isMinimized) {
            minimizeChat(); // Сбрасываем минимизированное состояние
        }
    }
    
    // Функция форматирования времени
    function formatTime() {
        const now = new Date();
        return now.getHours().toString().padStart(2, '0') + ':' + 
               now.getMinutes().toString().padStart(2, '0');
    }
    
    // Функция добавления сообщения в чат
    function addMessage(message, isUser = false) {
        const messageClass = isUser ? 'user-message' : 'bot-message';
        const messageElement = $(`
            <div class="message ${messageClass}">
                ${message}
                <div class="timestamp">${formatTime()}</div>
            </div>
        `);
        
        // Добавляем сообщение перед индикатором набора текста
        $('.typing-indicator').before(messageElement);
        
        // Прокручиваем чат вниз
        $('.chat-body').scrollTop($('.chat-body')[0].scrollHeight);
        
        // Сохраняем в историю
        chatHistory.push({
            message: message,
            isUser: isUser,
            time: formatTime()
        });
    }
    
    // Функция отображения индикатора набора
    function showTypingIndicator() {
        $('.typing-indicator').addClass('active');
    }
    
    function hideTypingIndicator() {
        $('.typing-indicator').removeClass('active');
    }
    
    // Функция отправки сообщения на сервер
    function sendMessage(message) {
        // Если сообщение не пустое, добавляем его в чат
        if (message.trim().length > 0) {
            addMessage(message, true);
        }
        
        // Показываем индикатор загрузки
        showTypingIndicator();
        
        // Отправляем запрос к API
        $.ajax({
            url: '/api/chatbot',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(response) {
                // Скрываем индикатор
                hideTypingIndicator();
                
                // Добавляем ответ бота
                addMessage(response.response);
            },
            error: function(xhr, status, error) {
                // Скрываем индикатор
                hideTypingIndicator();
                
                // Выводим сообщение об ошибке
                console.error('Ошибка при отправке сообщения:', error);
                addMessage('Извините, произошла ошибка. Пожалуйста, попробуйте позже.');
            }
        });
    }
    
    // Обработчики событий
    chatTrigger.on('click', toggleChat);
    $('.minimize-btn').on('click', function(e) {
        e.stopPropagation();
        minimizeChat();
    });
    $('.close-btn').on('click', function(e) {
        e.stopPropagation();
        closeChat();
    });
    $('.chat-header').on('click', function(e) {
        if (isMinimized) {
            minimizeChat();
        }
    });
    
    // Отправка сообщения
    $('.send-btn').on('click', function() {
        const message = $('.message-input').val().trim();
        if (message.length > 0) {
            sendMessage(message);
            $('.message-input').val('');
        }
    });
    
    // Отправка сообщения по нажатию Enter
    $('.message-input').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            const message = $(this).val().trim();
            if (message.length > 0) {
                sendMessage(message);
                $(this).val('');
            }
            e.preventDefault();
        }
    });
}); 