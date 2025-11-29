# 3. API Style та формат помилок

* Статус: Прийнято
* Дата: 2025-11-28

## Рішення
* Стиль: **REST Level 2** (Resources, HTTP Verbs, Status Codes).
* Формат обміну: **JSON**.
* Специфікація: **OpenAPI 3.0**.

## Формат помилки (ErrorResponse)
Всі помилки API повертаються у форматі:
```json
{
  "error": "ErrorType",
  "code": "ERROR_CODE",
  "details": ["Optional details..."]
}