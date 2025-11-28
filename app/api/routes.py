from flask import jsonify, request
from app.api import api
from app.services.product_service import ProductService

# Ініціалізація сервісу (шар бізнес-логіки)
product_service = ProductService()

# --- DTO Helpers (Конвертація даних) ---
def product_to_dto(product):
    """Перетворює об'єкт бази даних у словник (JSON)"""
    return {
        "id": product.id,
        "name": product.name,
        "desc": product.desc,
        "img": product.img
    }

def error_response(error, code, details=None, status=400):
    """Універсальна функція для повернення помилок"""
    response = {
        "error": error,
        "code": code,
        "details": details or []
    }
    return jsonify(response), status

# --- Endpoints (Маршрути) ---

@api.route('/health', methods=['GET'])
def health_check():
    """Перевірка стану сервера"""
    return jsonify({"status": "ok"}), 200

@api.route('/products', methods=['GET'])
def get_products():
    """Отримати список всіх продуктів"""
    products = product_service.get_all()
    # Конвертуємо кожен об'єкт у JSON
    return jsonify([product_to_dto(p) for p in products]), 200

@api.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """Отримати один продукт по ID"""
    product = product_service.get_by_id(id)
    if not product:
        return error_response("Not Found", "PRODUCT_NOT_FOUND", status=404)
    return jsonify(product_to_dto(product)), 200

@api.route('/products', methods=['POST'])
def create_product():
    """Створити новий продукт"""
    data = request.get_json()
    
    # Валідація: перевіряємо наявність обов'язкових полів
    if not data or 'name' not in data or 'desc' not in data:
        return error_response("Validation Error", "MISSING_FIELDS", ["name and desc are required"], 400)
    
    new_product = product_service.create(data)
    # Повертаємо код 201 (Created)
    return jsonify(product_to_dto(new_product)), 201

@api.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    """Оновити існуючий продукт"""
    data = request.get_json()
    updated_product = product_service.update(id, data)
    
    if not updated_product:
        return error_response("Not Found", "PRODUCT_NOT_FOUND", status=404)
        
    return jsonify(product_to_dto(updated_product)), 200

@api.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Видалити продукт"""
    success = product_service.delete(id)
    if not success:
        return error_response("Not Found", "PRODUCT_NOT_FOUND", status=404)
    # Повертаємо 204 No Content (успіх, але без тіла відповіді)
    return '', 204