# 🤖 Sistema CAPTCHA - Guía de Implementación Completa

## 📋 Resumen

Se ha implementado exitosamente un **sistema CAPTCHA robusto** en el backend de login que incluye:

✅ **CAPTCHA matemático simple** (operaciones básicas)  
✅ **CAPTCHA de texto aleatorio** con distorsión  
✅ **Integración con Google reCAPTCHA** (opcional)  
✅ **Validación obligatoria en login**  
✅ **Expiración automática** (5 minutos)  
✅ **Límite de intentos** (máximo 3)  
✅ **Generación de imágenes** con ruido anti-bot  
✅ **APIs REST completas**  
✅ **Tests automatizados**  

---

## 🚀 Cómo Usar el Sistema

### 1. **Instalar Dependencias**

La dependencia principal ya está instalada:
```bash
pip install Pillow  # ✅ Ya instalado
```

### 2. **Configurar Variables de Entorno (Opcional)**

Para usar reCAPTCHA de Google, agregar a tu `.env`:
```env
# reCAPTCHA (opcional)
RECAPTCHA_SITE_KEY=tu_site_key_aqui
RECAPTCHA_SECRET_KEY=tu_secret_key_aqui
```

### 3. **Iniciar el Servidor**

```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

---

## 🔗 Endpoints Disponibles

### **Generar CAPTCHA**
```http
POST /api/captcha/generate
Content-Type: application/json

{
    "type": "math"  // o "text", opcional
}
```

**Respuesta:**
```json
{
    "success": true,
    "captcha": {
        "captcha_id": "abc123def456...",
        "question": "15 + 7",
        "image": "data:image/png;base64,iVBORw0KGgo..."
    }
}
```

### **Login con CAPTCHA (OBLIGATORIO)**
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
{
    "email": "user@example.com", 
    "password": "password123",
    "recaptcha_response": "03AGdBq27..."
}
```

---

## 💻 Integración Frontend

### **HTML Básico**
```html
<form id="login-form">
    <input type="email" id="email" placeholder="Email" required>
    <input type="password" id="password" placeholder="Contraseña" required>
    
    <!-- CAPTCHA -->
    <div class="captcha-container">
        <img id="captcha-image" src="" alt="CAPTCHA" onclick="generateNewCaptcha()">
        <input type="text" id="captcha-answer" placeholder="Respuesta del CAPTCHA" required>
        <button type="button" onclick="generateNewCaptcha()">🔄 Nuevo CAPTCHA</button>
    </div>
    
    <button type="submit">Iniciar Sesión</button>
</form>
```

### **JavaScript Completo**
```javascript
// Variables globales
let currentCaptchaId = null;

// Generar nuevo CAPTCHA al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    generateNewCaptcha();
});

// Función para generar CAPTCHA
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
            currentCaptchaId = data.captcha.captcha_id;
            document.getElementById('captcha-answer').value = '';
            
            // Mostrar pregunta si es matemático
            if (data.captcha.question) {
                document.getElementById('captcha-image').title = `Resuelve: ${data.captcha.question}`;
            }
        } else {
            console.error('Error generando CAPTCHA:', data);
        }
    } catch (error) {
        console.error('Error de conexión:', error);
    }
}

// Manejar login
document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const captchaAnswer = document.getElementById('captcha-answer').value;
    
    if (!email || !password || !captchaAnswer) {
        alert('Todos los campos son obligatorios');
        return;
    }
    
    try {
        const response = await fetch('/api/users/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                password: password,
                captcha_id: currentCaptchaId,
                captcha_answer: captchaAnswer
            })
        });
        
        const data = await response.json();
        
        if (data.token) {
            // Login exitoso
            localStorage.setItem('authToken', data.token);
            alert('Login exitoso! Bienvenido ' + data.user.full_name);
            
            // Redirigir al dashboard
            window.location.href = '/dashboard';
            
        } else {
            // Error en login
            alert(data.message);
            
            // Generar nuevo CAPTCHA siempre después de un intento fallido
            generateNewCaptcha();
        }
        
    } catch (error) {
        console.error('Error en login:', error);
        alert('Error de conexión. Intenta de nuevo.');
        generateNewCaptcha();
    }
});
```

### **CSS Para Estilizar**
```css
.captcha-container {
    margin: 15px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
    text-align: center;
}

.captcha-container img {
    display: block;
    margin: 10px auto;
    border: 2px solid #007bff;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s;
}

.captcha-container img:hover {
    opacity: 0.8;
    transform: scale(1.02);
}

#captcha-answer {
    width: 150px;
    padding: 8px;
    margin: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    text-align: center;
}

.captcha-container button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.captcha-container button:hover {
    background-color: #0056b3;
}

#login-form {
    max-width: 400px;
    margin: 50px auto;
    padding: 30px;
    border: 1px solid #ddd;
    border-radius: 10px;
    background-color: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

#login-form input[type="email"],
#login-form input[type="password"] {
    width: 100%;
    padding: 12px;
    margin: 10px 0;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
    box-sizing: border-box;
}

#login-form button[type="submit"] {
    width: 100%;
    padding: 12px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 20px;
}

#login-form button[type="submit"]:hover {
    background-color: #218838;
}
```

---

## 🛡️ Características de Seguridad

### **✅ Medidas Implementadas**

1. **Expiración Automática**: CAPTCHAs expiran en 5 minutos
2. **Límite de Intentos**: Máximo 3 intentos por CAPTCHA
3. **Validación Obligatoria**: No se puede hacer login sin CAPTCHA válido
4. **Imágenes con Distorsión**: Ruido y líneas para prevenir OCR
5. **IDs Únicos**: Cada CAPTCHA tiene identificador único MD5
6. **Limpieza Automática**: CAPTCHAs expirados se eliminan automáticamente
7. **Rate Limiting**: Se puede integrar con el sistema existente
8. **Logging de Seguridad**: Registro de intentos fallidos

### **🔒 Flujo de Seguridad**

```
Usuario → Generar CAPTCHA → Mostrar Imagen → Usuario Resuelve → 
Validar Respuesta → Login con Credenciales → JWT Token
```

### **❌ Casos de Error Manejados**

- CAPTCHA expirado (> 5 minutos)
- Máximo intentos alcanzado (> 3)
- Respuesta incorrecta
- CAPTCHA ID no existe
- Falta de datos obligatorios
- Errores de conexión
- Errores de generación de imagen

---

## 🧪 Testing

### **Test Manual Rápido**
```bash
cd LogIn_backend
python test_captcha_simple.py
```

**Salida Esperada:**
```
🧪 Iniciando test básico de CAPTCHA...
✅ CAPTCHA generado exitosamente
✅ Validación correcta exitosa 
✅ Validación incorrecta funcionó correctamente
✅ CAPTCHA de texto generado exitosamente
🎉 Todos los tests básicos completados exitosamente!
```

### **Test con Curl**
```bash
# 1. Generar CAPTCHA
curl -X POST http://localhost:5000/api/captcha/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "math"}'

# 2. Usar el captcha_id y resolver la pregunta en el login
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com", 
    "password": "password123",
    "captcha_id": "ID_DEL_CAPTCHA_AQUI",
    "captcha_answer": "RESPUESTA_AQUI"
  }'
```

---

## 🔧 Configuración Avanzada

### **Para usar reCAPTCHA de Google:**

1. Ir a https://www.google.com/recaptcha/admin/create
2. Crear un nuevo sitio
3. Obtener Site Key y Secret Key
4. Agregar a `.env`:
```env
RECAPTCHA_SITE_KEY=tu_site_key_aqui
RECAPTCHA_SECRET_KEY=tu_secret_key_aqui
```

5. En el frontend, cargar el script de Google:
```html
<script src="https://www.google.com/recaptcha/api.js"></script>
<div class="g-recaptcha" data-sitekey="TU_SITE_KEY"></div>
```

### **Personalizar Configuración:**

Editar `services/captcha_service.py`:
```python
class CaptchaService:
    def __init__(self):
        self.captcha_timeout = 300  # 5 minutos
        self.max_attempts = 3       # 3 intentos máximo
        self.image_size = (200, 80) # Tamaño de imagen
```

---

## 🎯 Próximos Pasos Recomendados

### **Para Producción:**
1. **Usar Redis** en lugar de memoria para almacenar CAPTCHAs
2. **Configurar reCAPTCHA v3** para mejor experiencia de usuario
3. **Implementar rate limiting** específico para CAPTCHAs
4. **Agregar métricas** de uso y éxito
5. **Configurar logging** detallado de seguridad

### **Para Mejorar UX:**
1. **CAPTCHA de audio** para accesibilidad
2. **Slider CAPTCHA** como alternativa
3. **Auto-refresh** de CAPTCHA cada cierto tiempo
4. **Preview** antes de enviar el formulario
5. **Indicador visual** de CAPTCHA válido

---

## 📞 Soporte y Troubleshooting

### **Problemas Comunes:**

**Q: Error "No module named 'services'"**  
A: Ejecutar desde el directorio raíz del proyecto: `cd LogIn_backend && python archivo.py`

**Q: Error "PIL no encontrado"**  
A: Instalar con: `pip install Pillow`

**Q: CAPTCHA no se ve**  
A: Verificar que el servidor esté ejecutándose en puerto 5000 y que CORS esté configurado

**Q: Login falla siempre**  
A: Verificar que el usuario exista en la base de datos y que las credenciales sean correctas

**Q: reCAPTCHA no funciona**  
A: Verificar que las keys de Google estén configuradas correctamente en `.env`

### **Debug Mode:**
Agregar al código para debug:
```python
print(f"🐛 CAPTCHA ID: {captcha_id}")
print(f"🐛 Respuesta correcta: {correct_answer}")  
print(f"🐛 Respuesta usuario: {user_answer}")
```

---

## 🎉 ¡Sistema Completamente Funcional!

El sistema CAPTCHA está **100% implementado y probado**. Ahora tu aplicación tiene:

✅ **Protección contra bots**  
✅ **Prevención de ataques de fuerza bruta**  
✅ **Reducción de spam significativa**  
✅ **Experiencia de usuario fluida**  
✅ **Seguridad robusta**  

**¡Tu sistema de login ahora es mucho más seguro!** 🔐🚀
