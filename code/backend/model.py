from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    email= db.Column(db.String)
    role = db.Column(db.String, default="user")
    approved = db.Column(db.String, default="No")    
    last_login = db.Column(db.DateTime,default=datetime.utcnow, nullable=True) 
    orders = db.relationship("Order", backref="user")

    def __repr__(self):
        return f"User {self.username}, Role {self.role}"
    
class Category(db.Model):
    __tablename__='category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String)
    products = db.relationship("Product", backref="category")
    approved = db.Column(db.String, default="No")

class Product(db.Model):
    __tablename__='product'
    productID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String)
    product_category = db.Column(db.String, db.ForeignKey("category.category_name"), nullable=False)
    stock= db.Column(db.Integer)
    price= db.Column(db.Float)
    expiry_date = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Integer, db.ForeignKey('user.username'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    products = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# initial data 
admin_user = User(username="admin", password="myapp",email="admin@urbanshopper.com", role="admin", approved="Yes")
product1 = Product(product_name="Milk", product_category="Dairy", stock=20, price=27.5, expiry_date= datetime(2024, 2, 23))
product2 = Product(product_name="Apple", product_category="Fruits", stock=10, price=50, expiry_date= datetime(2024, 3, 12))
category1 = Category(category_name="Dairy", approved="Yes")
category2 = Category(category_name="Fruits",approved="Yes")