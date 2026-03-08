# 🎬 FlixKG — Онлайн-кинотеатр Кыргызстана

<div align="center">
  <img src="https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django">
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/SQLite-Database-orange?style=for-the-badge&logo=sqlite">
  <img src="https://img.shields.io/badge/REST-API-red?style=for-the-badge">
</div>

<br>

> Платформа для онлайн-бронирования билетов в кино с удобным выбором мест, оплатой и электронными билетами.

---

## ✨ Возможности

- 🎥 Просмотр афиши и информации о фильмах
- 💺 Интерактивный выбор мест в зале (обычные и VIP)
- 💳 Онлайн-оплата с выдачей чека
- 🎫 Электронные билеты с QR-кодом в PDF
- 👤 Личный кабинет с историей бронирований
- 🔔 Уведомления
- ⚙️ Панель управления для администратора

---

## 🚀 Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Aizirek11/FlixKg.git
cd FlixKg
```

### 2. Создать виртуальное окружение
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения
Создай файл `.env` в корне проекта:
```
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 5. Применить миграции
```bash
python manage.py migrate
```

### 6. Создать суперпользователя
```bash
python manage.py createsuperuser
```

### 7. Запустить сервер
```bash
python manage.py runserver
```

Открой в браузере: **http://127.0.0.1:8000**

---

## 🗂️ Структура проекта
```
cinema/
├── config/          # Настройки проекта
├── movies/          # Фильмы, актёры, жанры
├── bookings/        # Залы, места, сеансы, бронирование
├── payments/        # Оплата и чеки
├── users/           # Авторизация и профиль
├── notifications/   # Уведомления
├── templates/       # HTML шаблоны
├── static/          # CSS, JS, изображения
└── media/           # Загружаемые файлы
```

---

## 🛠️ Технологии

| Технология | Описание |
|------------|----------|
| Django 6.0 | Backend фреймворк |
| Django REST Framework | REST API |
| SimpleJWT | JWT авторизация |
| drf-spectacular | Swagger документация |
| SQLite | База данных |
| ReportLab | Генерация PDF билетов |

---

## 📖 API Документация

После запуска сервера доступна по адресу:
**http://127.0.0.1:8000/api/docs/**

---

## 👩‍💻 Автор

**Aizirek** — [GitHub](https://github.com/Aizirek11)