# Yatube project
# Описание

Данный проект представляет собой сервис для обмена постами.
Пост в данном случае является совокупностью изоборажения и текста.


# Технологии

* [Python](https://www.python.org)

* [Django REST framework](https://www.django-rest-framework.org)


# Как запустить проект
---

Клонировать репозиторий и перейти в него в командной строке:

```python 
git clone https://github.com/illager10/api_final_yatube.git
```

```python 
cd yatube_api
```

Cоздать и активировать виртуальное окружение:

```python 
python -m venv venv
```

```python 
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```python 
pip install -r requirements.txt
```

Выполнить миграции:

```python 
python manage.py migrate
```

Запустить проект:

```python 
python manage.py runserver
```

<!-- [![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml) -->
