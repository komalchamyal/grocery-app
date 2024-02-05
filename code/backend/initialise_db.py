from main import db
db.create_all()
from model import admin_user, product1, product2, category1, category2
db.session.add(admin_user)
db.session.add(category2)
db.session.add(category1)
db.session.add(product1)
db.session.add(product2)
db.session.commit()