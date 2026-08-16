# 📊 Visualización de Datos, HUDs y Prevención de Layout Shift

> **Área:** `docs/investigaciones/remotion_motion_graphics/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

## 📌 1. El Problema del Layout Shift en Contadores
Las tipografías proporcionales varían el ancho de cada glifo numérico (el '1' es más angosto que el '8'), provocando vibración tipográfica en cronómetros y contadores rápidos.

## 🛠️ 2. La Regla `tabular-nums`
Es obligatorio aplicar:
```css
font-variant-numeric: tabular-nums;
font-feature-settings: "tnum";
```

## 💻 3. Componente de Cronómetro y Barra de Progreso Determinista
Contador numérico interpolado cuadro a cuadro con barras de progreso con `interpolate(frame, [0, 100], [0, 100], { extrapolateRight: 'clamp' })`.
