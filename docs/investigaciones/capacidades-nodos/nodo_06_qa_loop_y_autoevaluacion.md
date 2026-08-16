# 📘 NODO 06: Bucle de Autoevaluación y Control de Calidad (Self-Eval QA Loop)

> **Rol del Nodo:** Inspeccionar silenciosamente el vídeo compilado antes de la entrega final, detectando y corrigiendo anomalías de forma autónoma.

---

## 🎯 Protocolo de Inspección Visual (`timeline_view`):

1. **Generación de Hoja de Contactos (Contact Sheet / Tira de Fotogramas):**
   * Extracción de mosaico 3x3 o 4x4 de fotogramas clave a lo largo de la línea de tiempo.

2. **Criterios de Validación Estricta:**
   * **Auditoría de Textos:** Verificar que no existan textos superpuestos, recortados por los márgenes de pantalla o ilegibles sobre fondos brillantes.
   * **Auditoría de Movimiento:** Confirmar que no existen fotogramas congelados ni saltos bruscos (*jump cuts*) sin transición.
   * **Auditoría de Sincronismo:** Validar que el final del vídeo coincide exactamente con el último frame del audio del usuario.

3. **Bucle de Auto-Corrección:**
   * Si la inspección detecta anomalías, el agente reajusta el código de la composición en Remotion o los filtros de FFmpeg y re-renderiza (límite de 3 iteraciones autónomas).
