# 🐾 Mascotas App - Backend

![CI Tests](https://github.com/MascotasBogota/LogIn_backend/workflows/CI%20Tests/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![Swagger](https://img.shields.io/badge/swagger-3.0-brightgreen.svg)

API RESTful completa para sistema de gestión de usuarios y perfiles desarrollada con Flask, MongoDB y documentación Swagger/OpenAPI.

## 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- **Autenticación JWT** - Sistema seguro de login/registro con tokens de 30 días
- **Autenticación Google** - Integración con Google Sign-In OAuth2
- **Restablecimiento de contraseñas** - Sistema completo con tokens de verificación
- **Encriptación bcrypt** - Hashing seguro de contraseñas
- **Rate Limiting** - Protección contra spam (200 req/día, 50 req/hora)

### 👤 Gestión de Perfiles
- **CRUD completo** - Crear, leer, actualizar perfiles de usuario
- **Subida de imágenes** - Upload de fotos de perfil con validación (JPG, PNG, GIF, máx 5MB)
- **Cambio de contraseñas** - Actualización segura de credenciales
- **Sistema de reputación** - Puntuación y ranking de usuarios
- **Información pública** - Endpoints para obtener datos básicos de usuarios

### 🛠️ Funcionalidades Técnicas
- **Documentación Swagger/OpenAPI** - API interactiva en `/api/docs/`
- **Validación robusta** - Patrón Chain of Responsibility para validaciones
- **MongoDB Atlas** - Base de datos en la nube con esquemas optimizados
- **Auditoría completa** - Logging de todas las operaciones en `logs/audit.log`
- **Telemetría** - Métricas con OpenTelemetry y Prometheus
- **CORS configurado** - Soporte para múltiples frontends
- **Tests automatizados** - Suite completa de tests con pytest
- **CI/CD** - GitHub Actions para tests automáticos

## 📋 Requisitos

- Python 3.9+
- MongoDB Atlas (o MongoDB local)
- Git

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/MascotasBogota/LogIn_backend.git
cd LogIn_backend
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
Crear archivo `.env` con:
```env
# Base de datos
MONGO_URI=tu_cadena_de_conexion_mongodb_atlas

# Seguridad
JWT_SECRET=tu_clave_secreta_super_segura

# Servidor
PORT=5000
FLASK_ENV=development

# Google OAuth (opcional)
GOOGLE_CLIENT_ID=tu_google_client_id.apps.googleusercontent.com

# Email (para restablecimiento de contraseñas)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
```

## 📚 Documentación Interactiva

### Swagger/OpenAPI UI
Una vez iniciada la aplicación, accede a la documentación interactiva:

- **🌐 Swagger UI**: `http://localhost:5000/api/docs/`
- **📋 Schema JSON**: `http://localhost:5000/api/swagger.json`

### Características de Swagger:
- ✅ **Prueba endpoints en vivo** directamente desde el navegador
- ✅ **Autenticación JWT integrada** - botón "Authorize" 
- ✅ **Validación automática** de requests y responses
- ✅ **Ejemplos incluidos** para todos los endpoints
- ✅ **Documentación detallada** con códigos de error
- ✅ **Soporte para upload de archivos** (multipart/form-data)

### Cómo usar Swagger:
1. Inicia el servidor con `python start_swagger.py`
2. Ve a `http://localhost:5000/api/docs/`
3. Para endpoints protegidos:
   - Registra/loguea un usuario
   - Copia el token JWT de la respuesta
   - Haz clic en **"Authorize"** en la parte superior
   - Ingresa: `Bearer <tu_token_aquí>`
4. ¡Prueba cualquier endpoint directamente desde la interfaz!

## 🧪 Testing

### Ejecutar todos los tests:
```bash
python -m pytest -v
```

### Ejecutar tests específicos:
```bash
python -m pytest tests/test_basic.py -v
python -m pytest tests/test_user_controller.py -v
python -m pytest tests/test_profile_controller.py -v
python -m pytest tests/test_password_reset.py -v
python -m pytest tests/test_file_upload.py -v
```

### Tests con cobertura:
```bash
pip install pytest-cov
python -m pytest --cov=. --cov-report=html
```

### Suite de Tests Incluida:
- ✅ **Tests básicos** - Funcionalidad core de la API
- ✅ **Tests de usuario** - Registro, login, validaciones
- ✅ **Tests de perfil** - CRUD completo, subida de archivos
- ✅ **Tests de restablecimiento** - Flow completo de reset de password
- ✅ **Tests de archivos** - Upload, validación, storage

## 🔍 Monitoreo y Observabilidad

### Logging y Auditoría
- **Audit Log**: `logs/audit.log` - Registro completo de operaciones
- **Console Logging**: Logs estructurados en tiempo real
- **Error Tracking**: Captura y logging de excepciones

### Métricas (OpenTelemetry + Prometheus)
```bash
# Métricas disponibles en /metrics
http_requests_total          # Total de requests HTTP
http_request_duration_seconds # Latencia de requests
http_errors_total           # Total de errores HTTP
```

### Rate Limiting
- **200 requests/día** por IP
- **50 requests/hora** por IP
- Protección automática contra spam y abuso

## 🛡️ Seguridad

### Características de Seguridad Implementadas:
- ✅ **JWT Tokens** con expiración de 30 días
- ✅ **Bcrypt Hashing** para contraseñas
- ✅ **Input Validation** robusta en todos los endpoints
- ✅ **CORS configurado** para dominios específicos
- ✅ **Rate Limiting** para prevenir ataques
- ✅ **File Upload Validation** (tipo, tamaño, contenido)
- ✅ **Audit Logging** completo de operaciones
- ✅ **Error Handling** sin exposición de información sensible

### Google OAuth2 Integration:
- Login/registro automático con cuentas Google
- Validación de tokens ID de Google
- Creación automática de usuarios nuevos

## 🚀 Ejecutar la aplicación

### Método rápido (recomendado):
```bash
python start_swagger.py
```

### Método manual:
```bash
python app.py
```

### URLs disponibles:
- **🏠 API Base**: `http://localhost:5000`
- **📚 Documentación Swagger**: `http://localhost:5000/api/docs/`
- **📋 Schema JSON**: `http://localhost:5000/api/swagger.json`
- **🔗 API Endpoints**: `http://localhost:5000/api`

## 📡 API Endpoints

### 🔓 Endpoints Públicos

#### Autenticación (`/api/auth` y `/api/users`)
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/google_login` - Login con Google OAuth2
- `POST /api/auth/forgot-password` - Solicitar restablecimiento de contraseña
- `POST /api/auth/verify-token` - Verificar token de restablecimiento
- `POST /api/auth/reset-password` - Restablecer contraseña

#### Información Pública
- `GET /api/profile/user/<user_id>` - Obtener información básica de usuario
- `GET /` - Estado de la API
- `GET /api` - Test del endpoint API

### 🔒 Endpoints Protegidos (Requieren JWT)

#### Gestión de Perfil (`/api/profile`)
- `GET /api/profile/` - Obtener perfil del usuario autenticado
- `PUT /api/profile/` - Actualizar perfil
- `PUT /api/profile/password` - Cambiar contraseña
- `POST /api/profile/upload-picture` - Subir foto de perfil

#### Sistema de Reputación
- `PATCH /api/profile/<user_id>/reputation` - Actualizar reputación de usuario

#### Archivos Estáticos
- `GET /static/uploads/<filename>` - Servir imágenes de perfil subidas

## 📝 Ejemplos de Uso

### Registro de Usuario:
```json
POST /api/auth/register
Content-Type: application/json

{
  "full_name": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "password": "MiPassword123"
}
```

### Login:
```json
POST /api/auth/login
Content-Type: application/json

{
  "email": "juan@ejemplo.com",
  "password": "MiPassword123"
}
```

### Login con Google:
```json
POST /api/auth/google_login
Content-Type: application/json

{
  "google_id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Actualizar Perfil (con JWT):
```json
PUT /api/profile/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "full_name": "Juan Carlos Pérez",
  "username": "juanperez",
  "phoneNumber": "+573001234567",
  "address": "Calle 123 #45-67, Bogotá",
  "gender": "male"
}
```

### Subir Foto de Perfil:
```bash
POST /api/profile/upload-picture
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: [imagen.jpg]
```

### Restablecimiento de Contraseña:
```json
# 1. Solicitar restablecimiento
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "juan@ejemplo.com"
}

# 2. Verificar token (opcional)
POST /api/auth/verify-token
Content-Type: application/json

{
  "token": "abc123def456..."
}

# 3. Restablecer contraseña
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "abc123def456...",
  "password": "NuevaPassword123"
}
```

## 🏗️ Arquitectura

```
LogIn_backend/
├── app.py                    # Aplicación principal Flask
├── start_swagger.py          # Script de inicio con Swagger
├── requirements.txt          # Dependencias del proyecto
├── pytest.ini              # Configuración de tests
├── Dockerfile              # Containerización
├──
├── api/                     # API con documentación Swagger/OpenAPI
│   ├── __init__.py         # Configuración principal de la API
│   ├── auth_api.py         # Endpoints de autenticación documentados
│   ├── profile_api.py      # Endpoints de perfil documentados
│   └── swagger_models.py   # Modelos de datos para Swagger
├──
├── config/                 # Configuración de la aplicación
│   ├── database.py        # Configuración de MongoDB
│   └── __init__.py
├──
├── controllers/            # Lógica de negocio
│   ├── auth_controller.py     # Controlador unificado de autenticación
│   ├── user_controller.py     # Gestión de usuarios
│   ├── profile_controller.py  # Gestión de perfiles
│   ├── password_reset_controller.py # Restablecimiento de contraseñas
│   ├── reputation_controller.py     # Sistema de reputación
│   └── __init__.py
├──
├── handlers/               # Validadores (Chain of Responsibility)
│   ├── user_creation_handler.py      # Validación de creación de usuarios
│   ├── profile_validation_handler.py # Validación de perfiles
│   └── __init__.py
├──
├── models/                # Modelos de datos MongoDB
│   ├── user.py           # Modelo de usuario
│   ├── password_reset_token.py # Modelo de tokens de reset
│   └── __init__.py
├──
├── routes/               # Rutas de la API (compatibilidad)
│   ├── user_routes.py          # Rutas de usuarios
│   ├── profile_routes.py       # Rutas de perfil
│   ├── password_reset_routes.py # Rutas de restablecimiento
│   └── __init__.py
├──
├── services/             # Servicios y utilidades
│   ├── audit_service.py        # Servicio de auditoría
│   ├── email_service.py        # Servicio de envío de emails
│   ├── file_upload_service.py  # Servicio de subida de archivos
│   ├── profile_validation.py   # Validación de perfiles
│   ├── user_creation_validation.py # Validación de usuarios
│   └── __init__.py
├──
├── utils/                # Utilidades generales
│   ├── telemetry.py     # Métricas con OpenTelemetry/Prometheus
│   ├── serialization.py # Utilidades de serialización
│   ├── handler_template.py # Template para handlers
│   └── __init__.py
├──
├── tests/               # Tests automatizados
│   ├── test_basic.py
│   ├── test_user_controller.py
│   ├── test_profile_controller.py
│   ├── test_password_reset.py
│   ├── test_file_upload.py
│   └── __init__.py
├──
├── logs/               # Archivos de log
│   └── audit.log      # Log de auditoría
├──
└── uploads/           # Archivos subidos (imágenes de perfil)
```

### 🎯 Patrones de Diseño Implementados
- **Chain of Responsibility** - Validadores en cascada
- **Factory Pattern** - Creación de la aplicación Flask
- **Repository Pattern** - Acceso a datos con MongoDB
- **Service Layer** - Lógica de negocio en servicios
- **MVC Architecture** - Separación de responsabilidades

## 🔄 CI/CD

Este proyecto incluye GitHub Actions que automáticamente:

- ✅ **Tests Automáticos** en Python 3.9, 3.10, y 3.11
- ✅ **Verificación de Calidad** de código
- ✅ **Reportes de Cobertura** de tests
- ✅ **Validación de Swagger** schema
- ✅ **Checks de Seguridad** básicos
- ✅ **Ejecución en cada** push y pull request

## 🐳 Docker Support

### Dockerfile incluido para containerización:
```bash
# Construir imagen
docker build -t mascotas-backend .

# Ejecutar contenedor
docker run -p 5000:5000 mascotas-backend
```

## 📖 Documentación Adicional

- **📋 [Frontend Integration Guide](FRONTEND_INTEGRATION_GUIDE.md)** - Guía completa para integración frontend
- **📚 [Swagger Documentation](SWAGGER_DOCUMENTATION.md)** - Documentación técnica de Swagger
- **🎉 [Swagger Completed](SWAGGER_COMPLETED.md)** - Status de implementación
- **📄 [User Basic Info Endpoint](USER_BASIC_INFO_ENDPOINT.md)** - Documentación específica

## 🚀 Features Avanzadas

### Chain of Responsibility Pattern
Sistema de validación en cascada para:
- Validación de datos de entrada
- Verificación de reglas de negocio  
- Sanitización de datos
- Logging automático

### File Upload System
- **Tipos soportados**: JPG, PNG, GIF
- **Tamaño máximo**: 5MB
- **Validación**: Tipo MIME y contenido real
- **Storage**: Sistema local con URLs públicas
- **Seguridad**: Validación de archivos maliciosos

### Reputation System
- Sistema de puntuación para usuarios
- Endpoints para actualizar reputación
- Tracking de cambios en audit log

## 🎯 Próximas Funcionalidades Planeadas

- [ ] **OAuth2 con más proveedores** (Facebook, GitHub)
- [ ] **Sistema de roles y permisos** avanzado
- [ ] **API Versioning** (v2)
- [ ] **WebSocket support** para real-time
- [ ] **Caching con Redis**
- [ ] **Background jobs** con Celery
- [ ] **Notificaciones push**

## 🤝 Contribuir

1. Hacer fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Hacer commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👨‍💻 Autor

David Alejandro Cifuentes Gonzalez - [@dcifuentesg](https://github.com/dcifuentesg)
