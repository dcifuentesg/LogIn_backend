# 🔐 Guía Completa de Características de Seguridad

## 📋 Índice

1. [Autenticación JWT](#autenticación-jwt)
2. [Autenticación Google OAuth2](#autenticación-google-oauth2)
3. [Restablecimiento de Contraseñas](#restablecimiento-de-contraseñas)
4. [Encriptación bcrypt](#encriptación-bcrypt)
5. [Rate Limiting](#rate-limiting)
6. [Implementación Paso a Paso](#implementación-paso-a-paso)

---

## 🎯 Autenticación JWT

### ¿Qué es JWT?
JSON Web Token (JWT) es un estándar abierto que define una forma compacta y auto-contenida para transmitir información de forma segura entre partes como un objeto JSON.

### ¿Cómo funciona en nuestro sistema?

#### 1. Estructura del Token
```python
# models/user.py - Generación de JWT
import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt_token(self):
    """Generar token JWT para el usuario"""
    payload = {
        'userId': str(self._id),
        'email': self.email,
        'full_name': self.full_name,
        'iat': datetime.utcnow(),  # Issued at
        'exp': datetime.utcnow() + timedelta(days=30)  # Expira en 30 días
    }
    
    secret_key = current_app.config['SECRET_KEY']
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token
```

#### 2. Validación del Token
```python
# utils/jwt_validator.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app

def token_required(f):
    """Decorador para validar JWT en rutas protegidas"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Formato: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token faltante'}), 401
        
        try:
            # Decodificar y validar token
            secret_key = current_app.config['SECRET_KEY']
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user_id = payload['userId']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        # Pasar user_id a la función protegida
        return f(current_user_id, *args, **kwargs)
    
    return decorated
```

#### 3. Uso en Controladores
```python
# controllers/auth_controller.py
class AuthController:
    @staticmethod
    def login(data):
        """Login de usuario y generación de JWT"""
        try:
            email = data.get('email')
            password = data.get('password')
            
            # Buscar usuario
            user = User.find_by_email(email)
            if not user:
                return {'message': 'Usuario no encontrado'}, 404
            
            # Verificar contraseña
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return {'message': 'Credenciales incorrectas'}, 401
            
            # Generar JWT
            token = user.generate_jwt_token()
            
            return {
                'message': 'Login exitoso',
                'token': token,
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            return {'message': f'Error en login: {str(e)}'}, 500
```

### Ventajas del JWT:
- ✅ **Stateless**: No requiere almacenamiento en servidor
- ✅ **Escalable**: Funciona en sistemas distribuidos
- ✅ **Seguro**: Firmado digitalmente
- ✅ **Flexible**: Incluye información del usuario

---

## 🔑 Autenticación Google OAuth2

### ¿Cómo funciona Google Sign-In?

#### 1. Configuración del Cliente
```python
# app.py - Configuración
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
```

#### 2. Validación del Token de Google
```python
# controllers/auth_controller.py
@staticmethod
def google_login(data):
    """Login/registro con Google ID Token"""
    try:
        google_id_token = data.get('google_id_token')
        
        if not google_id_token:
            return {'message': 'Token de Google requerido'}, 400
        
        # Verificar token con Google
        try:
            client_id = current_app.config['GOOGLE_CLIENT_ID']
            idinfo = id_token.verify_oauth2_token(
                google_id_token, 
                google_requests.Request(), 
                client_id
            )
            
            # Extraer información del usuario
            user_email = idinfo['email']
            user_full_name = idinfo['name']
            google_user_id = idinfo['sub']
            
        except ValueError as e:
            return {'message': 'Token de Google inválido'}, 401
        
        # Buscar usuario existente
        user = User.find_by_email(user_email)
        
        if not user:
            # Crear nuevo usuario
            placeholder_password = bcrypt.hashpw(
                (user_email + current_app.config['SECRET_KEY']).encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            new_user = User(
                full_name=user_full_name,
                email=user_email,
                password=placeholder_password,
                google_id=google_user_id
            )
            new_user.save()
            user = new_user
        
        # Generar JWT
        token = user.generate_jwt_token()
        
        return {
            'message': 'Login con Google exitoso',
            'token': token,
            'user': user.to_dict()
        }, 200
        
    except Exception as e:
        return {'message': f'Error en Google login: {str(e)}'}, 500
```

#### 3. Frontend Integration
```javascript
// Ejemplo de integración en frontend
// 1. Configurar Google Sign-In
function initGoogleSignIn() {
    google.accounts.id.initialize({
        client_id: 'TU_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
        callback: handleGoogleResponse
    });
}

// 2. Manejar respuesta de Google
async function handleGoogleResponse(response) {
    try {
        const result = await fetch('/api/auth/google_login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                google_id_token: response.credential
            })
        });
        
        const data = await result.json();
        
        if (result.ok) {
            // Guardar token JWT
            localStorage.setItem('authToken', data.token);
            console.log('Login exitoso:', data.user);
        }
    } catch (error) {
        console.error('Error en Google login:', error);
    }
}
```

---

## 🔄 Restablecimiento de Contraseñas

### Flujo Completo del Sistema

#### 1. Modelo de Token de Restablecimiento
```python
# models/password_reset_token.py
from datetime import datetime, timedelta
import secrets
from config.database import get_database

class PasswordResetToken:
    def __init__(self, user_id, token=None, expires_at=None):
        self.user_id = user_id
        self.token = token or secrets.token_urlsafe(32)  # Token seguro
        self.expires_at = expires_at or datetime.utcnow() + timedelta(hours=1)
        self.created_at = datetime.utcnow()
        self.used = False
    
    def save(self):
        """Guardar token en la base de datos"""
        db = get_database()
        collection = db.password_reset_tokens
        
        # Invalidar tokens anteriores del usuario
        collection.update_many(
            {'user_id': self.user_id, 'used': False},
            {'$set': {'used': True}}
        )
        
        # Insertar nuevo token
        collection.insert_one(self.to_dict())
    
    def is_valid(self):
        """Verificar si el token es válido"""
        return (
            not self.used and 
            datetime.utcnow() < self.expires_at
        )
    
    @staticmethod
    def find_by_token(token):
        """Buscar token por valor"""
        db = get_database()
        collection = db.password_reset_tokens
        
        token_data = collection.find_one({'token': token})
        if token_data:
            return PasswordResetToken(
                user_id=token_data['user_id'],
                token=token_data['token'],
                expires_at=token_data['expires_at']
            )
        return None
```

#### 2. Controlador de Restablecimiento
```python
# controllers/password_reset_controller.py
class PasswordResetController:
    @staticmethod
    def request_password_reset(data):
        """Solicitar restablecimiento de contraseña"""
        try:
            email = data.get('email')
            
            if not email:
                return {'message': 'Email requerido'}, 400
            
            # Buscar usuario
            user = User.find_by_email(email)
            if not user:
                # Por seguridad, no revelar si el email existe
                return {'message': 'Si el email existe, recibirás un enlace'}, 200
            
            # Generar token
            reset_token = PasswordResetToken(user_id=str(user._id))
            reset_token.save()
            
            # Enviar email (simulado)
            email_sent = EmailService.send_password_reset_email(
                email, 
                reset_token.token
            )
            
            if email_sent:
                return {'message': 'Email de restablecimiento enviado'}, 200
            else:
                return {'message': 'Error enviando email'}, 500
                
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500
    
    @staticmethod
    def verify_reset_token(data):
        """Verificar validez del token"""
        try:
            token = data.get('token')
            
            if not token:
                return {'message': 'Token requerido'}, 400
            
            reset_token = PasswordResetToken.find_by_token(token)
            
            if not reset_token or not reset_token.is_valid():
                return {'message': 'Token inválido o expirado'}, 400
            
            return {'message': 'Token válido'}, 200
            
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500
    
    @staticmethod
    def reset_password(data):
        """Restablecer contraseña con token"""
        try:
            token = data.get('token')
            new_password = data.get('password')
            
            if not token or not new_password:
                return {'message': 'Token y contraseña requeridos'}, 400
            
            # Validar token
            reset_token = PasswordResetToken.find_by_token(token)
            if not reset_token or not reset_token.is_valid():
                return {'message': 'Token inválido o expirado'}, 400
            
            # Validar contraseña
            if len(new_password) < 8:
                return {'message': 'Contraseña debe tener al menos 8 caracteres'}, 400
            
            # Buscar usuario
            user = User.find_by_id(reset_token.user_id)
            if not user:
                return {'message': 'Usuario no encontrado'}, 404
            
            # Actualizar contraseña
            hashed_password = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            user.password = hashed_password
            user.save()
            
            # Marcar token como usado
            reset_token.mark_as_used()
            
            return {'message': 'Contraseña restablecida exitosamente'}, 200
            
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500
```

#### 3. Servicio de Email
```python
# services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    @staticmethod
    def send_password_reset_email(user_email, token):
        """Enviar email de restablecimiento de contraseña"""
        try:
            # Configuración SMTP
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = user_email
            msg['Subject'] = 'Restablecimiento de Contraseña - Mascotas App'
            
            # Cuerpo del email
            reset_url = f"http://localhost:3000/reset-password?token={token}"
            body = f"""
            Hola,
            
            Has solicitado restablecer tu contraseña en Mascotas App.
            
            Haz clic en el siguiente enlace para continuar:
            {reset_url}
            
            Este enlace expira en 1 hora.
            
            Si no solicitaste este cambio, ignora este email.
            
            Saludos,
            Equipo Mascotas App
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, user_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False
```

---

## 🤖 Sistema CAPTCHA

### ¿Por qué usar CAPTCHA?
El CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart) es una medida de seguridad que:
- **Previene ataques de fuerza bruta** automatizados
- **Reduce el spam** y registros falsos
- **Protege contra bots maliciosos**
- **Mejora la seguridad general** del sistema de autenticación

### Tipos de CAPTCHA Implementados

#### 1. CAPTCHA Matemático Simple
```python
# services/captcha_service.py - CAPTCHA Matemático
class CaptchaService:
    def generate_math_captcha(self) -> Dict[str, str]:
        """Genera un CAPTCHA con operación matemática simple"""
        try:
            # Generar operación matemática
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            operation = random.choice(['+', '-', '*'])
            
            if operation == '+':
                answer = num1 + num2
                question = f"{num1} + {num2}"
            elif operation == '-':
                if num1 < num2:
                    num1, num2 = num2, num1
                answer = num1 - num2
                question = f"{num1} - {num2}"
            else:  # multiplication
                num1 = random.randint(1, 10)
                num2 = random.randint(1, 10)
                answer = num1 * num2
                question = f"{num1} × {num2}"
            
            # Generar ID único
            captcha_id = self._generate_captcha_id()
            
            # Crear imagen del CAPTCHA
            captcha_image = self._create_captcha_image(question)
            
            # Almacenar respuesta con expiración
            self.captcha_storage[captcha_id] = {
                'answer': str(answer),
                'created_at': time.time(),
                'attempts': 0
            }
            
            return {
                'captcha_id': captcha_id,
                'question': question,
                'image': captcha_image
            }
            
        except Exception as e:
            print(f"Error generando CAPTCHA: {str(e)}")
            return self._generate_fallback_captcha()
```

#### 2. CAPTCHA de Texto Aleatorio
```python
def generate_text_captcha(self) -> Dict[str, str]:
    """Genera un CAPTCHA con texto aleatorio"""
    try:
        # Generar texto (evitando caracteres confusos)
        chars = 'ABCDEFGHIJKLMNPQRSTUVWXYZ23456789'  # Sin O, 0, 1, I
        captcha_text = ''.join(random.choices(chars, k=6))
        
        captcha_id = self._generate_captcha_id()
        captcha_image = self._create_text_captcha_image(captcha_text)
        
        self.captcha_storage[captcha_id] = {
            'answer': captcha_text.upper(),
            'created_at': time.time(),
            'attempts': 0
        }
        
        return {
            'captcha_id': captcha_id,
            'image': captcha_image
        }
        
    except Exception as e:
        return self._generate_fallback_captcha()
```

#### 3. Google reCAPTCHA
```python
# services/captcha_service.py - reCAPTCHA Integration
class RecaptchaService:
    def verify_recaptcha(self, recaptcha_response: str, user_ip: str = None):
        """Verifica el token de reCAPTCHA con Google"""
        try:
            data = {
                'secret': self.recaptcha_secret,
                'response': recaptcha_response
            }
            
            if user_ip:
                data['remoteip'] = user_ip
            
            response = requests.post(self.verify_url, data=data, timeout=10)
            result = response.json()
            
            return {
                'success': result.get('success', False),
                'score': result.get('score', 0),  # Para reCAPTCHA v3
                'action': result.get('action', ''),
                'errors': result.get('error-codes', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Error interno verificando CAPTCHA'
            }
```

### Integración con el Sistema de Login

#### 1. Controlador Actualizado
```python
# controllers/user_controller.py - Login con CAPTCHA
@staticmethod
def login_user(request_data):
    """Login con validación CAPTCHA obligatoria"""
    try:
        email = request_data.get('email', '').strip()
        password = request_data.get('password', '')
        captcha_id = request_data.get('captcha_id')
        captcha_answer = request_data.get('captcha_answer')
        recaptcha_response = request_data.get('recaptcha_response')
        
        # Validar campos básicos
        if not email or not password:
            return {'message': 'Email y contraseña son obligatorios'}, 400
        
        # Validar CAPTCHA (priorizar reCAPTCHA si está presente)
        captcha_valid = False
        
        if recaptcha_response:
            # Validar reCAPTCHA de Google
            verification_result = recaptcha_service.verify_recaptcha(recaptcha_response)
            
            if verification_result['success']:
                score = verification_result.get('score', 1.0)
                if score >= 0.5:  # Umbral de confianza
                    captcha_valid = True
                    
        elif captcha_id and captcha_answer:
            # Validar CAPTCHA propio
            captcha_valid = captcha_service.validate_captcha(captcha_id, captcha_answer)
        
        # Si no es válido, retornar error
        if not captcha_valid:
            return {
                'message': 'CAPTCHA requerido y debe ser válido',
                'captcha_required': True
            }, 400
        
        # Continuar con validación de usuario y contraseña...
        user = User.find_by_email(email)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return {'message': 'Credenciales inválidas'}, 400
        
        # Generar JWT si todo es correcto
        token = user.generate_jwt_token()
        
        return {
            'message': 'Login exitoso',
            'token': token,
            'user': user.to_dict()
        }, 200
        
    except Exception as e:
        return {
            'message': 'Error al iniciar sesión',
            'error': str(e)
        }, 500
```

### Endpoints de API

#### 1. Generar CAPTCHA
```http
POST /api/captcha/generate
Content-Type: application/json

{
    "type": "math" | "text"  // opcional, por defecto "math"
}
```

**Respuesta:**
```json
{
    "success": true,
    "captcha": {
        "captcha_id": "abc123def456...",
        "question": "15 + 7",  // solo para tipo math
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    }
}
```

#### 2. Validar CAPTCHA
```http
POST /api/captcha/validate
Content-Type: application/json

{
    "captcha_id": "abc123def456...",
    "answer": "22"
}
```

**Respuesta:**
```json
{
    "success": true,
    "valid": true,
    "message": "CAPTCHA válido"
}
```

#### 3. Login con CAPTCHA
```http
POST /api/users/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "captcha_id": "abc123def456...",
    "captcha_answer": "22"
}
```

**O con reCAPTCHA:**
```http
POST /api/users/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "recaptcha_response": "03AGdBq27..."
}
```

### Frontend Integration

#### HTML Básico
```html
<!-- CAPTCHA Matemático -->
<div class="captcha-container">
    <img id="captcha-image" src="" alt="CAPTCHA" onclick="generateNewCaptcha()">
    <input type="text" id="captcha-answer" placeholder="Respuesta del CAPTCHA" required>
    <button type="button" onclick="generateNewCaptcha()">🔄 Nuevo</button>
</div>

<!-- reCAPTCHA -->
<div class="g-recaptcha" data-sitekey="TU_SITE_KEY_AQUI"></div>
```

#### JavaScript
```javascript
// Generar CAPTCHA
async function generateNewCaptcha() {
    try {
        const response = await fetch('/api/captcha/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'math' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('captcha-image').src = data.captcha.image;
            localStorage.setItem('captcha_id', data.captcha.captcha_id);
            document.getElementById('captcha-answer').value = '';
        }
    } catch (error) {
        console.error('Error generando CAPTCHA:', error);
    }
}

// Login con CAPTCHA
async function loginWithCaptcha(email, password) {
    const captchaId = localStorage.getItem('captcha_id');
    const captchaAnswer = document.getElementById('captcha-answer').value;
    
    try {
        const response = await fetch('/api/users/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                password,
                captcha_id: captchaId,
                captcha_answer: captchaAnswer
            })
        });
        
        const data = await response.json();
        
        if (data.token) {
            localStorage.setItem('authToken', data.token);
            window.location.href = '/dashboard';
        } else {
            alert(data.message);
            if (data.captcha_required) {
                generateNewCaptcha();
            }
        }
    } catch (error) {
        console.error('Error en login:', error);
        generateNewCaptcha();
    }
}
```

### Configuración y Despliegue

#### Variables de Entorno
```env
# .env - Configuración CAPTCHA
# reCAPTCHA (opcional)
RECAPTCHA_SITE_KEY=tu_site_key_aqui
RECAPTCHA_SECRET_KEY=tu_secret_key_aqui
```

#### Instalación de Dependencias
```bash
pip install Pillow  # Para generación de imágenes
```

### Características de Seguridad

#### ✅ Medidas de Seguridad Implementadas
- **Expiración automática**: CAPTCHAs expiran en 5 minutos
- **Límite de intentos**: Máximo 3 intentos por CAPTCHA
- **Imágenes con ruido**: Distorsión para prevenir OCR automático
- **IDs únicos**: Cada CAPTCHA tiene un identificador único
- **Limpieza automática**: Eliminación de CAPTCHAs expirados
- **Fallback robusto**: Sistema alternativo en caso de errores

#### 🔒 Validaciones
- **Entrada sanitizada**: Limpieza de respuestas de usuario
- **Verificación temporal**: Control de tiempo de expiración
- **Rate limiting**: Integración con sistema de límites
- **Logging**: Registro de intentos fallidos

### Testing

#### Test Básico
```bash
# Ejecutar tests de CAPTCHA
python -m pytest tests/test_captcha.py -v
```

#### Test Manual
```bash
# Ejecutar test básico integrado
python tests/test_captcha.py
```

---

## 🔒 Encriptación bcrypt

### ¿Por qué bcrypt?
- **Resistente a ataques de fuerza bruta**
- **Salt automático** para prevenir rainbow tables
- **Costo adaptativo** - se puede ajustar la dificultad

#### 1. Hashing de Contraseñas
```python
# models/user.py
import bcrypt

class User:
    def __init__(self, full_name, email, password, **kwargs):
        self.full_name = full_name
        self.email = email
        # Hash automático de la contraseña
        self.password = self._hash_password(password)
        # ... otros campos
    
    def _hash_password(self, password):
        """Hash seguro de contraseña con bcrypt"""
        # Generar salt y hash
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = buena seguridad
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password):
        """Verificar contraseña contra hash almacenado"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password.encode('utf-8')
        )
    
    def update_password(self, new_password):
        """Actualizar contraseña con nuevo hash"""
        self.password = self._hash_password(new_password)
        self.save()
```

#### 2. Validación en Login
```python
# controllers/auth_controller.py
@staticmethod
def login(data):
    """Validación segura de login"""
    try:
        email = data.get('email')
        password = data.get('password')
        
        # Buscar usuario
        user = User.find_by_email(email)
        if not user:
            return {'message': 'Credenciales incorrectas'}, 401
        
        # Verificar contraseña con bcrypt
        if not user.verify_password(password):
            return {'message': 'Credenciales incorrectas'}, 401
        
        # Login exitoso
        token = user.generate_jwt_token()
        return {
            'message': 'Login exitoso',
            'token': token,
            'user': user.to_dict()
        }, 200
        
    except Exception as e:
        return {'message': 'Error interno'}, 500
```

#### 3. Cambio de Contraseña
```python
# controllers/profile_controller.py
@staticmethod
def change_password(user_id, data):
    """Cambiar contraseña del usuario"""
    try:
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return {'message': 'Contraseñas requeridas'}, 400
        
        # Buscar usuario
        user = User.find_by_id(user_id)
        if not user:
            return {'message': 'Usuario no encontrado'}, 404
        
        # Verificar contraseña actual
        if not user.verify_password(current_password):
            return {'message': 'Contraseña actual incorrecta'}, 400
        
        # Validar nueva contraseña
        if len(new_password) < 8:
            return {'message': 'Nueva contraseña muy débil'}, 400
        
        # Actualizar contraseña
        user.update_password(new_password)
        
        return {'message': 'Contraseña actualizada exitosamente'}, 200
        
    except Exception as e:
        return {'message': f'Error: {str(e)}'}, 500
```

---

## ⏱️ Rate Limiting

### Protección contra Abuso y Spam

#### 1. Configuración de Rate Limiting
```python
# routes/profile_routes.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configurar rate limiter
limiter = Limiter(
    key_func=get_remote_address,  # Usar IP como identificador
    storage_uri="memory://",      # Almacenamiento en memoria
    default_limits=["200 per day", "50 per hour"]  # Límites por defecto
)

# Aplicar a Blueprint
@profile_bp.route('/upload-picture', methods=['POST'])
@limiter.limit("10 per hour")  # Límite específico para upload
@token_required
def upload_profile_picture(current_user_id):
    """Upload con rate limiting"""
    # ... lógica de upload
```

#### 2. Rate Limiting Avanzado por Usuario
```python
# utils/rate_limiter.py
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import redis

class AdvancedRateLimiter:
    def __init__(self, redis_client=None):
        # En producción usar Redis, en desarrollo usar memoria
        self.storage = redis_client or {}
        
    def limit_by_user(self, max_requests=100, window_hours=1):
        """Rate limiting por usuario autenticado"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                # Obtener user_id del token JWT
                token = request.headers.get('Authorization')
                if not token:
                    return jsonify({'message': 'Token requerido'}), 401
                
                try:
                    # Decodificar token para obtener user_id
                    payload = jwt.decode(
                        token.split(' ')[1], 
                        current_app.config['SECRET_KEY'], 
                        algorithms=['HS256']
                    )
                    user_id = payload['userId']
                except:
                    return jsonify({'message': 'Token inválido'}), 401
                
                # Crear clave única para el usuario
                key = f"rate_limit:user:{user_id}:{datetime.utcnow().hour}"
                
                # Verificar límite
                current_count = self.storage.get(key, 0)
                if isinstance(current_count, bytes):
                    current_count = int(current_count)
                
                if current_count >= max_requests:
                    return jsonify({
                        'message': f'Rate limit excedido. Máximo {max_requests} requests por hora'
                    }), 429
                
                # Incrementar contador
                self.storage[key] = current_count + 1
                
                # Ejecutar función original
                return f(*args, **kwargs)
            
            return decorated
        return decorator

# Uso del rate limiter avanzado
rate_limiter = AdvancedRateLimiter()

@profile_bp.route('/sensitive-operation', methods=['POST'])
@rate_limiter.limit_by_user(max_requests=5, window_hours=1)
@token_required
def sensitive_operation(current_user_id):
    """Operación sensible con rate limiting estricto"""
    # ... lógica de operación sensible
```

#### 3. Rate Limiting con Diferentes Niveles
```python
# utils/tiered_rate_limiter.py
class TieredRateLimiter:
    """Rate limiter con diferentes niveles según el endpoint"""
    
    LIMITS = {
        'auth': {
            'login': "10 per minute",
            'register': "5 per minute", 
            'forgot_password': "3 per minute"
        },
        'profile': {
            'get': "100 per hour",
            'update': "20 per hour",
            'upload': "10 per hour"
        },
        'admin': {
            'reputation_update': "50 per hour"
        }
    }
    
    @classmethod
    def apply_limits(cls, app, limiter):
        """Aplicar límites específicos a endpoints"""
        
        # Límites para autenticación
        @app.route('/api/auth/login', methods=['POST'])
        @limiter.limit(cls.LIMITS['auth']['login'])
        def login_with_limit():
            return AuthController.login(request.get_json())
        
        @app.route('/api/auth/register', methods=['POST'])
        @limiter.limit(cls.LIMITS['auth']['register'])  
        def register_with_limit():
            return AuthController.register(request.get_json())
        
        # Límites para operaciones de perfil
        @app.route('/api/profile/upload-picture', methods=['POST'])
        @limiter.limit(cls.LIMITS['profile']['upload'])
        @token_required
        def upload_with_limit(current_user_id):
            return ProfileController.upload_picture(current_user_id, request.files.get('file'))
```

#### 4. Manejo de Errores de Rate Limiting
```python
# app.py - Configuración global de rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app():
    app = Flask(__name__)
    
    # Configurar rate limiter
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Manejador personalizado para errores de rate limit
    @app.errorhandler(429)
    def rate_limit_handler(e):
        return jsonify({
            'message': 'Rate limit excedido',
            'error': 'Demasiadas solicitudes. Intenta más tarde.',
            'retry_after': str(e.retry_after) if hasattr(e, 'retry_after') else '60'
        }), 429
    
    return app
```

---

## 🛠️ Implementación Paso a Paso

### Paso 1: Configuración Inicial

#### 1.1 Instalar Dependencias
```bash
pip install flask flask-cors PyJWT bcrypt google-auth flask-limiter
```

#### 1.2 Variables de Entorno
```env
# .env
JWT_SECRET=tu_clave_secreta_super_segura_de_al_menos_32_caracteres
GOOGLE_CLIENT_ID=tu_client_id.apps.googleusercontent.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
```

### Paso 2: Estructura de Archivos
```
project/
├── models/
│   ├── user.py
│   └── password_reset_token.py
├── controllers/
│   ├── auth_controller.py
│   └── password_reset_controller.py
├── services/
│   └── email_service.py
├── utils/
│   ├── jwt_validator.py
│   └── rate_limiter.py
└── app.py
```

### Paso 3: Implementación Gradual

#### 3.1 Implementar JWT Básico
1. Crear modelo de usuario con hash bcrypt
2. Implementar generación de JWT en login
3. Crear decorador de validación de token
4. Aplicar a rutas protegidas

#### 3.2 Agregar Google OAuth
1. Configurar Google Client ID
2. Implementar validación de Google ID Token
3. Crear/actualizar usuario con datos de Google
4. Generar JWT para usuario autenticado

#### 3.3 Sistema de Reset de Contraseñas
1. Crear modelo de token de reset
2. Implementar generación y envío de tokens
3. Crear endpoints de verificación y reset
4. Configurar servicio de email

#### 3.4 Rate Limiting
1. Instalar y configurar Flask-Limiter
2. Aplicar límites globales
3. Crear límites específicos por endpoint
4. Implementar manejo de errores

### Paso 4: Testing de Seguridad

#### 4.1 Tests de JWT
```python
# tests/test_jwt_security.py
import pytest
import jwt
from datetime import datetime, timedelta

def test_jwt_expiration():
    """Test que JWT expira correctamente"""
    # Crear token expirado
    expired_payload = {
        'userId': 'test_user',
        'exp': datetime.utcnow() - timedelta(hours=1)
    }
    expired_token = jwt.encode(expired_payload, 'secret', algorithm='HS256')
    
    # Intentar validar token expirado
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired_token, 'secret', algorithms=['HS256'])

def test_jwt_invalid_signature():
    """Test que JWT con firma inválida es rechazado"""
    payload = {'userId': 'test_user'}
    token = jwt.encode(payload, 'secret1', algorithm='HS256')
    
    # Intentar decodificar con clave diferente
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, 'secret2', algorithms=['HS256'])
```

#### 4.2 Tests de Rate Limiting
```python
# tests/test_rate_limiting.py
def test_rate_limiting_enforced(client):
    """Test que rate limiting funciona"""
    # Hacer muchas requests rápidamente
    for i in range(15):  # Exceder límite de 10/min
        response = client.post('/api/auth/login', json={
            'email': 'test@test.com',
            'password': 'wrong'
        })
    
    # Última request debe ser bloqueada
    assert response.status_code == 429
    assert 'rate limit' in response.json['message'].lower()
```

### Paso 5: Monitoreo y Logs

#### 5.1 Logging de Seguridad
```python
# utils/security_logger.py
import logging

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)
    
    def log_failed_login(self, email, ip_address):
        """Log intento de login fallido"""
        self.logger.warning(
            f"Failed login attempt | Email: {email} | IP: {ip_address}"
        )
    
    def log_rate_limit_exceeded(self, ip_address, endpoint):
        """Log rate limit excedido"""
        self.logger.warning(
            f"Rate limit exceeded | IP: {ip_address} | Endpoint: {endpoint}"
        )
    
    def log_password_reset_request(self, email, ip_address):
        """Log solicitud de reset de contraseña"""
        self.logger.info(
            f"Password reset requested | Email: {email} | IP: {ip_address}"
        )
```

---

## 🔍 Mejores Prácticas de Seguridad

### ✅ Do's (Hacer)
- **Usar HTTPS** en producción siempre
- **Validar todos los inputs** del usuario
- **Implementar rate limiting** en todos los endpoints públicos
- **Rotar claves JWT** periódicamente
- **Auditar logs** de seguridad regularmente
- **Implementar 2FA** para cuentas administrativas
- **Usar tokens de corta duración** para operaciones sensibles

### ❌ Don'ts (No hacer)
- **No almacenar contraseñas** en texto plano jamás
- **No incluir información sensible** en logs
- **No usar claves JWT débiles** (mínimo 32 caracteres)
- **No confiar solo en JWT** para operaciones críticas
- **No ignorar rate limiting** en endpoints de autenticación
- **No enviar tokens** por URL parameters
- **No usar algoritmos** de hash obsoletos (MD5, SHA1)

---

## 📚 Recursos Adicionales

- [RFC 7519 - JSON Web Token](https://tools.ietf.org/html/rfc7519)
- [Google Sign-In Documentation](https://developers.google.com/identity/sign-in/web)
- [bcrypt Documentation](https://pypi.org/project/bcrypt/)
- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

*Esta guía cubre las características de seguridad implementadas en Mascotas App Backend. Para más información, consulta la documentación específica de cada componente.*
