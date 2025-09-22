from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

# Список продуктів
products = [
    {"id": 1, "name": "Atlas", "desc": "Гуманоїдний робот для мобільності та досліджень.", "img": "robot1.jpg"},
    {"id": 2, "name": "Spot", "desc": "Робот-собака для промислових і оборонних задач.", "img": "robot2.jpg"},
    {"id": 3, "name": "Handle", "desc": "Робот для складів та логістики.", "img": "robot3.jpg"}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/products")
def products_page():
    return render_template("products.html", products=products)

@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        abort(404)
    return render_template("product_detail.html", product=product)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("desc")
        img = request.form.get("img")
        if name and desc and img:
            new_id = max(p["id"] for p in products) + 1 if products else 1
            products.append({"id": new_id, "name": name, "desc": desc, "img": img})
        return redirect(url_for("products_page"))
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
