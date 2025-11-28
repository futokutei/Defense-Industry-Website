
## API Тести — Команди та короткий опис

### 1. Health Check — перевірка роботи API
```bash
curl http://127.0.0.1:5000/api/health
```

### 2. Отримати список продуктів (GET)
```bash
curl http://127.0.0.1:5000/api/products
```

### 3. Створити новий продукт (POST)
```bash
curl -X POST http://127.0.0.1:5000/api/products      -H "Content-Type: application/json"      -d '{"name": "New Drone X", "desc": "Super fast drone", "img": "drone.jpg"}'
```

### 4. Оновити продукт за ID (PUT)
```bash
curl -X PUT http://127.0.0.1:5000/api/products/1      -H "Content-Type: application/json"      -d '{"name": "New Drone X v2", "desc": "Updated description"}'
```

### 5. Видалити продукт за ID (DELETE)
```bash
curl -X DELETE http://127.0.0.1:5000/api/products/1
```

### 6. Перевірити, чи видалилось (GET)
```bash
curl http://127.0.0.1:5000/api/products
```
