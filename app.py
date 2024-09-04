from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_cors import CORS
import os




app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    barcode = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), unique=False)
    color = db.Column(db.String(50), unique=False)
    size = db.Column(db.String(50), unique=False)
    count = db.Column(db.Integer, unique=False)
    gender = db.Column(db.String(50), unique=False)
    logo = db.Column(db.String(5), unique=False)



    def __init__(self,barcode,name,color, size ,count, gender, logo ):
        
        self.barcode = barcode
        self.name = name
        self.color = color
        self.size = size
        self.count = count
        self.gender = gender
        self.logo = logo
        



class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id','barcode','name', 'color','size', 'count', 'gender', 'logo')


item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

@app.route("/Items", methods=["GET"])
def get_items():
    all_specs = Item.query.all()
    result = items_schema.dump(all_specs)
    return jsonify(result)


# @app.route("/Item/<id>", methods=["GET"])
# def get_item(id):
#     item = Item.query.get(id)
#     return item_schema.jsonify(item)

@app.route("/Item/<barcode>", methods=["GET"])
def get_item(barcode):
    # Query the item by barcode
    item = Item.query.filter_by(barcode=barcode).first()
    
    # Check if item exists
    if item is None:
        return {"error": "Item not found"}, 404

    return item_schema.jsonify(item)





@app.route("/Item", methods=["POST"])
def add_item():
    barcode = request.json['barcode']
    name = request.json['name']
    color = request.json['color']
    size = request.json['size']
    count = request.json['count']
    gender = request.json['gender']
    logo = request.json['logo']

    new_item = Item(barcode=barcode, name=name, color=color, size=size, count=count, gender=gender, logo=logo)

    db.session.add(new_item)
    db.session.commit()

    item = Item.query.get(new_item.id)

    return item_schema.jsonify(item)

@app.route("/Item/<barcode>", methods=["PUT"])
def specs_update(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    data = request.get_json()
    

    item.barcode = data.get('barcode', item.barcode)
    item.name = data.get('name', item.name)
    item.color = data.get('color', item.color)
    item.size = data.get('size', item.size)
    item.count = data.get('count', item.count)
    item.gender = data.get('gender', item.gender)
    item.logo = data.get('logo', item.logo)

    db.session.commit()
    return item_schema.jsonify(item)

@app.route('/Item/<barcode>', methods=['DELETE'])
def item_delete(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)