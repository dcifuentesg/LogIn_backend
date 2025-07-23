"""
Controlador para manejo de usuarios
"""
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from flask import current_app, jsonify
from models.user import User
from services.user_creation_validation import create_user_validation_chain
from services.captcha_service import captcha_service, recaptcha_service

class UserController:
    """Controlador para operaciones de usuario"""
    
    @staticmethod
    async def register_user(request_data):
        """Registrar un nuevo usuario"""
        try:
            # Obtener datos del request
            full_name = request_data.get('full_name', '').strip() # Cambiado a full_name
            email = request_data.get('email', '').strip()
            password = request_data.get('password', '')
            
            print(f'📝 Datos recibidos para registro: full_name={full_name}, email={email}, password=***')
            
            # Crear cadena de validación
            validation_chain = create_user_validation_chain()
            
            # Variable para capturar la respuesta de validación
            validation_response = {'sent': False, 'data': None, 'status': None}
            
            def response_handler(data, status_code):
                """Handler para capturar respuestas de validación"""
                validation_response['sent'] = True
                validation_response['data'] = data
                validation_response['status'] = status_code
            
            # Ejecutar validaciones
            validation_passed = await validation_chain.handle(request_data, response_handler)
            
            # Si las validaciones fallaron, retornar el error
            if not validation_passed or validation_response['sent']:
                print('❌ Validaciones fallaron')
                return validation_response['data'], validation_response['status']
            
            print('✅ Validaciones pasaron, creando usuario...')
            
            # Hashear la contraseña
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            # Crear el usuario
            user = User(
                full_name=full_name, # Usar full_name
                email=email,
                password=hashed_password
            )
            
            user_id = user.save()
            print(f'✅ Usuario creado: {user_id}')
            
            # Responder con el usuario creado (sin la contraseña)
            return user.to_dict(), 201
            
        except ValueError as e:
            print(f'❌ Error de validación: {e}')
            return {'message': str(e)}, 400
        except Exception as e:
            print(f'❌ Error en register_user: {e}')
            return {
                'message': 'Error al registrar usuario',
                'error': str(e)
            }, 500
    
    @staticmethod
    def login_user(request_data):
        """Iniciar sesión de usuario con validación CAPTCHA"""
        try:
            email = request_data.get('email', '').strip()
            password = request_data.get('password', '')
            captcha_id = request_data.get('captcha_id')
            captcha_answer = request_data.get('captcha_answer')
            recaptcha_response = request_data.get('recaptcha_response')
            
            print(f'🔐 Intento de login para: {email}')
            
            # Validar que todos los campos básicos estén presentes
            if not email or not password:
                return {'message': 'Email y contraseña son obligatorios'}, 400
            
            # Validar CAPTCHA (priorizar reCAPTCHA si está presente)
            captcha_valid = False
            captcha_error = None
            
            if recaptcha_response:
                # Validar reCAPTCHA de Google
                print('🤖 Validando reCAPTCHA...')
                verification_result = recaptcha_service.verify_recaptcha(recaptcha_response)
                
                if verification_result['success']:
                    # Para reCAPTCHA v3, verificar score si está disponible
                    score = verification_result.get('score', 1.0)
                    if score >= 0.5:  # Umbral de confianza
                        captcha_valid = True
                        print(f'✅ reCAPTCHA válido (score: {score})')
                    else:
                        captcha_error = f'Score de reCAPTCHA muy bajo: {score}'
                        print(f'❌ reCAPTCHA score bajo: {score}')
                else:
                    captcha_error = verification_result.get('error', 'reCAPTCHA inválido')
                    errors = verification_result.get('errors', [])
                    if errors:
                        captcha_error += f' ({", ".join(errors)})'
                    print(f'❌ reCAPTCHA inválido: {captcha_error}')
            
            elif captcha_id and captcha_answer:
                # Validar CAPTCHA propio
                print('🧮 Validando CAPTCHA matemático...')
                captcha_valid = captcha_service.validate_captcha(captcha_id, captcha_answer)
                if captcha_valid:
                    print('✅ CAPTCHA matemático válido')
                else:
                    captcha_error = 'CAPTCHA inválido o expirado'
                    print('❌ CAPTCHA matemático inválido')
            
            else:
                captcha_error = 'CAPTCHA requerido. Proporciona recaptcha_response o captcha_id/captcha_answer'
                print('❌ No se proporcionó CAPTCHA')
            
            # Si el CAPTCHA no es válido, retornar error
            if not captcha_valid:
                return {
                    'message': captcha_error or 'CAPTCHA inválido',
                    'captcha_required': True
                }, 400
            
            # Buscar el usuario por email
            user = User.find_by_email(email)
            print(f'🔍 Usuario encontrado: {"Sí" if user else "No"}')
            
            if not user:
                return {'message': 'Credenciales inválidas'}, 400
            
            # Verificar la contraseña
            password_bytes = password.encode('utf-8')
            stored_password_bytes = user.password.encode('utf-8')
            is_match = bcrypt.checkpw(password_bytes, stored_password_bytes)
            print(f'🔐 Contraseña válida: {"Sí" if is_match else "No"}')
            
            if not is_match:
                return {'message': 'Credenciales inválidas'}, 400
            
            # Crear el token JWT
            secret_key = os.getenv('JWT_SECRET', 'mascotas_secret_key')
            payload = {
                'sub': str(user._id),
                'userId': str(user._id),
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            
            print(f'✅ Login exitoso para: {email}')
            
            return {
                'message': 'Login exitoso',
                'token': token,
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            print(f'❌ Error en login_user: {e}')
            return {
                'message': 'Error al iniciar sesión',
                'error': str(e)
            }, 500
