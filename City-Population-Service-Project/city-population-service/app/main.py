from flask import Blueprint, jsonify, request
from app.db import es_client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return "OK", 200

@main_bp.route('/city', methods=['PUT', 'POST'])
def upsert_city():
    """Insert or update a city's population"""
    data = request.get_json()
    
    # Validate request data
    if not data or 'name' not in data or 'population' not in data:
        return jsonify({'error': 'Missing required fields: name and population'}), 400
    
    city_name = data['name']
    
    # Ensure population is an integer
    try:
        population = int(data['population'])
        if population < 0:
            return jsonify({'error': 'Population must be a non-negative integer'}), 400
    except ValueError:
        return jsonify({'error': 'Population must be a valid integer'}), 400
    
    # Upsert city data
    if es_client.upsert_city(city_name, population):
        return jsonify({
            'success': True,
            'message': f'City {city_name} updated with population {population}'
        }), 200
    else:
        return jsonify({'error': 'Failed to update city data'}), 500

@main_bp.route('/city/<name>', methods=['GET'])
def get_city(name):
    """Get a city's population"""
    population = es_client.get_city_population(name)
    
    if population is not None:
        return jsonify({
            'name': name,
            'population': population
        }), 200
    else:
        return jsonify({'error': f'City {name} not found'}), 404

@main_bp.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500