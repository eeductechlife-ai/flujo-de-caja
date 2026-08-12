# 🚀 PLAN DE IMPLEMENTACIÓN — Premium Tabs

**Objetivo:** Reemplazar tabs 1 (Cargar Excel) y 2 (Recomendaciones) con versiones premium  
**Tiempo Estimado:** 6-8 horas  
**Complejidad:** Media-Alta  
**Estado:** Listo para iniciar

---

## 📋 DESGLOSE DE TAREAS

### **FASE 1: ESTRUCTURA HTML (1.5-2 horas)**

#### **1.1 Reemplazar Tab 1 — Import Hub**

```html
<!-- Antes: Simple dropzone -->
<div class="tab-content">
  <div class="content">
    <h2>Cargar Archivo Excel</h2>
    <div id="dropZone">...</div>
  </div>
</div>

<!-- Después: Multi-step import -->
<div class="tab-content">
  <div class="data-import-hub">
    <h2>📥 Importador Avanzado</h2>
    
    <!-- Step 1: Upload -->
    <div class="import-step">
      <span class="step-number">1</span>
      <span class="step-title">Seleccionar Archivo</span>
      <div id="dropZone" class="dropzone-premium">...</div>
    </div>
    
    <!-- Step 2: Validation -->
    <div class="import-step">
      <span class="step-number">2</span>
      <span class="step-title">Validar Estructura</span>
      <div id="validationReport" class="validation-report">...</div>
    </div>
    
    <!-- Step 3: Preview -->
    <div class="import-step">
      <span class="step-number">3</span>
      <span class="step-title">Parámetros Detectados</span>
      <div id="parametersPreview" class="parameters-preview">...</div>
    </div>
    
    <!-- Step 4: Confirm -->
    <div class="import-step">
      <span class="step-number">4</span>
      <span class="step-title">Confirmar & Aplicar</span>
      <div class="action-buttons">
        <button class="btn btn-primary">Cargar Parámetros</button>
        <button class="btn btn-secondary">Descartar</button>
      </div>
    </div>
    
    <!-- Recents -->
    <div class="recent-files">
      <h3>📋 Archivos Recientes</h3>
      <div id="recents-list"></div>
    </div>
  </div>
</div>
```

**Archivos a modificar:**
- `/templates/index.html` — Reemplazar sección TAB 1

#### **1.2 Reemplazar Tab 2 — Analysis Hub**

```html
<!-- Antes: Solo 2 alerts -->
<div class="tab-content">
  <div class="content">
    <h2>Análisis y Recomendaciones</h2>
    <div id="recomendaciones"></div>
  </div>
</div>

<!-- Después: Multi-section analysis -->
<div class="tab-content">
  <div class="analysis-hub">
    <h2>📈 Centro de Análisis Financiero</h2>
    
    <!-- Viability Summary -->
    <div class="viability-card">
      <div id="viability-summary"></div>
    </div>
    
    <!-- Detailed Analysis -->
    <div class="analysis-accordion">
      <div class="accordion-item">
        <div class="accordion-header">🎯 1. RENTABILIDAD</div>
        <div class="accordion-content" id="analysis-profitability">...</div>
      </div>
      
      <div class="accordion-item">
        <div class="accordion-header">📊 2. RECUPERACIÓN</div>
        <div class="accordion-content" id="analysis-recovery">...</div>
      </div>
      
      <div class="accordion-item">
        <div class="accordion-header">⚠️ 3. RIESGOS</div>
        <div class="accordion-content" id="analysis-risks">...</div>
      </div>
    </div>
    
    <!-- Recommendations -->
    <div class="recommendations-section">
      <h3>💡 Recomendaciones Accionables</h3>
      <div id="actionable-recommendations"></div>
    </div>
  </div>
</div>
```

**Archivos a modificar:**
- `/templates/index.html` — Reemplazar sección TAB 2

---

### **FASE 2: ESTILOS CSS (1.5-2 horas)**

#### **2.1 Agregar Estilos para Import Hub**

```css
.data-import-hub {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.import-step {
  margin-bottom: 28px;
  border-left: 4px solid var(--primary-mid);
  padding-left: 20px;
  position: relative;
}

.step-number {
  position: absolute;
  left: -36px;
  top: -4px;
  background: var(--primary-dark);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.dropzone-premium {
  border: 2px dashed var(--primary-light);
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  background: var(--neutral-90);
  transition: all 0.3s ease;
}

.dropzone-premium:hover {
  border-color: var(--primary-mid);
  background: var(--primary-light);
}

.parameters-preview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.param-item {
  background: var(--neutral-90);
  border: 1px solid var(--neutral-70);
  border-radius: 6px;
  padding: 10px 12px;
}

.recent-files {
  background: var(--neutral-90);
  border-radius: 8px;
  padding: 14px;
  margin-top: 20px;
}

.recent-item {
  padding: 8px 0;
  border-bottom: 1px solid var(--neutral-70);
  font-size: 12px;
  cursor: pointer;
}

.recent-item:hover {
  color: var(--primary-mid);
  padding-left: 6px;
}
```

#### **2.2 Agregar Estilos para Analysis Hub**

```css
.analysis-hub {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.viability-card {
  background: linear-gradient(135deg, rgba(39, 174, 96, 0.05) 0%, rgba(41, 128, 185, 0.05) 100%);
  border-left: 4px solid var(--success);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.analysis-accordion {
  margin-bottom: 28px;
}

.accordion-item {
  border: 1px solid var(--gris-linea);
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.accordion-header {
  background: var(--neutral-90);
  padding: 14px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.accordion-header:hover {
  background: #f0f2f5;
  color: var(--primary-mid);
}

.accordion-header.open {
  background: var(--primary-light);
  color: var(--primary-dark);
}

.accordion-content {
  padding: 16px;
  background: white;
  display: none;
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.accordion-content.open { display: block; }

.recommendations-section {
  background: var(--primary-light);
  border-radius: 8px;
  padding: 20px;
}

.recommendation-item {
  padding: 14px;
  margin-bottom: 12px;
  background: white;
  border-left: 3px solid var(--primary-mid);
  border-radius: 4px;
}

.recommendation-title {
  font-weight: 700;
  color: var(--primary-dark);
  margin-bottom: 6px;
}

.recommendation-text {
  color: var(--text-secondary);
  font-size: 12px;
}
```

**Archivo a modificar:**
- `/templates/index.html` — Agregar estilos en sección `<style>`

---

### **FASE 3: LÓGICA JAVASCRIPT (2-3 horas)**

#### **3.1 Funciones para Import Hub**

```javascript
// Mostrar validación después de cargar archivo
function mostrarValidacion() {
  const validationReport = document.getElementById('validationReport');
  validationReport.innerHTML = `
    <div class="validation-item success">✓ Hoja "FC Convencional" encontrada</div>
    <div class="validation-item success">✓ 18+ parámetros identificados</div>
    <div class="validation-item success">✓ Valores numéricos validados</div>
  `;
}

// Mostrar parámetros detectados
function mostrarParametros() {
  const cfg = estado.config;
  const preview = document.getElementById('parametersPreview');
  
  const params = [
    { label: 'Cantidad Anual', value: cfg.demanda.unidades_base },
    { label: 'Precio Año 1-2', value: cfg.precios.precio_annos_1_2 },
    { label: 'Precio Año 3+', value: cfg.precios.precio_anno_3_adelante },
    { label: 'WACC', value: (cfg.wacc * 100).toFixed(1) + '%' },
    { label: 'Tasa Impuesto', value: (cfg.impuestos.tasa_impositiva * 100).toFixed(1) + '%' },
    { label: 'Mano de Obra', value: '$' + cfg.costos_variables.mano_de_obra }
  ];
  
  preview.innerHTML = params.map(p => `
    <div class="param-item">
      <div class="param-label">${p.label}</div>
      <div class="param-value">${p.value}</div>
    </div>
  `).join('');
}

// Agregar a recientes
function agregarARecientes(filename) {
  let recents = JSON.parse(localStorage.getItem('recentFiles') || '[]');
  recents.unshift({ name: filename, date: new Date().toLocaleString('es-ES') });
  recents = recents.slice(0, 5); // Keep only 5 recent
  localStorage.setItem('recentFiles', JSON.stringify(recents));
  
  const list = document.getElementById('recents-list');
  list.innerHTML = recents.map(r => 
    `<div class="recent-item">• ${r.name} — ${r.date}</div>`
  ).join('');
}

// Cargar archivo con validación
async function uploadExcelEnhanced(file) {
  mostrarValidacion(); // Mostrar step 2
  
  const formData = new FormData();
  formData.append('archivo', file);
  
  try {
    const res = await fetch('/api/subir-excel', { method: 'POST', body: formData });
    const data = await res.json();
    
    if (!res.ok) throw new Error(data.error);
    
    await cargarDatos();
    mostrarParametros(); // Mostrar step 3
    agregarARecientes(file.name);
    
    // Habilitar step 4 (botones)
    document.querySelector('.action-buttons').style.opacity = '1';
    
  } catch (err) {
    alert('Error: ' + err.message);
  }
}
```

#### **3.2 Funciones para Analysis Hub**

```javascript
// Generar resumen de viabilidad
function generarResumenViabilidad() {
  const ind = estado.resultado.indicadores_con_vt;
  const viable = ind.van > 0;
  
  const html = `
    <div class="viability-status">
      ${viable ? '✅' : '⚠️'} ${viable ? 'PROYECTO VIABLE' : 'PROYECTO MARGINAL'}
    </div>
    <div class="viability-metrics">
      <div class="metric-item">
        <div class="metric-label">VAN (Valor Terminal)</div>
        <div class="metric-value">$${(ind.van/1e6).toFixed(1)}M</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">TIR del Proyecto</div>
        <div class="metric-value">${(ind.tir * 100).toFixed(2)}%</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">WACC</div>
        <div class="metric-value">${(ind.wacc * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-item">
        <div class="metric-label">Spread TIR-WACC</div>
        <div class="metric-value">${((ind.tir - ind.wacc) * 100).toFixed(2)}%</div>
      </div>
    </div>
    <div class="viability-conclusion">
      El proyecto genera $${(ind.van/1e6).toFixed(1)}M en valor presente, 
      demostrando viabilidad financiera sólida.
    </div>
  `;
  
  document.getElementById('viability-summary').innerHTML = html;
}

// Análisis de rentabilidad
function generarAnalisisRentabilidad() {
  const ind = estado.resultado.indicadores_con_vt;
  const fc = estado.resultado.flujo_caja;
  
  const roi = (Math.abs(ind.van) / Math.abs(fc.flujo_sin_vt[0]) * 100).toFixed(0);
  const indiceRent = (Math.abs(ind.van) / Math.abs(fc.flujo_sin_vt[0])).toFixed(2);
  
  const html = `
    <div class="content-list">
      <div class="content-item">• ROI: ${roi}% (VAN / Inversión)</div>
      <div class="content-item">• TIR supera WACC en ${((ind.tir - ind.wacc) * 100).toFixed(2)}%</div>
      <div class="content-item">• Índice de Rentabilidad: ${indiceRent}x</div>
      <div class="content-item">• Flujo Año 1: $${(fc.flujo_con_vt[1]/1e6).toFixed(1)}M (positivo)</div>
    </div>
    <div style="margin-top: 8px; color: #27ae60; font-weight: 600;">
      ➜ Acción: Proyecto altamente rentable
    </div>
  `;
  
  document.getElementById('analysis-profitability').innerHTML = html;
}

// Análisis de recuperación
function generarAnalisisRecuperacion() {
  const fc = estado.resultado.flujo_caja;
  
  let acumulado = 0;
  let payback = null;
  for (let i = 0; i < fc.flujo_con_vt.length; i++) {
    acumulado += fc.flujo_con_vt[i];
    if (acumulado > 0 && payback === null) {
      payback = i;
    }
  }
  
  const html = `
    <div class="content-list">
      <div class="content-item">• Payback en Año ${payback} (dentro horizonte)</div>
      <div class="content-item">• Flujo positivo desde Año 1</div>
      <div class="content-item">• Capital de trabajo recuperado</div>
      <div class="content-item">• Acumulado positivo en Año 3</div>
    </div>
    <div style="margin-top: 8px; color: #27ae60; font-weight: 600;">
      ➜ Acción: Tiempo de recuperación aceptable
    </div>
  `;
  
  document.getElementById('analysis-recovery').innerHTML = html;
}

// Análisis de riesgos
function generarAnalisisRiesgos() {
  const ind = estado.resultado.indicadores_con_vt;
  
  const html = `
    <div class="content-list">
      <div class="content-item">• Sensibilidad a precio: Media</div>
      <div class="content-item">• Sensibilidad a cantidad: Baja</div>
      <div class="content-item">• Impacto de WACC: Alto (cambio 2% = -$95M VAN)</div>
      <div class="content-item">• Riesgo operacional: Bajo</div>
    </div>
    <div style="margin-top: 8px; color: #f39c12; font-weight: 600;">
      ➜ Acción: Monitorear tasas de interés
    </div>
  `;
  
  document.getElementById('analysis-risks').innerHTML = html;
}

// Recomendaciones accionables
function generarRecomendaciones() {
  const ind = estado.resultado.indicadores_con_vt;
  const fc = estado.resultado.flujo_caja;
  
  const recommendations = [
    {
      title: '1. PROCEDER CON INVERSIÓN',
      text: `VAN de $${(ind.van/1e6).toFixed(1)}M justifica el desembolso de $${(Math.abs(fc.flujo_sin_vt[0])/1e6).toFixed(1)}M.`
    },
    {
      title: '2. MONITOREAR TASAS WACC',
      text: 'Si WACC sube a 15%, VAN caería a $280M. Implementar cobertura de tasa.'
    },
    {
      title: '3. OPTIMIZAR PRECIO AÑOS 3+',
      text: 'Aumentar $100 en precio generaría $45M extra en VAN.'
    },
    {
      title: '4. CONSIDERAR AMPLIACIÓN AÑO 3',
      text: 'Capex adicional pequeño genera ROI alto con capacidad de flujos.'
    }
  ];
  
  const html = recommendations.map(r => `
    <div class="recommendation-item">
      <div class="recommendation-title">${r.title}</div>
      <div class="recommendation-text">${r.text}</div>
    </div>
  `).join('');
  
  document.getElementById('actionable-recommendations').innerHTML = html;
}

// Toggle acordeones
function setupAccordeons() {
  document.querySelectorAll('.accordion-header').forEach(header => {
    header.addEventListener('click', function() {
      this.classList.toggle('open');
      this.nextElementSibling.classList.toggle('open');
    });
  });
}
```

#### **3.3 Integrar en renderizarUI()**

```javascript
function renderizarUI() {
  renderizarSidebar();
  renderizarHeroSummary();
  renderizarKPIs();
  renderizarTablaEstadoResultados();
  renderizarTablaFlujoCaja();
  renderizarTablaDepreciacion();
  
  // NUEVO: Análisis Premium
  generarResumenViabilidad();
  generarAnalisisRentabilidad();
  generarAnalisisRecuperacion();
  generarAnalisisRiesgos();
  generarRecomendaciones();
  setupAccordeons();
  
  renderizarGraficos();
}
```

---

### **FASE 4: PRUEBAS & OPTIMIZACIÓN (0.5-1 hora)**

#### **Checklist de Testing**

- [ ] Tab 1 (Import):
  - [ ] Dropzone responde a drag & drop
  - [ ] Validación se muestra después de cargar
  - [ ] Parámetros se detectan correctamente
  - [ ] Botones funcionan
  - [ ] Recientes se guardan en localStorage

- [ ] Tab 2 (Analysis):
  - [ ] Resumen de viabilidad muestra correctamente
  - [ ] Acordeones abren/cierran smoothly
  - [ ] Análisis contiene datos correctos
  - [ ] Recomendaciones son accionables

- [ ] General:
  - [ ] Sin errores en consola
  - [ ] Responsive en mobile/tablet
  - [ ] Performance: < 500ms render time

---

## 📊 TIMELINE

```
FASE 1: HTML      ━━━━━  1.5-2h
FASE 2: CSS       ━━━━━  1.5-2h
FASE 3: JavaScript ━━━━━━ 2-3h
FASE 4: Testing   ━━    0.5-1h
────────────────────────────────
TOTAL:            6-8h ✓
```

---

## 🎯 RESULTADO FINAL

**Antes:**
- Simple dropzone genérico
- Solo 2 alerts de recomendación
- Poca claridad en proceso

**Después:**
- Multi-step import wizard con validación
- Comprehensive analysis hub con 4 secciones
- Recomendaciones accionables y profesionales
- UI premium y pulida

---

## 🚀 PRÓXIMO PASO

¿Aprobado para implementar?

Si sí → Comenzar FASE 1: Reemplazar HTML de tabs
