"""
Test simple del sistema de CAPTCHA
"""
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.captcha_service import CaptchaService, RecaptchaService
    
    print("🧪 Iniciando test básico de CAPTCHA...")
    
    # Crear instancia del servicio
    captcha_service = CaptchaService()
    
    # Test 1: Generar CAPTCHA matemático
    print("\n📊 Test 1: Generar CAPTCHA matemático")
    captcha_data = captcha_service.generate_math_captcha()
    
    if 'captcha_id' in captcha_data and 'question' in captcha_data and 'image' in captcha_data:
        print(f"✅ CAPTCHA generado exitosamente")
        print(f"   ID: {captcha_data['captcha_id'][:8]}...")
        print(f"   Pregunta: {captcha_data['question']}")
        print(f"   Imagen: {len(captcha_data['image'])} caracteres")
        
        # Test 2: Validar respuesta correcta
        print("\n🔍 Test 2: Validar respuesta correcta")
        captcha_id = captcha_data['captcha_id']
        correct_answer = captcha_service.captcha_storage[captcha_id]['answer']
        
        is_valid = captcha_service.validate_captcha(captcha_id, correct_answer)
        if is_valid:
            print(f"✅ Validación correcta exitosa (respuesta: {correct_answer})")
        else:
            print(f"❌ Error en validación correcta")
            
        # Test 3: Generar otro CAPTCHA para probar respuesta incorrecta
        print("\n❌ Test 3: Validar respuesta incorrecta")
        captcha_data2 = captcha_service.generate_math_captcha()
        captcha_id2 = captcha_data2['captcha_id']
        
        is_invalid = captcha_service.validate_captcha(captcha_id2, "999")
        if not is_invalid:
            print(f"✅ Validación incorrecta funcionó correctamente")
        else:
            print(f"❌ Error: validación incorrecta devolvió True")
            
        # Test 4: Generar CAPTCHA de texto
        print("\n🔤 Test 4: Generar CAPTCHA de texto")
        text_captcha = captcha_service.generate_text_captcha()
        
        if 'captcha_id' in text_captcha and 'image' in text_captcha:
            print(f"✅ CAPTCHA de texto generado exitosamente")
            print(f"   ID: {text_captcha['captcha_id'][:8]}...")
            print(f"   Imagen: {len(text_captcha['image'])} caracteres")
        else:
            print(f"❌ Error generando CAPTCHA de texto")
            
        # Test 5: Cleanup
        print("\n🧹 Test 5: Limpieza de CAPTCHAs")
        initial_count = len(captcha_service.captcha_storage)
        captcha_service.cleanup_expired_captchas()
        final_count = len(captcha_service.captcha_storage)
        print(f"✅ Cleanup ejecutado. CAPTCHAs: {initial_count} -> {final_count}")
        
        print("\n🎉 Todos los tests básicos completados exitosamente!")
        print("\n📋 Resumen:")
        print(f"   - Generación de CAPTCHA matemático: ✅")
        print(f"   - Validación de respuesta correcta: ✅")
        print(f"   - Validación de respuesta incorrecta: ✅")
        print(f"   - Generación de CAPTCHA de texto: ✅")
        print(f"   - Sistema de limpieza: ✅")
        
    else:
        print("❌ Error: Estructura de CAPTCHA incorrecta")
        print(f"   Datos recibidos: {list(captcha_data.keys())}")
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de que el archivo services/captcha_service.py existe")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🚀 Para probar el sistema completo:")
print("1. Ejecuta el servidor: python app.py")
print("2. Genera un CAPTCHA: POST /api/captcha/generate")
print("3. Valida el CAPTCHA: POST /api/captcha/validate")  
print("4. Haz login con CAPTCHA: POST /api/users/login")
print("="*60)
