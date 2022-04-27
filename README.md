# hosting
Тема 19. Аналог airbnb, booking.
Гордеева Елена, Корнеева Варвара, Зиатдинов Марсель.
## Vision
Наша цель - разработать приложение, которое можно считать аналогом airbnb.
Возможности приложения:
- снять жильё;
- стать хостом и сдать жильё в аренду;
- чат арендодателя и арендатора;
- рейтинг пользователей: как арендатора, так и арендодателя.


## ER-диаграмма
[Diagram](https://online.visual-paradigm.com/community/share/untitled-xn5l9vwds)


## Getting started

Install all dependencies

```bash
poetry install
```

Create database


Copy all environments variables


```bash
copy example.env
```

Synchronize the database state with the current set of models and migrations.

```bash
alembic upgrade head
```

Install pre-commit

```bash
pre-commit install
```

Run the server

```bash
uvicorn web:app
```

## Design layout
[Figma](https://www.figma.com/file/ojhuuUbVw3gAGSFp4VfX20/hosting?node-id=0%3A1)