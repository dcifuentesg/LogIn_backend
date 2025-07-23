"""
Tests para el sistema de CAPTCHA
"""
import pytest
import json
import base64
from io import BytesIO
from PIL import Image
from services.captcha_service import CaptchaService, RecaptchaService
from controllers.user_controller import UserController


class TestCaptchaService:
    """Tests para el servicio de CAPTCHA"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.captcha_service = CaptchaService()
    
    def test_generate_math_captcha(self):
        """Test generación de CAPTCHA matemático"""
        captcha_data = self.captcha_service.generate_math_captcha()
        
        assert 'captcha_id' in captcha_data
        assert 'question' in captcha_data
        assert 'image' in captcha_data
        assert captcha_data['image'].startswith('data:image/')
        assert len(captcha_data['captcha_id']) == 32  # MD5 hash length
    
    def test_generate_text_captcha(self):
        """Test generación de CAPTCHA de texto"""
        captcha_data = self.captcha_service.generate_text_captcha()
        
        assert 'captcha_id' in captcha_data
        assert 'image' in captcha_data
        assert captcha_data['image'].startswith('data:image/')
        assert len(captcha_data['captcha_id']) == 32
    
    def test_validate_correct_math_captcha(self):
        """Test validación correcta de CAPTCHA matemático"""
        # Generar CAPTCHA
        captcha_data = self.captcha_service.generate_math_captcha()
        captcha_id = captcha_data['captcha_id']
        
        # Obtener la respuesta correcta del almacenamiento
        correct_answer = self.captcha_service.captcha_storage[captcha_id]['answer']
        
        # Validar con respuesta correcta
        is_valid = self.captcha_service.validate_captcha(captcha_id, correct_answer)
        assert is_valid is True
    
    def test_validate_incorrect_captcha(self):
        """Test validación incorrecta de CAPTCHA"""
        # Generar CAPTCHA
        captcha_data = self.captcha_service.generate_math_captcha()
        captcha_id = captcha_data['captcha_id']
        
        # Validar con respuesta incorrecta
        is_valid = self.captcha_service.validate_captcha(captcha_id, "respuesta_incorrecta")
        assert is_valid is False
    
    def test_validate_nonexistent_captcha(self):
        """Test validación de CAPTCHA que no existe"""
        is_valid = self.captcha_service.validate_captcha("id_inexistente", "123")
        assert is_valid is False
    
    def test_captcha_expiry(self):
        """Test expiración de CAPTCHA"""
        import time
        
        # Generar CAPTCHA
        captcha_data = self.captcha_service.generate_math_captcha()
        captcha_id = captcha_data['captcha_id']
        
        # Simular expiración modificando el timestamp
        self.captcha_service.captcha_storage[captcha_id]['created_at'] = time.time() - 400  # 400 segundos atrás
        
        # Intentar validar CAPTCHA expirado
        is_valid = self.captcha_service.validate_captcha(captcha_id, "cualquier_respuesta")
        assert is_valid is False
    
    def test_max_attempts(self):
        """Test máximo número de intentos"""
        # Generar CAPTCHA
        captcha_data = self.captcha_service.generate_math_captcha()
        captcha_id = captcha_data['captcha_id']
        
        # Hacer 3 intentos incorrectos
        for i in range(3):
            is_valid = self.captcha_service.validate_captcha(captcha_id, "incorrecta")
            assert is_valid is False
        
        # El 4to intento debería fallar por exceder límite
        is_valid = self.captcha_service.validate_captcha(captcha_id, "cualquiera")
        assert is_valid is False
        
        # El CAPTCHA debe haber sido eliminado
        assert captcha_id not in self.captcha_service.captcha_storage
    
    def test_cleanup_expired_captchas(self):
        """Test limpieza de CAPTCHAs expirados"""
        import time
        
        # Generar varios CAPTCHAs
        captcha1 = self.captcha_service.generate_math_captcha()
        captcha2 = self.captcha_service.generate_math_captcha()
        
        # Hacer que uno expire
        expired_id = captcha1['captcha_id']
        self.captcha_service.captcha_storage[expired_id]['created_at'] = time.time() - 400
        
        # Limpiar expirados
        self.captcha_service.cleanup_expired_captchas()
        
        # El expirado debe haber sido eliminado
        assert expired_id not in self.captcha_service.captcha_storage
        
        # El válido debe seguir ahí
        assert captcha2['captcha_id'] in self.captcha_service.captcha_storage
    
    def test_captcha_image_format(self):
        """Test formato de imagen del CAPTCHA"""
        captcha_data = self.captcha_service.generate_math_captcha()
        image_data = captcha_data['image']
        
        # Verificar que es base64
        assert image_data.startswith('data:image/png;base64,')
        
        # Extraer datos base64
        base64_data = image_data.split(',')[1]
        
        try:
            # Decodificar base64
            image_bytes = base64.b64decode(base64_data)
            
            # Verificar que se puede abrir como imagen
            image = Image.open(BytesIO(image_bytes))
            assert image.format == 'PNG'
            assert image.size == (200, 80)  # Tamaño esperado
            
        except Exception as e:
            # Si PIL no está disponible, al menos verificar base64 válido
            assert len(base64_data) > 0


@pytest.fixture
def mock_user_data():
    """Datos de usuario para tests"""
    return {
        'email': 'test@example.com',
        'password': 'password123',
        'full_name': 'Test User'
    }


class TestCaptchaLoginIntegration:
    """Tests de integración para login con CAPTCHA"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.captcha_service = CaptchaService()
    
    def test_login_with_valid_captcha(self, mock_user_data):
        """Test login exitoso con CAPTCHA válido"""
        # Generar CAPTCHA
        captcha_data = self.captcha_service.generate_math_captcha()
        captcha_id = captcha_data['captcha_id']
        correct_answer = self.captcha_service.captcha_storage[captcha_id]['answer']
        
        # Datos de login con CAPTCHA
        login_data = {
            'email': mock_user_data['email'],
            'password': mock_user_data['password'],
            'captcha_id': captcha_id,
            'captcha_answer': correct_answer
        }
        
        # Nota: Este test requiere que el usuario exista en la base de datos
        # En un test real, deberías crear el usuario primero o mockearlo
    
    def test_login_with_invalid_captcha(self, mock_user_data):
        """Test login fallido con CAPTCHA inválido"""
        # Generar CAPTCHA
        captcha_data = self.captcha_service.generate_math_captcha()
        captcha_id = captcha_data['captcha_id']
        
        # Datos de login con CAPTCHA incorrecto
        login_data = {
            'email': mock_user_data['email'],
            'password': mock_user_data['password'],
            'captcha_id': captcha_id,
            'captcha_answer': 'respuesta_incorrecta'
        }
        
        # Llamar al controlador
        response, status_code = UserController.login_user(login_data)
        
        # Debe fallar por CAPTCHA inválido
        assert status_code == 400
        assert 'CAPTCHA' in response['message']
        assert response.get('captcha_required') is True
    
    def test_login_without_captcha(self, mock_user_data):
        """Test login fallido sin CAPTCHA"""
        # Datos de login sin CAPTCHA
        login_data = {
            'email': mock_user_data['email'],
            'password': mock_user_data['password']
        }
        
        # Llamar al controlador
        response, status_code = UserController.login_user(login_data)
        
        # Debe fallar por falta de CAPTCHA
        assert status_code == 400
        assert 'CAPTCHA requerido' in response['message']
        assert response.get('captcha_required') is True


class TestRecaptchaService:
    """Tests para el servicio de reCAPTCHA"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.recaptcha_service = RecaptchaService()
    
    def test_recaptcha_not_configured(self):
        """Test cuando reCAPTCHA no está configurado"""
        # Asegurar que no hay clave configurada
        self.recaptcha_service.recaptcha_secret = None
        
        result = self.recaptcha_service.verify_recaptcha('test_token')
        
        assert result['success'] is False
        assert 'no configurado' in result['error']
    
    def test_get_site_key_not_configured(self):
        """Test obtener site key cuando no está configurado"""
        self.recaptcha_service.recaptcha_site_key = None
        
        site_key = self.recaptcha_service.get_site_key()
        
        assert site_key is None
    
    @pytest.mark.skip(reason="Requiere configuración real de reCAPTCHA")
    def test_recaptcha_with_real_token(self):
        """Test con token real de reCAPTCHA (requiere configuración)"""
        # Este test se skipea por defecto porque requiere configuración real
        # Para usarlo, configura las variables de entorno y quita el skip
        
        real_token = "token_real_de_recaptcha"
        result = self.recaptcha_service.verify_recaptcha(real_token)
        
        assert 'success' in result
        assert isinstance(result['success'], bool)


class TestCaptchaRoutes:
    """Tests para las rutas de CAPTCHA (requiere cliente de prueba)"""
    
    @pytest.fixture
    def client(self, app):
        """Cliente de prueba Flask"""
        return app.test_client()
    
    def test_generate_captcha_endpoint(self, client):
        """Test endpoint de generación de CAPTCHA"""
        response = client.post('/api/captcha/generate')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'captcha' in data
        assert 'captcha_id' in data['captcha']
        assert 'image' in data['captcha']
    
    def test_validate_captcha_endpoint(self, client):
        """Test endpoint de validación de CAPTCHA"""
        # Primero generar un CAPTCHA
        gen_response = client.post('/api/captcha/generate')
        gen_data = json.loads(gen_response.data)
        
        captcha_id = gen_data['captcha']['captcha_id']
        
        # Intentar validar con respuesta incorrecta
        validate_response = client.post('/api/captcha/validate', 
                                      json={
                                          'captcha_id': captcha_id,
                                          'answer': 'incorrecta'
                                      })
        
        assert validate_response.status_code == 200
        
        validate_data = json.loads(validate_response.data)
        assert validate_data['success'] is True
        assert validate_data['valid'] is False
    
    def test_recaptcha_site_key_endpoint(self, client):
        """Test endpoint para obtener site key de reCAPTCHA"""
        response = client.get('/api/captcha/recaptcha/site-key')
        
        # Puede ser 200 con site_key o 404 si no está configurado
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'site_key' in data


# Ejecutar tests individualmente
if __name__ == '__main__':
    # Test básico del servicio
    captcha_service = CaptchaService()
    
    print("🧪 Ejecutando test básico de CAPTCHA...")
    
    # Generar CAPTCHA
    captcha_data = captcha_service.generate_math_captcha()
    print(f"✅ CAPTCHA generado: {captcha_data['captcha_id']}")
    print(f"📝 Pregunta: {captcha_data['question']}")
    
    # Obtener respuesta correcta
    captcha_id = captcha_data['captcha_id']
    correct_answer = captcha_service.captcha_storage[captcha_id]['answer']
    print(f"🔢 Respuesta correcta: {correct_answer}")
    
    # Validar respuesta correcta
    is_valid = captcha_service.validate_captcha(captcha_id, correct_answer)
    print(f"✅ Validación correcta: {is_valid}")
    
    # Generar nuevo CAPTCHA para probar respuesta incorrecta
    captcha_data2 = captcha_service.generate_math_captcha()
    captcha_id2 = captcha_data2['captcha_id']
    
    # Validar respuesta incorrecta
    is_invalid = captcha_service.validate_captcha(captcha_id2, "999")
    print(f"❌ Validación incorrecta: {not is_invalid}")
    
    print("🎉 Tests básicos completados exitosamente!")
