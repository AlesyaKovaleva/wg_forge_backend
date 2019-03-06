Тестовое задание WG Forge (Backend)
----

Тестовое задание выполнено на Python 3

Для запуска проекта нужно запустить сервер PostgreSQL в подготовленом докер-контейнере.
Инструкции по установке https://github.com/wgnet/wg_forge_backend/blob/master/docker_instructions.md

После запуска и подключению к Docker:

- Установить зависимости с помощью `pipenv`:

```bash
pipenv install
```

или с помощью `pip`:

```bash
pip install -r requirements.txt
```


- Для выполнения 1 и 2 задания необходимо запустить файл `main.py`

- Для выполнения 3, 4 заданий необходимо запустить сервер  

```bash
python web_server.py
```

- 5 и 6 задание находится в разработке 🤔