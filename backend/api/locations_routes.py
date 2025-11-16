from flask import Blueprint, request, jsonify
from core.locations_logic import (
    get_all_locations,
    create_location,
    update_location,
    delete_location,
    get_location
)

locations_bp = Blueprint('locations_bp', __name__)

@locations_bp.route('/', methods=['GET'])
def handle_get_all_locations():
    """Restituisce tutti i luoghi."""
    locations = get_all_locations()
    return jsonify(locations)

@locations_bp.route('/<string:name>', methods=['GET'])
def handle_get_location(name):
    """Restituisce un singolo luogo."""
    location = get_location(name)
    if location:
        return jsonify(location)
    return jsonify({"error": "Location not found"}), 404

@locations_bp.route('/', methods=['POST'])
def handle_create_location():
    """Crea un nuovo luogo."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400
    
    name = data.pop('name')
    new_location, error = create_location(name, data)
    
    if error:
        return jsonify({"error": error}), 409 # Conflict
    
    return jsonify(new_location), 201

@locations_bp.route('/<string:name>', methods=['PUT'])
def handle_update_location(name):
    """Aggiorna un luogo esistente."""
    data = request.get_json()
    updated_location, error = update_location(name, data)
    
    if error:
        return jsonify({"error": error}), 404
        
    return jsonify(updated_location)

@locations_bp.route('/<string:name>', methods=['DELETE'])
def handle_delete_location(name):
    """Cancella un luogo."""
    success, error = delete_location(name)
    
    if not success:
        return jsonify({"error": error}), 404
        
    return '', 204 # No Content
