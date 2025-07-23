"""
Aplicación principal Flask para Mascotas App
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config.database import init_db
from routes.user_routes import user_bp
from routes.password_reset_routes import password_reset_bp
from routes.profile_routes import profile_bp
from routes.captcha_routes import captcha_bp
from api import create_api

# Importar telemetría de forma opcional
try:
    from utils.telemetry import init_telemetry
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    print("⚠️  OpenTelemetry no disponible - continuando sin telemetría")

# Cargar variables de entorno
load_dotenv()

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'mascotas_secret_key')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/mascotas-app')
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID') # Load Google Client ID
    
    # Configuración para archivos subidos
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
    
    # Configurar CORS
    CORS(
        app,
        origins=['http://localhost:5173', 'http://localhost:3000'],
        supports_credentials=True,  # Allows cookies to be sent (if you use them)
        allow_headers=['Content-Type', 'Authorization'],  # Explicitly allow Authorization header
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']  # Explicitly list allowed methods
    )
    
    # Inicializar base de datos
    init_db(app)
      # Crear carpeta de uploads si no existe
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    
    # Inicializar API Swagger
    api = create_api(app)
    
    # Registrar blueprints (rutas legadas para compatibilidad)
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(password_reset_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(captcha_bp, url_prefix='/api/captcha')
    
    # Ruta para servir archivos estáticos (imágenes subidas)
    @app.route('/static/uploads/<path:filename>')
    def uploaded_file(filename):
        """Servir archivos subidos"""
        return send_from_directory('uploads', filename)
    
    # Ruta de prueba raíz
    @app.route('/')
    def home():
        return jsonify({'message': 'Mascotas App API is running 🐾'})
    
    # Ruta de prueba para /api
    @app.route('/api')
    def api_test():
        return jsonify({'message': 'API endpoint working ✅'})
    
    # Manejador de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': f'Route not found'}), 404
    
    # Manejador de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    
    # Inicializar telemetría solo si está disponible
    if TELEMETRY_AVAILABLE:
        init_telemetry(app)
        print("📊 Telemetría inicializada")
    
    print(f'🚀 Server running on port {port}')
    print(f'📡 API available at: http://localhost:{port}/api')
    print(f'📚 Swagger UI available at: http://localhost:{port}/api/docs/')
    print(f'📋 API JSON Schema at: http://localhost:{port}/api/swagger.json')
    
    app.run(host='0.0.0.0', port=port, debug=True)
