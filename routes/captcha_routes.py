"""
Rutas para manejo de CAPTCHA
"""
from flask import Blueprint, request, jsonify
from services.captcha_service import captcha_service, recaptcha_service

# Crear blueprint para rutas de CAPTCHA
captcha_bp = Blueprint('captcha', __name__)

@captcha_bp.route('/', methods=['GET'])
def test_captcha_route():
    """Ruta de prueba para CAPTCHA"""
    return jsonify({'message': 'CAPTCHA routes working'})

@captcha_bp.route('/generate', methods=['POST'])
def generate_captcha():
    """
    Generar un nuevo CAPTCHA
    
    Body (opcional):
    {
        "type": "math" | "text"  // Por defecto "math"
    }
    """
    try:
        request_data = request.get_json() or {}
        captcha_type = request_data.get('type', 'math')
        
        if captcha_type == 'text':
            captcha_data = captcha_service.generate_text_captcha()
        else:
            captcha_data = captcha_service.generate_math_captcha()
        
        return jsonify({
            'success': True,
            'captcha': captcha_data
        }), 200
        
    except Exception as e:
        print(f"Error generando CAPTCHA: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error generando CAPTCHA',
            'error': str(e)
        }), 500

@captcha_bp.route('/validate', methods=['POST'])
def validate_captcha():
    """
    Validar respuesta de CAPTCHA
    
    Body:
    {
        "captcha_id": "string",
        "answer": "string"
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron datos'
            }), 400
        
        captcha_id = request_data.get('captcha_id')
        answer = request_data.get('answer')
        
        if not captcha_id or not answer:
            return jsonify({
                'success': False,
                'message': 'captcha_id y answer son requeridos'
            }), 400
        
        is_valid = captcha_service.validate_captcha(captcha_id, answer)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': 'CAPTCHA válido' if is_valid else 'CAPTCHA inválido'
        }), 200
        
    except Exception as e:
        print(f"Error validando CAPTCHA: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error validando CAPTCHA',
            'error': str(e)
        }), 500

@captcha_bp.route('/recaptcha/verify', methods=['POST'])
def verify_recaptcha():
    """
    Verificar reCAPTCHA de Google
    
    Body:
    {
        "recaptcha_response": "string"
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'success': False,
                'message': 'No se enviaron datos'
            }), 400
        
        recaptcha_response = request_data.get('recaptcha_response')
        
        if not recaptcha_response:
            return jsonify({
                'success': False,
                'message': 'recaptcha_response es requerido'
            }), 400
        
        # Obtener IP del usuario
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # Verificar con Google
        verification_result = recaptcha_service.verify_recaptcha(recaptcha_response, user_ip)
        
        return jsonify({
            'success': True,
            'verification': verification_result
        }), 200
        
    except Exception as e:
        print(f"Error verificando reCAPTCHA: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error verificando reCAPTCHA',
            'error': str(e)
        }), 500

@captcha_bp.route('/recaptcha/site-key', methods=['GET'])
def get_recaptcha_site_key():
    """
    Obtener la clave del sitio de reCAPTCHA para el frontend
    """
    try:
        site_key = recaptcha_service.get_site_key()
        
        if not site_key:
            return jsonify({
                'success': False,
                'message': 'reCAPTCHA no configurado'
            }), 404
        
        return jsonify({
            'success': True,
            'site_key': site_key
        }), 200
        
    except Exception as e:
        print(f"Error obteniendo clave de reCAPTCHA: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error obteniendo configuración',
            'error': str(e)
        }), 500

@captcha_bp.route('/cleanup', methods=['POST'])
def cleanup_expired():
    """
    Limpiar CAPTCHAs expirados (endpoint administrativo)
    """
    try:
        captcha_service.cleanup_expired_captchas()
        
        return jsonify({
            'success': True,
            'message': 'CAPTCHAs expirados limpiados'
        }), 200
        
    except Exception as e:
        print(f"Error limpiando CAPTCHAs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error limpiando CAPTCHAs',
            'error': str(e)
        }), 500
