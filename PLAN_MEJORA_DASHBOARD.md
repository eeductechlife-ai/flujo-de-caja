# 🎯 PLAN EXPERTO DE MEJORA DASHBOARD — Flujo de Caja

**Fecha:** 2026-08-11  
**Proyecto:** Limited Group S.A. — Evaluación Financiera de Inversión  
**Alcance:** Rediseño integral de presentación y experiencia de usuario

---

## 📊 ANÁLISIS DE ESTADO ACTUAL

### ✅ FORTALEZAS IDENTIFICADAS

| Aspecto | Evaluación | Nota |
|---------|-----------|------|
| **Funcionalidad Core** | Excelente | Carga Excel, recalcula modelos, exporta formatos |
| **Estructura de Datos** | Completa | Todos los KPIs necesarios presentes |
| **Interactividad Parámetros** | Buena | Sidebar editable con actualización en tiempo real |
| **Gráficos Base** | Correcta | Chart.js con datos correctos |
| **Responsividad** | Básica | Adapta a mobile pero imperfectamente |

### ⚠️ PROBLEMAS IDENTIFICADOS

| # | Categoría | Problema | Impacto | Severidad |
|---|-----------|----------|--------|-----------|
| 1 | **Tipografía** | System font stack genérico, sin jerarquía clara | Falta sofisticación, difícil escanear | Alta |
| 2 | **Color & Diseño** | Paleta básica, sin refinamiento cromático | Aspecto corporativo pero plano | Media |
| 3 | **Gráficos** | Sin grid, tooltips básicos, sin contexto visual | Pérdida de información al leer | Alta |
| 4 | **Información Visual** | KPIs dispersos, sin mini-gráficos de tendencia | No se ve el desempeño a primera vista | Alta |
| 5 | **Tablas** | Formateo básico, sin color-coding, números sin alineación | Difícil comparar valores | Media |
| 6 | **Layout Sidebar** | Muy denso, muchas secciones, scroll infinito | Fatiga visual, navegación lenta | Alta |
| 7 | **Tema Oscuro** | No soportado | Accesibilidad deficiente para usuarios nocturnos | Media |
| 8 | **Indicadores Clave** | Viabilidad como alerta simple, no prominent | No captura atención de decisión crítica | Alta |
| 9 | **Interactividad** | Falta feedback visual, sin animaciones suaves | Siente genérico, poco pulido | Media |
| 10 | **Resumen Ejecutivo** | Inexistente, hay que desplazarse para ver flujo | Falta contexto inmediato | Alta |

---

## 🎨 DISEÑO PLAN PROPUESTO

### **Color Token System**

```
LIGHT THEME:
- Primary Dark: #1a3a5c (corporativo profundo)
- Primary Mid: #2980b9 (interacción)
- Primary Light: #e8f4f8 (fondo claro)
- Success: #27ae60 (VAN positivo, TIR > WACC)
- Warning: #f39c12 (atención)
- Critical: #e74c3c (riesgo)
- Neutral 90%: #f8f9fa (fondo secundario)
- Neutral 70%: #d0d5dd (bordes)
- Neutral 20%: #2c3e50 (texto principal)
- Neutral 10%: #0f1419 (texto alto contraste)

DARK THEME:
- Primary Dark: #0f1b2e (fondo principal)
- Primary Mid: #3d9fd9 (interacción luminosa)
- Primary Light: #2d5a80 (acentos)
- Success: #4cbc6b (mejorado para contraste)
- Text Primary: #f0f2f5 (legible)
- Text Secondary: #a0a5b1 (dimmed)
- Borders: #374151 (sutil)
```

### **Tipografía Refinada**

```
DISPLAY (Headings): "Georgia", serif
- Peso: 700, 600
- Uso: Títulos principales, métricas críticas
- Propósito: Autoridad, profesionalismo

BODY (UI & Data): "Inter", -apple-system, sans-serif
- Peso: 400, 500, 600
- Uso: Párrafos, etiquetas, form
- Propósito: Legibilidad, limpieza

MONO (Valores numéricos): "Menlo", monospace
- Uso: Cantidades, tasas, porcentajes
- Propósito: Alineación perfecta, legibilidad numérica
```

### **Layout Concepto**

**3-Column Grid Dashboard:**
- **Columna 1 (Parámetros):** Sidebar comprimido con acordeón expandible
- **Columna 2 (Resumen + Gráficos):** KPIs summary + Waterfall/Area charts
- **Columna 3 (Análisis):** Tablas principales, exportación

**Visual Hierarchy:**
1. **Hero Metric:** VAN en grande con indicador de viabilidad
2. **Supporting KPIs:** TIR, Payback, IRR en mini-cards
3. **Gráficos Progresivos:** Waterfall → Cumulative → Sensibilidad
4. **Tablas de Detalle:** Estado de Resultados, FCL, Depreciación

---

## 🚀 MEJORAS ESPECÍFICAS

### **1. RESUMEN EJECUTIVO VISUAL**

```
┌─────────────────────────────────────────────────────────┐
│  VAN: $377.5M  │  TIR: 55.89%  │  PAYBACK: Año 6       │
│  ✅ PROYECTO VIABLE                                     │
│  Genera $377.5M en valor presente a 13% WACC            │
└─────────────────────────────────────────────────────────┘
```

**Implementación:**
- Fondo con gradiente sutil
- Badge de viabilidad con ícono y color dinámico
- Mini-gráfico de tendencia VAN (sparkline)
- Métricas principales en columnas balanceadas

### **2. REDISEÑO KPI CARDS**

**De:**
```
┌──────────────────┐
│ Inversión Total  │
│ $122.0M          │
│ Capex + KW       │
└──────────────────┘
```

**A:**
```
┌─────────────────────────────┐
│ INVERSIÓN INICIAL           │
│ $122.0M                     │
│ ▁▂▃▄▅▄▃▂▁  (sparkline)     │
│ vs caso base: -2.1%         │
└─────────────────────────────┘
```

**Cambios:**
- Fondo con color de marca suave
- Sparkline de 6 períodos
- Comparativa con caso base
- Borde izquierdo retirado (más moderno)
- Efecto hover con elevation

### **3. GRÁFICOS MEJORADOS**

**Flujo de Caja Libre - De Bar Simple a Waterfall:**
```
Año 0: Inversión -$125M
  ↓
Año 1: FCL +$15M
  ↓
Año 2: FCL +$18M
  ↓
...
Año 6: Acumulado = +$50M
```

**Beneficios:**
- Visualiza cómo se recupera inversión
- Muestra cada año como escalón
- Más intuitivo que barras separadas
- Resalta los años positivos

**Gráfico Acumulado - De Línea Simple a Área Rellena:**
- Gradiente de color de rojo (negativo) a verde (positivo)
- Grid visible sutilmente
- Tooltip enriquecido con info de sensibilidad
- Punto de quiebre (Payback) marcado

**Agregar - Heatmap de Sensibilidad:**
```
                Precio -10%  Base  Precio +10%
Cantidad -20%    [-M]       [M]      [M]
Cantidad Base    [-M]     [377.5M]  [M]
Cantidad +20%    [-M]       [M]      [M]
```

### **4. TABLAS REDISEÑADAS**

**Mejoras:**
- Tipografía monospace para números (perfect alignment)
- Alternancia de filas con contraste mejorado
- Filas totales con background prominente + número en negrilla
- Columnas de signos (+/-) visuales
- Tooltip en header con descripción de concepto

**Ejemplo:**
```
┌─────────────────────┬──────────┬──────────┬──────────┐
│ CONCEPTO            │ Año 0    │ Año 1    │ Año 2    │
├─────────────────────┼──────────┼──────────┼──────────┤
│ INGRESOS            │      —   │ $60.0M   │ $60.0M   │
│ (-) Costos variables│      —   │ -$45.0M  │ -$45.0M  │
│ (-) Costos fijos    │      —   │ -$2.8M   │ -$2.8M   │
├─────────────────────┼──────────┼──────────┼──────────┤
│ EBITDA              │      —   │ $12.2M   │ $12.2M   │
└─────────────────────┴──────────┴──────────┴──────────┘
```

### **5. SIDEBAR REORGANIZADO**

**Estructura Acordeón:**
```
▼ 📤 CARGAR ARCHIVO (siempre visible)
  [Seleccionar archivo] [Restaurar caso base]

▶ 🏭 OPERACIÓN
▶ 💰 COSTOS VARIABLES
▶ 🏢 COSTOS FIJOS
▶ 💵 FINANZAS
```

**Beneficios:**
- Scroll reducido 60%
- Fácil encontrar sección
- Expandir solo lo que necesitas
- Mejor en mobile

### **6. TEMA OSCURO COMPLETO**

**Sistema de Tokens Dual:**
- CSS variables para colores
- Redefinición en `@media (prefers-color-scheme: dark)`
- Contraste mantenido en ambos temas
- Colores semánticos (verde éxito, rojo riesgo) funcionan en ambos

### **7. INDICADORES VISUALES MEJORADOS**

**Badges de Estado:**
```
✅ VIABLE          ⚠️  MARGINAL      ❌ NO VIABLE
Verde, Grande      Naranja, Med.     Rojo, Prominente
```

**Mini Indicadores en KPIs:**
```
VAN: $377.5M  ↗ +12.3% vs anterior
TIR: 55.89%   ↘ -2.1% vs anterior
```

---

## 📋 ROADMAP DE IMPLEMENTACIÓN

### **FASE 1: Fundamentos (2-3 horas)**
- [ ] Sistema de colores con CSS variables
- [ ] Tipografía mejorada
- [ ] Tema oscuro base
- [ ] Reordenar sidebar con acordeón

### **FASE 2: Gráficos (2-3 horas)**
- [ ] Waterfall chart flujo de caja
- [ ] Área chart acumulado con gradiente
- [ ] Tooltips enriquecidos
- [ ] Grid visible en gráficos

### **FASE 3: Información (1-2 horas)**
- [ ] Rediseño KPI cards con sparklines
- [ ] Resumen ejecutivo hero
- [ ] Badges de viabilidad
- [ ] Mini-indicadores de cambio

### **FASE 4: Pulido (1-2 horas)**
- [ ] Tablas con monospace
- [ ] Animaciones suaves
- [ ] Responsive refinado
- [ ] Testing completo

**Total estimado:** 6-10 horas de desarrollo

---

## 🎯 MÉTRICAS DE ÉXITO

| Métrica | Antes | Objetivo |
|---------|-------|----------|
| **Tiempo para ver VAN** | 2+ clics | Inmediato (hero) |
| **Escaneo sidebar** | 30+ seg | <5 seg (acordeón) |
| **Comprensión flujo** | Requiere gráficos | Waterfall intuitiva |
| **Accesibilidad** | Light solo | Light + Dark |
| **Mobile usability** | Difícil | Óptimo |

---

## 🚀 PRÓXIMO PASO

Proceder a **FASE 1** implementando el sistema de diseño base y mejorando estructura visual fundamental.
