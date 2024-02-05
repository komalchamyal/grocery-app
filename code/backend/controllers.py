from flask import jsonify, request, send_file
from flask_cors import cross_origin
from model import db, User, Product, Category, Order
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
from main import app
from tasks import *
from celery.result import AsyncResult


@app.route("/downloadcsv")
def download_csv():
    job = export_csv_task.delay()

    task_result = AsyncResult(job.id)
    task_result.wait()

    if task_result.successful():
        return send_file("static/ManagerFile.csv", as_attachment=True, download_name="ManagerFile.csv")
    else:
        return {"error": "Failed to generate CSV file."}
    


########################### USER ################################

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    user= User.query.filter_by(username=username).first()
    if user:
        if email==user.email:
            if password==user.password:
                access_token = create_access_token(identity=username)
                return jsonify({"access_token":access_token, "role": user.role, "approved": user.approved, "username":username}), 200
            else: 
                return jsonify({"message": "Incorrect Password"}), 401
        else: 
            return jsonify({"message": "Incorrect Email"}), 401
    else:
        return jsonify({"message": "User not registered"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    checked = data.get('checked')
    approved="Yes"

    role="user"
    if checked==True: 
        role="manager"
        approved="No"
    user= User.query.filter_by(username=username).first()
    if user:
        return jsonify({"message": "User already exists"}), 401
    else:
        new=User(username=username,password=password, email=email,role=role, approved=approved)
        db.session.add(new)
        db.session.commit()
        access_token = create_access_token(identity=username)
        return jsonify({"access_token":access_token, "role": role, "approved": approved, "username":username}), 200

########################### CATEGORIES ################################

@app.route("/getCategories")
def get_categories():
    categories = Category.query.filter_by(approved="Yes").all()
    cat_list = [{"id":category.id,"name":category.category_name} for category in categories]
    return jsonify(cat_list), 200

@app.route("/addCategory", methods=['POST'])
def add_category():
    name = request.get_json()
        
    old= Category.query.filter_by(category_name=name).first()
    if(old):
        return jsonify({"message": "Category already exists"}), 401

    category= Category(category_name=name, approved="Yes")
    db.session.add(category)
    db.session.commit()
    return jsonify({"message": "Category successfully added."}), 200

@app.route("/editCategory", methods=['POST'])
def edit_category():
    data = request.get_json()
    name = data.get('name')
    id = data.get('id')
        
    try:
        category= Category.query.filter_by(id=id).first()
        category.category_name= name
        db.session.commit()
        return jsonify({"message": "Category successfully updated."}), 200
    except:
        return jsonify({"message": "Something went wrong."}), 400

@app.route("/deleteCategory", methods=['DELETE'])
def delete_category():
    id = request.get_json()
    print(id)
    try:
        cat= Category.query.filter_by(id=id).first()
        for product in cat.products:
            db.session.delete(product)
        db.session.delete(cat)
        db.session.commit()
        return jsonify({"message": "Category successfully deleted."}), 200
    except:
        return jsonify({"message": "Something went wrong."}), 400


@app.route("/approveCategory", methods=['POST'])
def category_approval():
    name = request.get_json()
    category= Category.query.filter_by(category_name=name).first() 
    if category:   
        category.approved="Yes"
        db.session.commit()
        return jsonify({"message": "Category Approved"}), 200
    return jsonify({"message": "Category does not exist"}), 401


@app.route("/rejectCategory", methods=['POST'])
def category_reject():
    name = request.get_json()
    category= Category.query.filter_by(category_name=name).first() 
    if category:   
        category.approved="Rejected"
        db.session.commit()
        return jsonify({"message": "Category Rejected"}), 200
    return jsonify({"message": "Category does not exist"}), 401


@app.route("/requestCategory", methods=['POST'])
def request_category():
    name = request.get_json()
    category= Category.query.filter_by(category_name=name).first() 
    if category:   
        return jsonify({"message": "Category Already Exists"}), 401
    cat = Category(category_name=name, approved="No")
    db.session.add(cat)
    db.session.commit()
    return jsonify({"message": "Category requested"}), 200

@app.route("/getCategoryRequests")
def category_requests():
    categories= Category.query.filter_by(approved="No").all() 
    cat = [{"name": category.category_name} for category in categories]
    # print(cat)
    return jsonify(cat), 200


########################### PRODUCTS ################################

@app.route("/getProducts")
def get_products():
    products = Product.query.all()
    product_list = [{'id': product.productID, 'name': product.product_name, 'category': product.product_category,'stock': product.stock,'price': product.price, 'expiry': product.expiry_date} for product in products]
    return jsonify(product_list), 200

@app.route("/addProduct", methods=['POST'])
def add_product():
    data = request.get_json()
    name = data.get('name')
    category = data.get('category')
    stock = data.get('stock')
    price = data.get('price')
    expiry = data.get('expiry')
        
    old= Product.query.filter_by(product_name=name).first()
    if(old):
        return jsonify({"message": "Product already exists"}), 401

    prod= Product(product_name=name, product_category=category, stock=stock, price=price, expiry=datetime.strptime(expiry, "%Y-%m-%d"))
    db.session.add(prod)
    db.session.commit()
    return jsonify({"message": "Product successfully added."}), 200

@app.route("/editProduct", methods=['POST'])
def edit_product():
    data = request.get_json()
    name = data.get('name')
    id = data.get('id')
    category = data.get('category')
    stock = data.get('stock')
    price = data.get('price')
    expiry = data.get('expiry')
        
    # try:
    prod= Product.query.filter_by(productID=id).first()
    prod.product_name= name
    prod.product_category=category
    prod.stock=stock
    prod.price=price
    if expiry:
        # prod.expiry_date=datetime.strptime(expiry,  "%Y-%m-%d")
        prod.expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
    db.session.commit()
    return jsonify({"message": "Product successfully updated."}), 200
    # except:
    #     return jsonify({"message": "Something went wrong."}), 400

@app.route("/deleteProduct", methods=['DELETE'])
def delete_product():
    id = request.get_json()
    try:
        prod= Product.query.filter_by(productID=id).first()
        db.session.delete(prod)
        db.session.commit()
        return jsonify({"message": "Product successfully deleted."}), 200
    except:
        return jsonify({"message": "Something went wrong."}), 400


@app.route("/buyProducts", methods=['POST'])
def buy_products():
    data = request.get_json()
    products=[]
    amount=0
    for i in range(len(data["cart"])):
        item=data["cart"][i]
        id = item.get('id')
        quantity = item.get("quantity")
        stock= item.get("stock")
        price=item.get("price")
        if quantity>stock:
            return jsonify({"message":"Stock is less"}), 401
        prod= Product.query.filter_by(productID=id).first()
        prod.stock = prod.stock - quantity
        db.session.commit()
        # print(data)
        # print(data["cart"])
        products.append(data["cart"][i]["name"])
        amount+=price*quantity
    order = Order(username=data["user"], amount=amount, products=str(products))
    db.session.add(order)
    db.session.commit()
    return jsonify({"message":"Products Bought Successfully"}), 200


########################### MANAGER REQUESTS ################################

@app.route("/getManagerRequests")
def manager_requests():
    requests= User.query.filter_by(approved="No").all()    
    req_list = [{'manager': manager.username} for manager in requests]
    return jsonify(req_list), 200

@app.route("/approveManagerRequests", methods=['POST'])
def manager_approval():
    username = request.get_json()
    user= User.query.filter_by(username=username).first() 
    if user:   
        user.approved="Yes"
        db.session.commit()
        return jsonify({"message": "Manager Approved"}), 200
    return jsonify({"message": "Manager does not exist"}), 401

@app.route("/rejectManagerRequests", methods=['POST'])
def manager_reject():
    username = request.get_json()
    user= User.query.filter_by(username=username).first() 
    if user:   
        user.approved="Rejected"
        db.session.commit()
        return jsonify({"message": "Manager Request Rejected"}), 200
    return jsonify({"message": "Manager does not exist"}), 401



@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
