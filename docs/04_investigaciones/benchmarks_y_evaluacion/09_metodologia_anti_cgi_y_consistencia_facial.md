# 🎬 Investigación Técnica: Erradicación del Look CGI/Plástico & Prevención del Face Morphing en Vídeo IA

> **Ubicación Permanente:** `/home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/09_metodologia_anti_cgi_y_consistencia_facial.md`  
> **Área:** VideoPro Studio v5.0 Ultra / Prompt Engineering & Temporal Consistency Architecture  
> **Fecha:** 16 de Agosto de 2026  
> **Autores:** Hermes AI / VideoPro Research Team  

---

## 1. Diagnóstico del "Efecto Plástico / CGI" (Synthetic Texture Trap)

### ¿Por qué la IA produce texturas plásticas, irreales y artificialmente brillantes?

1. **La Trampa de los "Buzzwords" de Motores 3D:**
   - Términos comunes como `"Unreal Engine 5"`, `"8K"`, `"hyper-realistic"`, `"octane render"`, `"photorealistic"` o `"glowing neon"` están fuertemente asociados en el dataset de entrenamiento a renders de videojuegos y modelos poligonales 3D con shaders de plástico y suavizado artificial (*airbrushed smoothness*).
2. **Falta de Física Óptica y Grano Analógico:**
   - Los modelos generativos tienden por defecto a limpiar el ruido de alta frecuencia. Sin especificaciones ópticas concretas, generan superficies perfectamente lisas, pieles sin poros ni vello y reflejos especulares infinitos que el cerebro humano identifica inmediatamente como "CGI".

---

## 2. El Protocolo de Cine Orgánico 35mm (Anti-CGI Prompting)

Para obligar a FLUX 3, NanoBanana Pro 2 y los motores de difusión a renderizar texturas fotográficas orgánicas, se debe sustituir la jerga sintética por **parámetros físicos de cinematografía real**:

### 📐 Matriz de Sustitución Léxica

| ❌ Término Prohibido (Produce CGI / Plástico) | ✅ Término Cinematográfico Orgánico (Física Real) |
| :--- | :--- |
| `hyper-realistic`, `8k`, `photorealistic` | `Shot on ARRI Alexa 65`, `Kodak Vision3 500T 5219 35mm film stock` |
| `Unreal Engine 5`, `octane render` | `Panavision C-Series Anamorphic prime lenses, f/1.8` |
| `smooth glowing skin`, `perfect face` | `visible skin pores, fine skin texture, subtle organic blemishes, micro-sweat droplets` |
| `glowing neon everywhere`, `colorful lights` | `directional tungsten practical lighting, muted atmospheric teal backlight, realistic roll-off highlight clipping` |
| `ultra clear digital look` | `authentic 35mm film grain, subtle optical halation, natural anamorphic horizontal flares` |
| `plastic metal surfaces` | `weathered concrete, oxidized matte aluminum, damp asphalt texture, realistic light diffusion` |

---

## 3. Diagnóstico del "Face Morphing" e Inconsistencia Facial

### ¿Por qué cambian las caras cuando se mueve la cámara?

1. **Salto de Escala Espacial en una Sola Toma (Latent Resolution Drift):**
   - En una toma larga de 15 a 20 segundos que intenta ir desde un plano aéreo general (150m) hasta el nivel de la calle (1.5m), los rostros humanos en el plano general ocupan apenas **8×8 píxeles**.
   - A medida que la cámara desciende a gran velocidad, los bloques de atención temporal del modelo de difusión deben **inventar y mutar la geometría facial desde la nada** en cada fotograma intermedio, generando caras deformes, ojos derretidos y cambio continuo de identidades (*Face Drift*).
2. **Sobrecarga de Vectores de Movimiento:**
   - Forzar simultáneamente avance rápido (*dolly forward*) + giro angular (*pan*) + descenso (*crane down*) entre una multitud desordena las trayectorias de flujo óptico en la difusión temporal.

---

## 4. La Solución Técnica Definitiva: Arquitectura de Montaje Multi-Plano

En lugar de obligar al modelo a resolver una toma continua imposible con deformaciones de rostros, el estándar cinematográfico profesional divide la secuencia en **planos dedicados con gramática de cámara limpia**:

```
[Plano 1: Aéreo General] ───(Corte Rítmico)───> [Plano 2: Detalle Macro] ───(Corte)───> [Plano 3: Tracking de Espaldas]
150m Gran Angular 35mm                           85mm f/1.4 Sujeto Estático              50mm Seguimiento Trasero / Perfil
(Sin caras visibles)                            (Rostro bloqueado al 100%)              (Cero morphing frontal)
```

### Reglas Maestras para Erradicar el Face Morphing:

1. **Regla de Escenificación (Back / Profile Staging):**
   - En tomas de dron o cámara en movimiento rápido a través de multitudes, los personajes deben encuadrarse **de espaldas (caminando en la dirección del movimiento), de perfil o con siluetas y capuchas transparentes**. Esto elimina el 100% de las deformaciones frontales.
2. **Plano Detalle / Macro Estático para Rostros:**
   - Si se requiere ver un rostro humano cibernético con micro-detalle (ojos, HUD, implantes), debe generarse en un **Plano Detalle (Close-Up de 85mm o 100mm) con movimiento de cámara mínimo (sutil drift o respiración de foco)**. Al no haber cambio de distancia, la geometría facial se mantiene inmutable.
3. **Un Solo Vector de Movimiento por Plano:**
   - Plano 1: Solo descenso vertical.
   - Plano 2: Solo avance frontal recto (*straight tracking*).
   - Plano 3: Solo elevación hacia el cielo (*pitch-up*).
4. **Montaje Sincronizado en Transitorios:**
   - Ensamblar los planos individuales con cortes secos en FFmpeg sobre los golpes de bombo y caja de la música (*beat-locked cuts*), emulando el montaje cinematográfico de Hollywood.

---

## 5. Estructura Canónica del Prompt de Cine Orgánico

```text
[Especificación de Cámara y Óptica] + [Sujeto con Texturas Físicas] + [Entorno y Dirección de Luz] + [Textura de Superficie y Grano Analógico]
```

### Ejemplo de Prompt Orgánico 35mm (Plano Detalle Sin CGI):
```text
35mm film photograph, shot on ARRI Alexa 65 with Panavision Primo 70 anamorphic lens (85mm f/1.4). Close-up portrait of a tired Japanese cybernetic pedestrian in Shibuya 2326 at night during gentle rain. Natural skin texture with visible pores, subtle facial blemishes, authentic moisture and rain droplets running down the skin. Fine chrome mechanical temple implant with realistic matte metal brushing. Directional soft tungsten streetlight illuminating the side of the face, deep moody shadows, muted teal and orange city lights blurred into soft oval anamorphic bokeh in the background. Subtle organic 35mm film grain, Kodak Vision3 500T color science, no airbrushed smoothness, cinematic authentic realism.
```
