"""
Servicio de CAPTCHA para validación de usuarios
"""
import random
import string
import time
from typing import Dict, Tuple, Optional
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import requests
import os

class CaptchaService:
    """Servicio para generar y validar CAPTCHAs"""
    
    def __init__(self):
        self.captcha_storage = {}  # En producción usar Redis
        self.captcha_timeout = 300  # 5 minutos
    
    def generate_math_captcha(self) -> Dict[str, str]:
        """
        Genera un CAPTCHA con operación matemática simple
        
        Returns:
            Dict con el CAPTCHA ID, pregunta y imagen en base64
        """
        try:
            # Generar operación matemática simple
            num1 = random.randint(1, 20)
            num2 = random.randint(1, 20)
            operation = random.choice(['+', '-', '*'])
            
            if operation == '+':
                answer = num1 + num2
                question = f"{num1} + {num2}"
            elif operation == '-':
                # Asegurar que el resultado sea positivo
                if num1 < num2:
                    num1, num2 = num2, num1
                answer = num1 - num2
                question = f"{num1} - {num2}"
            else:  # multiplication
                # Usar números más pequeños para multiplicación
                num1 = random.randint(1, 10)
                num2 = random.randint(1, 10)
                answer = num1 * num2
                question = f"{num1} × {num2}"
            
            # Generar ID único para el CAPTCHA
            captcha_id = self._generate_captcha_id()
            
            # Crear imagen del CAPTCHA
            captcha_image = self._create_captcha_image(question)
            
            # Almacenar la respuesta
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
            print(f"Error generando CAPTCHA matemático: {str(e)}")
            return self._generate_fallback_captcha()
    
    def generate_text_captcha(self) -> Dict[str, str]:
        """
        Genera un CAPTCHA con texto aleatorio
        
        Returns:
            Dict con el CAPTCHA ID y imagen en base64
        """
        try:
            # Generar texto aleatorio (evitar caracteres confusos)
            chars = 'ABCDEFGHIJKLMNPQRSTUVWXYZ23456789'  # Sin O, 0, 1, I
            captcha_text = ''.join(random.choices(chars, k=6))
            
            # Generar ID único
            captcha_id = self._generate_captcha_id()
            
            # Crear imagen del CAPTCHA
            captcha_image = self._create_text_captcha_image(captcha_text)
            
            # Almacenar la respuesta
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
            print(f"Error generando CAPTCHA de texto: {str(e)}")
            return self._generate_fallback_captcha()
    
    def validate_captcha(self, captcha_id: str, user_answer: str) -> bool:
        """
        Valida la respuesta del CAPTCHA
        
        Args:
            captcha_id: ID del CAPTCHA a validar
            user_answer: Respuesta proporcionada por el usuario
            
        Returns:
            True si la respuesta es correcta, False en caso contrario
        """
        try:
            # Verificar que el CAPTCHA existe
            if captcha_id not in self.captcha_storage:
                print(f"CAPTCHA ID no encontrado: {captcha_id}")
                return False
            
            captcha_data = self.captcha_storage[captcha_id]
            
            # Verificar expiración (5 minutos)
            if time.time() - captcha_data['created_at'] > self.captcha_timeout:
                del self.captcha_storage[captcha_id]
                print(f"CAPTCHA expirado: {captcha_id}")
                return False
            
            # Incrementar intentos
            captcha_data['attempts'] += 1
            
            # Máximo 3 intentos
            if captcha_data['attempts'] > 3:
                del self.captcha_storage[captcha_id]
                print(f"Máximo de intentos alcanzado para CAPTCHA: {captcha_id}")
                return False
            
            # Validar respuesta
            correct_answer = captcha_data['answer']
            user_answer_clean = str(user_answer).strip().upper()
            
            is_correct = correct_answer == user_answer_clean
            
            # Si es correcta, eliminar del almacenamiento
            if is_correct:
                del self.captcha_storage[captcha_id]
                print(f"CAPTCHA validado correctamente: {captcha_id}")
            
            return is_correct
            
        except Exception as e:
            print(f"Error validando CAPTCHA: {str(e)}")
            return False
    
    def _generate_captcha_id(self) -> str:
        """Genera un ID único para el CAPTCHA"""
        timestamp = str(time.time())
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return hashlib.md5(f"{timestamp}_{random_str}".encode()).hexdigest()
    
    def _create_captcha_image(self, question: str) -> str:
        """
        Crea una imagen para el CAPTCHA matemático
        
        Args:
            question: La pregunta matemática a mostrar
            
        Returns:
            Imagen codificada en base64
        """
        try:
            # Crear imagen
            width, height = 200, 80
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Intentar usar una fuente del sistema, si no usar la por defecto
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Agregar ruido de fondo
            for _ in range(100):
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.point((x, y), fill=(200, 200, 200))
            
            # Dibujar líneas de distracción
            for _ in range(5):
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                draw.line([(x1, y1), (x2, y2)], fill=(180, 180, 180), width=1)
            
            # Calcular posición del texto
            bbox = draw.textbbox((0, 0), question, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Dibujar el texto
            draw.text((x, y), question, fill='black', font=font)
            
            # Convertir a base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error creando imagen de CAPTCHA: {str(e)}")
            return self._create_simple_captcha_image(question)
    
    def _create_text_captcha_image(self, text: str) -> str:
        """
        Crea una imagen para el CAPTCHA de texto
        
        Args:
            text: El texto a mostrar
            
        Returns:
            Imagen codificada en base64
        """
        try:
            # Crear imagen
            width, height = 200, 80
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Intentar usar una fuente del sistema
            try:
                font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()
            
            # Agregar ruido de fondo
            for _ in range(150):
                x = random.randint(0, width)
                y = random.randint(0, height)
                draw.point((x, y), fill=(random.randint(150, 200), 
                                       random.randint(150, 200), 
                                       random.randint(150, 200)))
            
            # Dibujar líneas de distracción
            for _ in range(8):
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                draw.line([(x1, y1), (x2, y2)], 
                         fill=(random.randint(100, 150), 
                               random.randint(100, 150), 
                               random.randint(100, 150)), width=1)
            
            # Dibujar cada carácter con pequeñas variaciones
            x_offset = 20
            for i, char in enumerate(text):
                # Variar ligeramente la posición
                x = x_offset + (i * 25) + random.randint(-5, 5)
                y = 25 + random.randint(-5, 5)
                
                # Variar el color
                color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
                
                draw.text((x, y), char, fill=color, font=font)
            
            # Convertir a base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error creando imagen de texto CAPTCHA: {str(e)}")
            return self._create_simple_text_image(text)
    
    def _create_simple_captcha_image(self, text: str) -> str:
        """Fallback para crear imagen simple sin PIL"""
        # En caso de que PIL no esté disponible, retornar un placeholder
        svg_content = f'''<svg xmlns='http://www.w3.org/2000/svg' width='200' height='80'>
            <rect width='200' height='80' fill='#f0f0f0' stroke='#ccc'/>
            <text x='100' y='45' text-anchor='middle' font-family='Arial' font-size='20' fill='#333'>{text}</text>
        </svg>'''
        
        return f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"
    
    def _create_simple_text_image(self, text: str) -> str:
        """Fallback para crear imagen de texto simple"""
        return self._create_simple_captcha_image(text)
    
    def _generate_fallback_captcha(self) -> Dict[str, str]:
        """Genera un CAPTCHA de fallback en caso de error"""
        captcha_id = self._generate_captcha_id()
        answer = str(random.randint(10, 50))
        
        self.captcha_storage[captcha_id] = {
            'answer': answer,
            'created_at': time.time(),
            'attempts': 0
        }
        
        return {
            'captcha_id': captcha_id,
            'question': f"Escribe el número: {answer}",
            'image': self._create_simple_captcha_image(answer)
        }
    
    def cleanup_expired_captchas(self):
        """Limpia CAPTCHAs expirados"""
        current_time = time.time()
        expired_ids = [
            captcha_id for captcha_id, data in self.captcha_storage.items()
            if current_time - data['created_at'] > self.captcha_timeout
        ]
        
        for captcha_id in expired_ids:
            del self.captcha_storage[captcha_id]
        
        if expired_ids:
            print(f"Limpiados {len(expired_ids)} CAPTCHAs expirados")


class RecaptchaService:
    """Servicio para validación con Google reCAPTCHA"""
    
    def __init__(self):
        self.recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY')
        self.recaptcha_site_key = os.getenv('RECAPTCHA_SITE_KEY')
        self.verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    
    def verify_recaptcha(self, recaptcha_response: str, user_ip: str = None) -> Dict[str, any]:
        """
        Verifica el token de reCAPTCHA con Google
        
        Args:
            recaptcha_response: Token de respuesta del reCAPTCHA
            user_ip: IP del usuario (opcional)
            
        Returns:
            Dict con el resultado de la verificación
        """
        try:
            if not self.recaptcha_secret:
                return {
                    'success': False,
                    'error': 'reCAPTCHA no configurado correctamente'
                }
            
            # Datos para enviar a Google
            data = {
                'secret': self.recaptcha_secret,
                'response': recaptcha_response
            }
            
            if user_ip:
                data['remoteip'] = user_ip
            
            # Hacer request a Google
            response = requests.post(self.verify_url, data=data, timeout=10)
            result = response.json()
            
            return {
                'success': result.get('success', False),
                'score': result.get('score', 0),  # Para reCAPTCHA v3
                'action': result.get('action', ''),
                'errors': result.get('error-codes', [])
            }
            
        except requests.RequestException as e:
            print(f"Error conectando con Google reCAPTCHA: {str(e)}")
            return {
                'success': False,
                'error': 'Error de conexión con el servicio de CAPTCHA'
            }
        except Exception as e:
            print(f"Error verificando reCAPTCHA: {str(e)}")
            return {
                'success': False,
                'error': 'Error interno verificando CAPTCHA'
            }
    
    def get_site_key(self) -> Optional[str]:
        """Retorna la clave del sitio para el frontend"""
        return self.recaptcha_site_key


# Instancia global del servicio de CAPTCHA
captcha_service = CaptchaService()
recaptcha_service = RecaptchaService()
