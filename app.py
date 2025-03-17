from flask import Flask, request, jsonify
from flask_cors import CORS
from config import configure_app, db
from flasgger import Swagger, swag_from
from models import Item 

app = Flask(__name__)

configure_app(app)

CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"]
}}, supports_credentials=True)

swagger = Swagger(app)

with app.app_context():
    db.create_all()

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/items', methods=['POST'])
@swag_from({
    'tags': ['Items'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'}
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        201: {'description': 'Item created'},
        400: {'description': 'Invalid input'}
    }
})
def create_item():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    item = Item(name=data['name'], description=data.get('description', ''))
    db.session.add(item)
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name, 'description': item.description}), 201

@app.route('/items', methods=['GET'])
@swag_from({
    'tags': ['Items'],
    'responses': {
        200: {
            'description': 'List of items',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'description': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_items():
    items = Item.query.all()
    result = [{'id': item.id, 'name': item.name, 'description': item.description} for item in items]
    return jsonify(result), 200

@app.route('/items/<int:item_id>', methods=['GET'])
@swag_from({
    'tags': ['Items'],
    'parameters': [
        {
            'name': 'item_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the item'
        }
    ],
    'responses': {
        200: {
            'description': 'Item details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'description': {'type': 'string'}
                }
            }
        },
        404: {'description': 'Item not found'}
    }
})
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify({'id': item.id, 'name': item.name, 'description': item.description}), 200

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name, 'description': item.description}), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Items'],
    'parameters': [
        {
            'name': 'item_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the item'
        }
    ],
    'responses': {
        200: {'description': 'Item deleted'},
        404: {'description': 'Item not found'}
    }
})
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
