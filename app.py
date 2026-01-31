#!/usr/bin/env python3
"""
Flask веб-приложение для EtsyAIFactory
Позволяет управлять автоматизацией листингов через веб-интерфейс
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
CORS(app)

# Конфигурация
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"

# Статус процессов
process_status = {
    "running": False,
    "current_task": None,
    "progress": 0,
    "logs": []
}


class TaskRunner(threading.Thread):
    """Поток для запуска задач без блокирования приложения"""
    
    def __init__(self, task_type, params=None):
        super().__init__(daemon=True)
        self.task_type = task_type
        self.params = params or {}
    
    def run(self):
        try:
            process_status["running"] = True
            process_status["current_task"] = self.task_type
            process_status["progress"] = 0
            
            # Логирование
            log_msg = f"[{datetime.now()}] Запуск задачи: {self.task_type}"
            process_status["logs"].append(log_msg)
            print(log_msg)
            
            # Запуск Python скрипта
            cmd = f"cd {BASE_DIR} && python etsy_ai_factory.py"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                log_msg = f"✅ Задача {self.task_type} успешно завершена"
            else:
                log_msg = f"❌ Ошибка: {result.stderr}"
            
            process_status["logs"].append(log_msg)
            process_status["progress"] = 100
            
        except Exception as e:
            error_msg = f"❌ Исключение: {str(e)}"
            process_status["logs"].append(error_msg)
            print(error_msg)
        
        finally:
            process_status["running"] = False


# ═══════════════════════════════════════════════════════════════════════════
# МАРШРУТЫ ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Получить статус приложения"""
    
    # Проверяем наличие API ключей
    etsy_key = os.getenv('ETSY_API_KEY')
    config_exists = (CONFIG_DIR / '.env').exists()
    
    return jsonify({
        "app_name": "EtsyAIFactory v3.0",
        "version": "3.0",
        "configured": bool(etsy_key) and config_exists,
        "process": process_status,
        "output_dir": str(OUTPUT_DIR),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Получить текущую конфигурацию"""
    config_file = CONFIG_DIR / 'product_config.json'
    
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {
            "niche": "funny cat",
            "keyword": "sarcastic cat with coffee",
            "description": "Funny cat design for t-shirt",
            "listings_count": 1
        }
    
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def save_config():
    """Сохранить конфигурацию"""
    data = request.json
    config_file = CONFIG_DIR / 'product_config.json'
    
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({"status": "success", "message": "Конфигурация сохранена"})


@app.route('/api/create-listings', methods=['POST'])
def create_listings():
    """Создать листинг (ТОЛЬКО 1 за раз)"""
    
    if process_status["running"]:
        return jsonify({"error": "Процесс уже запущен"}), 409
    
    data = request.json
    
    # Сохраняем конфигурацию (ТОЛЬКО 1 листинг за раз!)
    config = {
        "niche": data.get('niche', 'funny cat'),
        "keyword": data.get('keyword', ''),
        "description": data.get('description', ''),
        "title": data.get('title', ''),
        "tags": data.get('tags', []),
        "listings_count": 1  # ВСЕГДА 1 листинг за раз
    }
    
    config_file = CONFIG_DIR / 'product_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Запускаем в отдельном потоке
    runner = TaskRunner('create_listings', config)
    runner.start()
    
    return jsonify({
        "status": "started",
        "message": "✅ Начато создание 1 листинга..."
    })


@app.route('/api/analyze-niche', methods=['POST'])
def analyze_niche():
    """Анализ ниши и конкурентов"""
    
    if process_status["running"]:
        return jsonify({"error": "Процесс уже запущен"}), 409
    
    data = request.json
    niche = data.get('niche', 'funny cat')
    
    runner = TaskRunner('analyze_niche', {'niche': niche})
    runner.start()
    
    return jsonify({
        "status": "started",
        "message": f"✅ Анализ ниши '{niche}' запущен..."
    })


@app.route('/api/niche-suggestions', methods=['GET'])
def get_niche_suggestions():
    """Получить рекомендуемые ниши"""
    
    popular_niches = [
        {
            "name": "Смешные коты",
            "keyword": "funny cat",
            "demand": "Высокий",
            "competition": "Средняя",
            "price_range": "$15-25"
        },
        {
            "name": "Подарки учителям",
            "keyword": "teacher appreciation",
            "demand": "Высокий",
            "competition": "Средняя",
            "price_range": "$18-28"
        },
        {
            "name": "Хеллоуин ведьмы",
            "keyword": "halloween witch",
            "demand": "Высокий",
            "competition": "Высокая",
            "price_range": "$16-26"
        },
        {
            "name": "Мама кофе",
            "keyword": "mom coffee lover",
            "demand": "Очень высокий",
            "competition": "Высокая",
            "price_range": "$17-27"
        },
        {
            "name": "Собаки любители",
            "keyword": "dog lover",
            "demand": "Очень высокий",
            "competition": "Высокая",
            "price_range": "$18-28"
        },
        {
            "name": "Йога мотивация",
            "keyword": "yoga motivation",
            "demand": "Средний",
            "competition": "Низкая",
            "price_range": "$20-30"
        },
        {
            "name": "Геймер подарок",
            "keyword": "gamer gift",
            "demand": "Высокий",
            "competition": "Средняя",
            "price_range": "$17-27"
        },
        {
            "name": "Путешественник",
            "keyword": "traveler adventure",
            "demand": "Средний",
            "competition": "Низкая",
            "price_range": "$19-29"
        }
    ]
    
    return jsonify({
        "niches": popular_niches,
        "tips": [
            "🔍 Низкая конкуренция = лучше для новичков",
            "💰 Выбирай ниши с высоким спросом",
            "🎯 Специализируйся в одной нише перед расширением",
            "📊 Анализируй конкурентов перед созданием",
            "⚡ Редкие ниши часто имеют выше цены"
        ]
    })


@app.route('/api/analyze-competitors', methods=['POST'])
def analyze_competitors():
    """Анализ конкурентов по ключевому слову"""
    
    data = request.json
    keyword = data.get('keyword', '')
    
    if not keyword:
        return jsonify({"error": "Укажите ключевое слово"}), 400
    
    # Имитируем анализ конкурентов (в реальности тут API запросы)
    competitors_data = {
        "keyword": keyword,
        "analysis": {
            "average_price": f"${15 + hash(keyword) % 15}-${25 + hash(keyword) % 15}",
            "competition_level": ["Низкая", "Средняя", "Высокая"][hash(keyword) % 3],
            "demand_level": ["Низкий", "Средний", "Высокий", "Очень высокий"][hash(keyword) % 4],
            "estimated_monthly_sales": f"{50 + hash(keyword) % 200}+ продаж/месяц",
            "top_tags": [
                keyword,
                keyword.split()[0] if len(keyword.split()) > 0 else keyword,
                "t-shirt",
                "gift",
                "custom"
            ][:5],
            "recommended_title_length": "100-140 символов",
            "best_upload_time": "Вторник-четверг, 14:00-18:00",
            "tips": [
                "✅ Используй по 13 тегов максимум",
                "✅ Заголовок в первых 60 символов должен содержать ключевое слово",
                "✅ Добавь видео - поднимает конверсию на 40%",
                "✅ Минимум 6 фотографий для лучших результатов",
                "✅ Обновляй листинг каждый месяц"
            ]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(competitors_data)


@app.route('/api/logs')
def get_logs():
    """Получить логи"""
    return jsonify({
        "logs": process_status["logs"][-50:],  # Последние 50 логов
        "running": process_status["running"]
    })


@app.route('/api/output')
def get_output():
    """Получить список готовых файлов"""
    files = {
        "designs": [],
        "mockups": [],
        "videos": [],
        "drafts": []
    }
    
    try:
        for category in files.keys():
            path = OUTPUT_DIR / category
            if path.exists():
                files[category] = [f.name for f in path.glob('*')]
    except Exception as e:
        print(f"Ошибка при чтении файлов: {e}")
    
    return jsonify(files)


@app.route('/api/output/<category>/<filename>')
def download_output(category, filename):
    """Скачать файл из output"""
    try:
        file_path = OUTPUT_DIR / category / filename
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/health')
def health_check():
    """Health check для хостинга"""
    return jsonify({
        "status": "ok",
        "app": "EtsyAIFactory Web Interface",
        "timestamp": datetime.now().isoformat()
    })


# ═══════════════════════════════════════════════════════════════════════════
# ЗАПУСК ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Создаем необходимые директории
    LOGS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)
    
    # Запускаем приложение
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'False') == 'True'
    )
