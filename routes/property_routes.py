from flask import Blueprint,jsonify,render_template
from services.property_service import PropertyService

property_bp = Blueprint('property', __name__)

@property_bp.route('/api/properties',methods=['GET'])
def get_all_property():
    properties = PropertyService.get_all_property()
    return render_template('property.html',properties=properties)
