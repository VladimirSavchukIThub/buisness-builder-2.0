document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('businessForm');
    const calculateBtn = document.getElementById('calculateBtn');
    const totalPriceElement = document.getElementById('totalPrice');
    
    // Вызываем функцию для первоначального расчета при загрузке страницы
    // (если какие-то элементы уже выбраны)
    updateQuickEstimate();
    
    // Обработчик кнопки расчета
    calculateBtn.addEventListener('click', async function() {
        // Проверка валидности формы
        if (!isFormValid()) {
            alert('Пожалуйста, выберите тип и размер бизнеса');
            return;
        }
        
        // Сбор данных формы
        const formData = {
            business_type: document.querySelector('input[name="businessType"]:checked').value,
            business_size: document.querySelector('input[name="businessSize"]:checked').value,
            features: Array.from(document.querySelectorAll('input[name="features"]:checked')).map(cb => cb.value)
        };
        
        try {
            // Отправка данных на сервер
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ошибка! Статус: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Отображение итоговой цены с анимацией
            animatePrice(data.price);
            
        } catch (error) {
            console.error('Ошибка при расчете:', error);
            alert('Произошла ошибка при расчете стоимости. Пожалуйста, попробуйте снова.');
        }
    });
    
    // Функция проверки валидности формы
    function isFormValid() {
        const businessTypeSelected = document.querySelector('input[name="businessType"]:checked');
        const businessSizeSelected = document.querySelector('input[name="businessSize"]:checked');
        
        return businessTypeSelected && businessSizeSelected;
    }
    
    // Функция анимации изменения цены
    function animatePrice(targetPrice) {
        const duration = 1000; // длительность анимации в миллисекундах
        const startPrice = parseInt(totalPriceElement.textContent.replace(/\s/g, '')) || 0;
        const startTime = performance.now();
        
        function updatePrice(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            
            // Функция плавности (easing)
            const easeOutQuad = t => t * (2 - t);
            const easedProgress = easeOutQuad(progress);
            
            const currentPrice = Math.floor(startPrice + (targetPrice - startPrice) * easedProgress);
            totalPriceElement.textContent = currentPrice.toLocaleString('ru-RU');
            
            if (progress < 1) {
                requestAnimationFrame(updatePrice);
            }
        }
        
        requestAnimationFrame(updatePrice);
    }
    
    // Быстрый предварительный расчет на клиенте при изменении опций
    function updateQuickEstimate() {
        // Находим выбранный тип бизнеса
        const selectedTypeRadio = document.querySelector('input[name="businessType"]:checked');
        if (!selectedTypeRadio) {
            console.log("Тип бизнеса не выбран");
            return;
        }
        
        // Находим выбранный размер бизнеса
        const selectedSizeRadio = document.querySelector('input[name="businessSize"]:checked');
        if (!selectedSizeRadio) {
            console.log("Размер бизнеса не выбран");
            return;
        }
        
        // Получаем базовую цену выбранного типа бизнеса
        const basePrice = parseInt(selectedTypeRadio.dataset.price) || 0;
        console.log("Базовая цена:", basePrice, "Атрибут data-price:", selectedTypeRadio.dataset.price);
        
        // Получаем множитель размера бизнеса
        const sizeMultiplier = parseFloat(selectedSizeRadio.dataset.multiplier) || 1.0;
        console.log("Множитель:", sizeMultiplier, "Атрибут data-multiplier:", selectedSizeRadio.dataset.multiplier);
        
        // Считаем стоимость выбранных функций
        let featuresPrice = 0;
        document.querySelectorAll('input[name="features"]:checked').forEach(checkbox => {
            const featurePrice = parseInt(checkbox.dataset.price) || 0;
            console.log("Цена функции:", checkbox.value, featurePrice, "Атрибут data-price:", checkbox.dataset.price);
            featuresPrice += featurePrice;
        });
        
        // Рассчитываем предварительную итоговую цену
        const estimatedPrice = Math.round((basePrice * sizeMultiplier) + featuresPrice);
        console.log("Итоговая предварительная цена:", estimatedPrice);
        
        // Обновляем отображение цены
        totalPriceElement.textContent = estimatedPrice.toLocaleString('ru-RU');
    }
    
    // Добавляем обработчики изменений для быстрого предварительного расчета
    document.querySelectorAll('input[name="businessType"]').forEach(radio => {
        radio.addEventListener('change', updateQuickEstimate);
    });
    
    document.querySelectorAll('input[name="businessSize"]').forEach(radio => {
        radio.addEventListener('change', updateQuickEstimate);
    });
    
    document.querySelectorAll('input[name="features"]').forEach(checkbox => {
        checkbox.addEventListener('change', updateQuickEstimate);
    });
}); 