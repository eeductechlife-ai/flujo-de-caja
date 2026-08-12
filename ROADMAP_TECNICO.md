# 🗺️ ROADMAP TÉCNICO — Dashboard Flujo de Caja

**Estado Actual:** Fases 1-2 completadas (✅)  
**Próximas:** Fases 3-4 (2-4 horas)

---

## 📋 FASE 3: GRÁFICOS AVANZADOS & ANÁLISIS

### **3.1 Waterfall Chart — Flujo de Caja**

**Objetivo:** Reemplazar bar chart simple por visualización waterfall que muestre cómo se recupera la inversión.

**Implementación:**

```javascript
// Usar Chart.js con plugin waterfall o crear manual con canvas
// Mostrar: Inversión → Año 1 → Año 2 → ... → Acumulado

function renderizarWaterfall() {
  const fc = estado.resultado.flujo_caja;
  const cfg = estado.resultado.config;
  
  // Transformar datos para waterfall
  const data = {
    labels: ['Año 0', 'Año 1', 'Año 2', ...],
    datasets: [{
      type: 'bar',
      label: 'Flujo de Caja',
      data: fc.flujo_con_vt,
      // Configurar como waterfall
      backgroundColor: flujoData.map(v => v >= 0 ? '#27ae60' : '#e74c3c'),
      borderRadius: 4,
      borderSkipped: false
    }]
  };
}
```

**Tiempo estimado:** 60-90 minutos  
**Dependencias:** Chart.js (ya presente)

---

### **3.2 Área Chart Mejorado — FCL Acumulado**

**Objetivo:** Cambiar línea simple a área con gradiente y grid visible.

**Cambios:**

```javascript
// Chart.js ya soporta esto
backgroundColor: 'linear-gradient(180deg, #27ae60 0%, transparent 100%)',
fill: true,
tension: 0.4,

// Agregar grid
options: {
  scales: {
    y: {
      grid: {
        drawBorder: true,
        color: 'rgba(200,200,200,0.1)',
        lineWidth: 1
      }
    }
  }
}
```

**Tiempo estimado:** 30-45 minutos  
**Impacto:** Visual + Información

---

### **3.3 Heatmap de Sensibilidad**

**Objetivo:** Mostrar cómo varían el VAN y TIR con cambios en precios y cantidades.

**Estructura:**

```html
<table class="sensitivity-heatmap">
  <tr>
    <td></td>
    <td>Precio -10%</td>
    <td>Precio Base</td>
    <td>Precio +10%</td>
  </tr>
  <tr>
    <td>Cant -20%</td>
    <td style="bg: #ffcccc">$228M</td>
    <td style="bg: #e6f2ff">$377.5M</td>
    <td style="bg: #ccffcc">$376M</td>
  </tr>
  <!-- ... -->
</table>
```

**Cálculo:**

```python
# En Python (model.py o nuevo archivo sensitivity.py)
def calcular_sensibilidad():
  """Calcula VAN para diferentes escenarios"""
  rangos = {
    'precio': [-0.2, -0.1, 0, 0.1, 0.2],
    'cantidad': [-0.2, -0.1, 0, 0.1, 0.2]
  }
  
  resultados = {}
  for pct_precio in rangos['precio']:
    for pct_cant in rangos['cantidad']:
      # Ajustar config
      # Ejecutar modelo
      # Guardar VAN
  
  return resultados
```

**Tiempo estimado:** 120-150 minutos  
**Impacto:** Análisis + Decisión

---

### **3.4 Tooltips Enriquecidos**

**Objetivo:** Mostrar información adicional al pasar mouse sobre gráficos.

**Implementación:**

```javascript
tooltips: {
  enabled: true,
  mode: 'index',
  backgroundColor: 'rgba(0,0,0,0.8)',
  titleColor: '#fff',
  bodyColor: '#fff',
  callbacks: {
    label: function(context) {
      let label = context.dataset.label || '';
      if (label) label += ': ';
      
      const value = context.parsed.y;
      label += `$${(value/1e6).toFixed(1)}M`;
      
      // Agregar delta año anterior
      if (context.dataIndex > 0) {
        const prev = context.dataset.data[context.dataIndex - 1];
        const delta = ((value - prev) / prev * 100).toFixed(1);
        label += ` (${delta > 0 ? '+' : ''}${delta}%)`;
      }
      
      return label;
    }
  }
}
```

**Tiempo estimado:** 45-60 minutos  
**Impacto:** UX

---

## 📊 FASE 4: PULIDO & OPTIMIZACIÓN

### **4.1 Selector de Tema Oscuro/Claro**

**Objetivo:** Permitir usuario elegir entre tema claro y oscuro.

**Implementación:**

```html
<!-- Botón en header -->
<button id="theme-toggle" onclick="toggleTheme()">
  <span id="theme-icon">🌙</span>
</button>

<style>
:root[data-theme="dark"] {
  --primary-dark: #0f1b2e;
  --text-primary: #f0f2f5;
  /* ... */
}
</style>

<script>
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  
  // Cambiar ícono
  document.getElementById('theme-icon').textContent = 
    next === 'dark' ? '☀️' : '🌙';
}

// En init, restaurar tema guardado
function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
  }
}
</script>
```

**Tiempo estimado:** 45-60 minutos  
**Impacto:** Accesibilidad + UX

---

### **4.2 Sparklines Reales en KPI Cards**

**Objetivo:** Reemplazar sparklines genéricas con gráficos reales de tendencia.

**Implementación:**

```javascript
// Para cada KPI, graficar últimos 6 períodos
function crearSparkline(elemento, datos) {
  const canvas = document.createElement('canvas');
  elemento.appendChild(canvas);
  
  new Chart(canvas, {
    type: 'line',
    data: {
      labels: ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'],
      datasets: [{
        data: datos,
        borderColor: '#27ae60',
        backgroundColor: 'transparent',
        borderWidth: 1,
        fill: false,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { x: { display: false }, y: { display: false } },
      plugins: { legend: { display: false } }
    }
  });
}
```

**Tiempo estimado:** 60-90 minutos  
**Impacto:** Información Visual

---

### **4.3 Animaciones de Scroll & Load**

**Objetivo:** Agregar animaciones suaves para mejorar feedback visual.

**Implementación:**

```css
/* Fade-in on load */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.kpi-card {
  animation: fadeIn 0.6s ease-out;
}

/* Stagger animation para múltiples elementos */
.kpi-card:nth-child(1) { animation-delay: 0.1s; }
.kpi-card:nth-child(2) { animation-delay: 0.2s; }
.kpi-card:nth-child(3) { animation-delay: 0.3s; }
.kpi-card:nth-child(4) { animation-delay: 0.4s; }
```

**Tiempo estimado:** 30-45 minutos  
**Impacto:** Polish

---

### **4.4 Responsive Refinado**

**Objetivo:** Optimizar layout para tablet y mobile edge cases.

**Breakpoints:**

```css
/* Desktop (1200+) */
.kpi-grid { grid-template-columns: repeat(4, 1fr); }

/* Tablet (768-1199) */
@media (max-width: 1199px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .main-container { grid-template-columns: 1fr; }
}

/* Mobile (< 768) */
@media (max-width: 767px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .sidebar { position: fixed; left: -280px; }
  /* Toggle sidebar con botón hamburguesa */
}
```

**Tiempo estimado:** 45-60 minutos  
**Impacto:** Usabilidad Mobile

---

### **4.5 Testing & QA**

**Checklist:**

- [ ] Todos los gráficos renderizan correctamente
- [ ] Tooltips funcionan en todos los charts
- [ ] Acordeones abren/cierran smoothly
- [ ] Parámetros se actualizan en tiempo real
- [ ] Exportación PDF/JSON/CSV funciona
- [ ] Responsive en mobile/tablet/desktop
- [ ] Tema oscuro funciona en todos los componentes
- [ ] Sin errores en consola
- [ ] Performance: Carga < 2s, Interacción < 100ms
- [ ] Accesibilidad: WCAG AA o mejor

**Tiempo estimado:** 60-90 minutos

---

## 📈 TIMELINE ESTIMADO

| Fase | Tarea | Horas | Acumulado |
|------|-------|-------|-----------|
| **3.1** | Waterfall Chart | 1.5 | 1.5h |
| **3.2** | Área Chart Mejorado | 0.75 | 2.25h |
| **3.3** | Heatmap Sensibilidad | 2.5 | 4.75h |
| **3.4** | Tooltips | 1 | 5.75h |
| **4.1** | Tema Oscuro/Claro | 1 | 6.75h |
| **4.2** | Sparklines Reales | 1.5 | 8.25h |
| **4.3** | Animaciones | 0.75 | 9h |
| **4.4** | Responsive Refinado | 1 | 10h |
| **4.5** | Testing | 1.5 | 11.5h |

**Total estimado:** 11-12 horas (completable en 2-3 sesiones de 4 horas)

---

## 🎯 PRIORIDADES

### **Must Have (MVP):**
1. ✅ Sistema de colores (Fase 1)
2. ✅ Tipografía mejorada (Fase 1)
3. ✅ Acordeones sidebar (Fase 2)
4. ✅ KPI cards rediseñadas (Fase 2)
5. Waterfall chart (Fase 3.1)

### **Should Have:**
6. Heatmap sensibilidad (Fase 3.3)
7. Tema oscuro (Fase 4.1)
8. Sparklines reales (Fase 4.2)

### **Nice to Have:**
9. Tooltips enriquecidos (Fase 3.4)
10. Animaciones (Fase 4.3)

---

## 🔧 SETUP TÉCNICO

### **Requisitos:**
- Python 3.8+
- Flask 2.0+
- Chart.js 4.0+
- Modern browser (Chrome 90+, Firefox 88+, Safari 14+)

### **Stack:**
- Backend: Flask (Python)
- Frontend: Vanilla JS + Chart.js
- Styling: CSS3 (No frameworks)
- Exportación: ReportLab (PDF)

### **Sin dependencias nuevas** ✅

Todas las mejoras se implementan con herramientas existentes.

---

## 🚀 PRÓXIMO PASO

**Inicio Fase 3.1:** Implementar Waterfall Chart

```bash
# Comenzar con
1. Backupear index.html actual
2. Modificar renderizarGraficos()
3. Cambiar chart tipo de 'bar' a 'bar' (waterfall via plugin/manual)
4. Probar en navegador
5. Validar en mobile/tablet
```

---

## 📝 NOTAS IMPORTANTES

- Mantener compatibilidad con datos Excel existentes
- No romper funcionalidad de exportación
- Probar cambios en navegadores principales
- Documentar cualquier cambio en versión
- Hacer commits pequeños y frecuentes

---

**Estado:** Listo para Fase 3 ✅

Documento generado: 2026-08-11
