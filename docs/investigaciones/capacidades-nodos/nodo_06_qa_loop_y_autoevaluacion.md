# 🔍 Nodo 06: QA Loop de Autoevaluación, Contact Sheet y Sync Firebase

## 🎯 Misión del Nodo
Evaluar el render final antes de darlo por válido, asegurando **cero errores de repetición visual**, contraste tipográfico impecable y sincronización con Firebase.

---

## 📋 Lista de Verificación Automatizada (Checklist de Calidad)

1. **Variedad Visual Estricta:**
   * Generación obligatoria de la tira de fotogramas mosaico (**Contact Sheet**).
   * Verificación algorítmica: El hash visual de fotogramas consecutivos no debe superar el 85% de similitud (evitar repetir el mismo fondo).
2. **Control Tipográfico:**
   * Comprobación de que ningún texto queda truncado o fuera de la zona segura (*Safe Title Margin 10%*).
   * Prohibición absoluta de cajas planas estilo drawbox.
3. **Calibración Acústica:**
   * Verificación de volumen RMS y ausencia de saturación (*clipping* a 0 dBFS).
4. **Sincronización Total en Firebase Firestore:**
   * Respaldo del proyecto con metadatos completos, enlaces de render y estado final (`COMPLETED` o `QA_FAILED`) en Firestore (`ayuda-emilio-83261`).
