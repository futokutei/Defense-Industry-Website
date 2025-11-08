<<<<<<< HEAD
# Roadmap на 3 тижні

## W3 — Категорії, теги, пошук, нотифікації
BE:
- Модель Category, Tag, зв’язки Many-to-Many з Product.
- GET /products?category=&tag=&query= — пошук і фільтрація.
- Email-нотифікації (SMTP/Flask-Mail) при створенні/оновленні/видаленні продуктів.
- Індекси під пошук (title, description, category_id).

FE:
- UI для фільтрів (категорії, теги, пошуковий рядок).
- Екран нотифікацій для адміністраторів.

Цілі: p95 GET ≤ 250 мс при 50 RPS; помилки < 0.5%.

DoD: дашборд пошукових запитів, логування request_id, тестові email через SMTP sandbox, 3 е2е тести (фільтр, пошук, нотифікація).

## W4 — Багатомовність, версіонування, розширені ролі
BE:
- i18n для назв, описів продуктів (таблиця ProductTranslation або JSONB).
- Версіонування контенту (історія змін у ProductHistory, rollback).
- Розширена система ролей: Role, Permission; ACL-перевірки на рівні ендпойнтів.

FE:
- Перемикач мови (UA/EN); fallback, збереження вибору в localStorage.
- UI для перегляду історії змін продукту.
- Панель керування ролями (чекбокси прав).

Цілі: переключення мови ≤ 100 мс; p95 API ≤ 300 мс; 0 критичних 403/401 кейсів.

DoD:
- Повна локалізація ключових сторінок;
- 80% покриття unit тестами ACL;
- тест rollback контенту;
- security-review PR (рівні доступу).

## W5 — Інтеграції (мобільні API + аналітика)

BE:
- REST API v2 для мобільних клієнтів: GET /api/v2/products, POST /api/v2/login.
- JWT або session-based auth із refresh-токеном.
- Інтеграція з Google Analytics (events: view_product, login, add_to_cart).

FE:
- Вбудовані GA події на основних сторінках.
- Документація OpenAPI/Swagger для мобільного API.

Цілі: p95 мобільних запитів ≤ 200 мс; 0 critical у GA events; 5xx < 0.5%.

DoD:
- Дашборд p95/5xx для v2 API;
- Перевірка JWT refresh-flow;
- Ендпойнти в Swagger;
- Тестове з’єднання з GA property;
- мінімум 3 е2е тести мобільного сценарію.
=======
roadmap.md
>>>>>>> 1de21f8a29728d66c5e27c2128e74dede4330889
