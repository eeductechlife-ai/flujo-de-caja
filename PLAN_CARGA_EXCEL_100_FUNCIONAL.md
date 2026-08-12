# 📋 PLAN COMPLETO — Carga de Excel 100% Funcional

**Análisis:** 2026-08-12  
**Status:** Diseño de Solución  
**Objetivo:** Que 100% de los datos del Excel se carguen Y se muestren en el dashboard

---

## 🔍 ANÁLISIS ACTUAL

### Situación
✅ **SERVIDOR:** Extrae correctamente todos los datos del Excel
- ✅ Parámetros de entrada (6 grupos)
- ✅ Flujo de caja (7 períodos)
- ✅ Indicadores (VAN, TIR, etc.)

❌ **FRONTEND:** No muestra los datos correctamente
- Problema: Los datos no aparecen en el dashboard después de cargar

### Root Cause Identificada
El código en `/api/subir-excel` (línea 308-318) intenta reemplazar valores, pero:
1. La estructura de datos puede no ser la correcta
2. El flujo de actualización no se propaga correctamente al frontend
3. El frontend sigue mostrando datos predeterminados en lugar de los cargados

---

## 📊 FLUJO DE DATOS ACTUAL

```
1. Usuario carga Excel
   ↓
2. POST /api/subir-excel
   ↓
3. Servidor extrae parámetros ✅
4. Servidor extrae flujo de caja ✅
5. Servidor reemplaza valores (AQUÍ HAY UN PROBLEMA)
   ↓
6. Frontend llama GET /api/resultado
   ↓
7. Frontend renderiza (PERO NO MUESTRA DATOS DEL EXCEL)
   ↓
8. Dashboard muestra valores pero no son los del Excel ❌
```

---

## 🎯 SOLUCIÓN PROPUESTA

### Paso 1: Mejorar el endpoint `/api/subir-excel`
**Problema:** La actualización de valores no está completa

**Solución:**
```python
# En lugar de solo reemplazar algunos valores,
# actualizar COMPLETAMENTE el estado_global['resultado']
# con los datos del Excel

if flujo_excel and flujo_excel.get('flujo_caja'):
    # 1. Calcular con parámetros nuevos
    resultado = ejecutar_modelo('config.json')
    
    # 2. Reemplazar COMPLETAMENTE los flujos
    resultado['estado_resultados']['ingresos'] = flujo_excel['ingresos']
    resultado['estado_resultados']['egresos_op'] = flujo_excel['egresos']
    resultado['flujo_caja']['flujo_con_vt'] = flujo_excel['flujo_caja']
    resultado['flujo_caja']['flujo_sin_vt'] = flujo_excel['flujo_caja']
    
    # 3. Actualizar indicadores si están en Excel
    if flujo_excel.get('indicadores'):
        # IMPORTANTE: Los indicadores del Excel podrían ser más precisos
        # Actualizar ambos estados (con y sin VT)
        for key, val in flujo_excel['indicadores'].items():
            if key in resultado['indicadores_con_vt']:
                resultado['indicadores_con_vt'][key] = val
            if key in resultado['indicadores_sin_vt']:
                resultado['indicadores_sin_vt'][key] = val
    
    estado_global['resultado'] = resultado
```

### Paso 2: Verificar respuesta en `/api/resultado`
**Verificar que retorna:**
- ✅ config actualizado
- ✅ estado_resultados actualizado
- ✅ flujo_caja actualizado
- ✅ indicadores actualizados

### Paso 3: Verificar frontend renderiza
**En JavaScript:**
```javascript
async function uploadExcel(file) {
    // ... código existente ...
    
    // Después de cargar:
    await cargarDatos();  // GET /api/resultado
    
    // IMPORTANTE: Verificar que renderiza TODOS los componentes
    renderizarUI();       // Debe actualizar TODAS las vistas
    
    // Específicamente:
    renderizarTablaEstadoResultados();  // Mostrar ingresos/egresos
    renderizarTablaFlujoCaja();          // Mostrar flujo completo
    generarResumenViabilidad();          // Mostrar indicadores
}
```

---

## 🔧 CAMBIOS NECESARIOS

### Cambio 1: Mejorar actualización de indicadores en app.py

**Archivo:** `/Users/home/Desktop/flujo de caja /app.py`
**Línea:** 321-326 (en función `subir_excel()`)

**Antes:**
```python
if flujo_excel.get('indicadores'):
    print(f"✅ Indicadores encontrados en Excel:")
    for key, val in flujo_excel['indicadores'].items():
        print(f"   - {key}: {val}")
    # Nota: Los indicadores se actualizan pero el modelo es la fuente de verdad
```

**Después:**
```python
if flujo_excel.get('indicadores'):
    print(f"✅ Indicadores encontrados en Excel:")
    for key, val in flujo_excel['indicadores'].items():
        print(f"   - {key}: {val}")
        # Actualizar indicadores en resultado
        if key in resultado['indicadores_con_vt']:
            resultado['indicadores_con_vt'][key] = val
        if key in resultado['indicadores_sin_vt']:
            resultado['indicadores_sin_vt'][key] = val
```

### Cambio 2: Logging mejorado para debugging

Agregar en `/api/subir-excel` después de actualizar:
```python
# Verificación de datos actualizados
print(f"\n✅ VERIFICACIÓN DE DATOS ACTUALIZADOS:")
print(f"   Ingresos (primero): {resultado['estado_resultados']['ingresos'][0] if resultado['estado_resultados']['ingresos'] else 'VACÍO'}")
print(f"   Egresos (primero): {resultado['estado_resultados']['egresos_op'][0] if resultado['estado_resultados']['egresos_op'] else 'VACÍO'}")
print(f"   Flujo (primero): {resultado['flujo_caja']['flujo_con_vt'][0] if resultado['flujo_caja']['flujo_con_vt'] else 'VACÍO'}")
print(f"   VAN: {resultado['indicadores_con_vt'].get('van', 'NO ENCONTRADO')}")
```

### Cambio 3: Verificar en frontend (opcional)

En `index.html`, en la función `uploadExcel()`:
```javascript
const data = await res.json();
console.log('✅ Excel cargado, respuesta:', data);  // Para debugging

// Recargar datos
await cargarDatos();
console.log('✅ Datos cargados, estado:', estado);  // Para debugging

renderizarUI();
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Backend (Servidor)
- [ ] Extraer parámetros ✅
- [ ] Extraer flujo de caja ✅
- [ ] Extraer indicadores ✅
- [ ] Reemplazar en resultado
- [ ] Actualizar estado_global
- [ ] Retornar datos en respuesta

### Frontend (Navegador)
- [ ] Recibir respuesta de /api/subir-excel
- [ ] Llamar cargarDatos() → GET /api/resultado
- [ ] Recibir datos actualizados
- [ ] Renderizar tablas
- [ ] Renderizar gráficos
- [ ] Renderizar indicadores

### Validación Visual
- [ ] Ingresos en tabla mostrados correctamente
- [ ] Egresos en tabla mostrados correctamente
- [ ] Flujo de caja mostrado correctamente
- [ ] VAN, TIR, etc. actualizados
- [ ] Gráficos reflejan los nuevos datos

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Fase 1: Correcciones en Backend (15 min)
1. ✅ Mejorar código de reemplazo de indicadores
2. ✅ Agregar logging para debugging
3. ✅ Verificar que datos se envían correctamente

### Fase 2: Verificación en Frontend (10 min)
1. ✅ Agregar logging en JavaScript
2. ✅ Verificar que se reciben datos
3. ✅ Verificar que se renderizan

### Fase 3: Testing (15 min)
1. ✅ Cargar Excel de prueba
2. ✅ Verificar valores en logs
3. ✅ Verificar valores en dashboard
4. ✅ Comparar con valores esperados

### Total: ~40 minutos

---

## 📈 RESULTADO ESPERADO

**Antes:** ❌
```
Usuario carga Excel con:
- VAN: $105.78M
- TIR: 37%
→ Dashboard muestra:
- VAN: $377.5M (valores por defecto)
- TIR: 55.89% (valores por defecto)
```

**Después:** ✅
```
Usuario carga Excel con:
- VAN: $105.78M
- TIR: 37%
→ Dashboard muestra:
- VAN: $105.78M (del Excel)
- TIR: 37% (del Excel)
- Todos los valores coinciden
```

---

## 🔒 Garantías de Calidad

- ✅ No alterar funcionalidad principal
- ✅ Mantener compatibilidad hacia atrás
- ✅ Preservar parámetros editables
- ✅ Mantener exportación intacta
- ✅ Logging para debugging futuro

---

**Status:** 🟢 LISTO PARA IMPLEMENTAR

**Complejidad:** 🟢 BAJA (Solo mejoras en backend)

**Riesgo:** 🟢 MÍNIMO (Cambios aislados)

**Impacto:** 🟢 ALTO (Funcionalidad crítica mejorada)
