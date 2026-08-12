"""
pdf_generator.py — Generador de Reporte PDF Corporativo
Limited Group S.A. · Flujo de Caja
Usa WeasyPrint (HTML + CSS Paged Media) para PDF vectorial nativo.
"""

import os
import re
import datetime
from typing import Dict, List


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de formato
# ─────────────────────────────────────────────────────────────────────────────

def fmt_m(valor: float, decimales: int = 0) -> str:
    """Formatea número como moneda colombiana."""
    if valor is None:
        return "—"
    negativo = valor < 0
    abs_val  = abs(valor)
    if decimales == 0:
        s = f"${abs_val:,.0f}"
    else:
        s = f"${abs_val:,.{decimales}f}"
    return f"({s})" if negativo else s


def fmt_pct(valor: float) -> str:
    if valor is None or (isinstance(valor, float) and (valor != valor)):
        return "N/D"
    return f"{valor:.2%}"


def badge_color(van: float) -> str:
    return "#27ae60" if van > 0 else "#e74c3c"


def anos_header(h: int) -> str:
    return "".join(f"<th>Año {i}</th>" for i in range(h + 1))


def fila_tabla(label: str, valores: List[float], negativo_parentesis: bool = True,
               bold: bool = False, clase: str = "") -> str:
    cls = f' class="{clase}"' if clase else ""
    bold_o = "<strong>" if bold else ""
    bold_c = "</strong>" if bold else ""
    cells = "".join(
        f"<td>{fmt_m(v)}</td>" for v in valores
    )
    return f"<tr{cls}><td>{bold_o}{label}{bold_c}</td>{cells}</tr>"


# ─────────────────────────────────────────────────────────────────────────────
# Secciones HTML
# ─────────────────────────────────────────────────────────────────────────────

def seccion_portada(cfg: dict) -> str:
    hoy = datetime.date.today().strftime("%d de %B de %Y")
    return f"""
    <div class="portada">
      <div class="portada-logo">LG</div>
      <h1 class="portada-title">{cfg['empresa']['nombre']}</h1>
      <h2 class="portada-sub">Evaluación Financiera del Proyecto</h2>
      <p class="portada-producto">Producto: {cfg['empresa']['producto']} · Sector: {cfg['empresa']['sector']}</p>
      <div class="portada-meta">
        <span>Horizonte de Evaluación: {cfg['horizonte_evaluacion']} años</span>
        <span>WACC: {cfg['wacc']:.0%}</span>
        <span>Tasa de Impuesto: {cfg['impuestos']['tasa_impositiva']:.0%}</span>
      </div>
      <p class="portada-fecha">{hoy}</p>
    </div>
    """


def seccion_supuestos(cfg: dict) -> str:
    inv = cfg["inversion_inicial"]
    amp = cfg["ampliacion"]
    rep = cfg["reemplazo_maquinaria"]
    cv  = cfg["costos_variables"]
    cf  = cfg["costos_fijos"]

    return f"""
    <div class="seccion page-break">
      <h2>1. Supuestos y Parámetros del Negocio</h2>

      <div class="grid-2">
        <div class="card">
          <h3>Operación</h3>
          <table class="kv">
            <tr><td>Unidades base (años 1-3)</td><td><strong>{cfg['demanda']['unidades_base']:,}</strong></td></tr>
            <tr><td>Incremento año 4</td><td><strong>{cfg['demanda']['incremento_anno_4']:.0%}</strong></td></tr>
            <tr><td>Unidades años 4-6</td><td><strong>{int(cfg['demanda']['unidades_base']*(1+cfg['demanda']['incremento_anno_4'])):,}</strong></td></tr>
            <tr><td>Precio años 1-2</td><td><strong>{fmt_m(cfg['precios']['precio_annos_1_2'])}</strong></td></tr>
            <tr><td>Precio año 3 en adelante</td><td><strong>{fmt_m(cfg['precios']['precio_anno_3_adelante'])}</strong></td></tr>
          </table>
        </div>

        <div class="card">
          <h3>Costos Variables por Unidad</h3>
          <table class="kv">
            <tr><td>Mano de obra</td><td><strong>{fmt_m(cv['mano_de_obra'])}</strong></td></tr>
            <tr><td>Materiales (años 1-3)</td><td><strong>{fmt_m(cv['materiales_base'])}</strong></td></tr>
            <tr><td>Materiales importados (años 4-6)</td><td><strong>{fmt_m(cv['materiales_importados'])}</strong></td></tr>
            <tr><td>Costos indirectos</td><td><strong>{fmt_m(cv['costos_indirectos'])}</strong></td></tr>
            <tr><td>CVU años 1-3</td><td><strong>{fmt_m(cv['mano_de_obra']+cv['materiales_base']+cv['costos_indirectos'])}</strong></td></tr>
            <tr><td>CVU años 4-6</td><td><strong>{fmt_m(cv['mano_de_obra']+cv['materiales_importados']+cv['costos_indirectos'])}</strong></td></tr>
          </table>
        </div>

        <div class="card">
          <h3>Inversión Inicial</h3>
          <table class="kv">
            <tr><td>Terreno</td><td>{fmt_m(inv['terreno'])}</td></tr>
            <tr><td>Obras físicas</td><td>{fmt_m(inv['obras_fisicas'])}</td></tr>
            <tr><td>Maquinaria total</td><td>{fmt_m(inv['maquinaria_total'])}</td></tr>
            <tr><td>Intangibles</td><td>{fmt_m(inv['intangibles_total'])}</td></tr>
            <tr><td>(-) Costo de estudio</td><td>({fmt_m(inv['costo_estudio_viabilidad'])})</td></tr>
            <tr class="total-row"><td><strong>Inversión Neta Total</strong></td><td><strong>{fmt_m(inv['total_inversion_neta'])}</strong></td></tr>
          </table>
        </div>

        <div class="card">
          <h3>Costos Fijos y Otros</h3>
          <table class="kv">
            <tr><td>Costo fijo fabricación (años 1-3)</td><td>{fmt_m(cf['costo_fijo_fabricacion_base'])}</td></tr>
            <tr><td>Costo fijo fabricación (años 4-6)</td><td>{fmt_m(cf['costo_fijo_fabricacion_base']+cf['incremento_ampliacion'])}</td></tr>
            <tr><td>Gastos admon y ventas (años 1-3)</td><td>{fmt_m(cf['gastos_admon_ventas_base'])}</td></tr>
            <tr><td>Gastos admon y ventas (años 4-6)</td><td>{fmt_m(cf['gastos_admon_ventas_ampliados'])}</td></tr>
            <tr><td>Comisión por ventas</td><td>{cf['comision_ventas_pct']:.0%}</td></tr>
            <tr><td>Tasa de impuesto</td><td>{cfg['impuestos']['tasa_impositiva']:.0%}</td></tr>
            <tr><td>WACC</td><td>{cfg['wacc']:.0%}</td></tr>
          </table>
        </div>

        <div class="card">
          <h3>Ampliación (Año {amp['anno']})</h3>
          <table class="kv">
            <tr><td>Obras físicas adicionales</td><td>{fmt_m(amp['obras_fisicas_adicionales'])}</td></tr>
            <tr><td>Maquinaria adicional</td><td>{fmt_m(amp['maquinaria_adicional'])}</td></tr>
            <tr class="total-row"><td><strong>Total Ampliación</strong></td><td><strong>{fmt_m(amp['total'])}</strong></td></tr>
          </table>
        </div>

        <div class="card">
          <h3>Reemplazo Maquinaria 1 (Año {rep['anno_venta']}/{rep['anno_compra']})</h3>
          <table class="kv">
            <tr><td>Costo nueva maquinaria</td><td>{fmt_m(rep['costo_reemplazo'])}</td></tr>
            <tr><td>Valor de salvamento (vieja)</td><td>{fmt_m(rep['valor_salvamento_maquina_vieja'])}</td></tr>
            <tr><td>Vida contable</td><td>{rep['vida_util_contable_annos']} años</td></tr>
            <tr><td>Años utilizados</td><td>{rep['annos_usados']} años</td></tr>
          </table>
        </div>
      </div>
    </div>
    """


def seccion_depreciacion(dep_tabla: dict, h: int) -> str:
    filas_html = ""
    componentes = [k for k in dep_tabla if k != "Total Depreciación"]
    for comp in componentes:
        valores = dep_tabla[comp][1:]  # Solo años 1-6
        filas_html += f"""
        <tr>
          <td>{comp}</td>
          {"".join(f"<td>{fmt_m(v) if v else '—'}</td>" for v in valores)}
        </tr>"""

    total_vals = dep_tabla["Total Depreciación"][1:]
    filas_html += f"""
        <tr class="total-row">
          <td><strong>Total Depreciación</strong></td>
          {"".join(f"<td><strong>{fmt_m(v)}</strong></td>" for v in total_vals)}
        </tr>"""

    headers = "".join(f"<th>Año {i}</th>" for i in range(1, h + 1))

    return f"""
    <div class="seccion page-break">
      <h2>2. Tabla de Depreciación y Amortización</h2>
      <p class="nota">Obras físicas: vida útil 20 años · Maquinaria: vida útil 10 años · Intangibles: amortización lineal 5 años</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Activo</th>{headers}</tr></thead>
          <tbody>{filas_html}</tbody>
        </table>
      </div>
    </div>
    """


def seccion_estado_resultados(er: dict, h: int, venta: dict) -> str:
    labels = ["Año 0"] + [f"Año {i}" for i in range(1, h + 1)]
    h_cells = "".join(f"<th>{l}</th>" for l in labels)

    a_venta = venta["anno"]
    flujo_neto = [0.0] * (h + 1)
    flujo_neto[a_venta] = venta["flujo_neto_venta"]

    return f"""
    <div class="seccion page-break">
      <h2>3. Estado de Resultados Proyectado</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Concepto</th>{h_cells}</tr></thead>
          <tbody>
            {fila_tabla("Ingresos Operativos", er['ingresos'], bold=True, clase="ingreso")}
            {fila_tabla("(-) Costos y Gastos Operativos", er['egresos_op'])}
            {fila_tabla("(-) Depreciación", er['depreciacion'])}
            {fila_tabla("(-) Amortización Intangibles", er['amortizacion'])}
            {fila_tabla("EBIT (Utilidad antes de Impuestos)", er['ebit'], bold=True, clase="subtotal")}
            {fila_tabla("(-) Impuesto de Renta (16%)", er['impuesto'])}
            {fila_tabla("UTILIDAD NETA", er['utilidad_neta'], bold=True, clase="total-row")}
          </tbody>
        </table>
      </div>
      <div class="nota-box">
        <strong>Nota — Disposición Maquinaria 1 (Año {a_venta}):</strong>
        Valor en libros: {fmt_m(venta['valor_libro'])} · Precio de venta: {fmt_m(venta['precio_venta'])} ·
        Ganancia / (Pérdida): {fmt_m(venta['ganancia_perd'])} ·
        Flujo neto después de impuesto: <strong>{fmt_m(venta['flujo_neto_venta'])}</strong>
      </div>
    </div>
    """


def seccion_capital_trabajo(kw_req: List[float], flujo_kw: List[float], h: int) -> str:
    labels = ["Año 0"] + [f"Año {i}" for i in range(1, h + 1)]
    h_cells = "".join(f"<th>{l}</th>" for l in labels)

    return f"""
    <div class="seccion">
      <h2>4. Capital de Trabajo</h2>
      <p class="nota">Capital de trabajo = 50% de los egresos operativos anuales (cobertura 6 meses)</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Concepto</th>{h_cells}</tr></thead>
          <tbody>
            {fila_tabla("KW Requerido (nivel)", kw_req)}
            {fila_tabla("Flujo de Inversión en KW", flujo_kw, bold=True, clase="total-row")}
          </tbody>
        </table>
      </div>
    </div>
    """


def seccion_flujo_caja(fc: dict, h: int) -> str:
    labels = ["Año 0"] + [f"Año {i}" for i in range(1, h + 1)]
    h_cells = "".join(f"<th>{l}</th>" for l in labels)

    # Venta de activo: solo año 4 tiene valor
    venta_fila = [0.0] * (h + 1)
    a_venta = fc["venta_activo"]["anno"]
    venta_fila[a_venta] = fc["venta_activo"]["flujo_neto_venta"]

    # VT solo en año h
    vt_fila = [0.0] * (h + 1)
    vt_fila[h] = fc["valor_terminal"]

    return f"""
    <div class="seccion page-break">
      <h2>5. Flujo de Caja Libre del Proyecto</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Concepto</th>{h_cells}</tr></thead>
          <tbody>
            {fila_tabla("(+) Utilidad Neta", fc['utilidad_neta'], clase="ingreso")}
            {fila_tabla("(+) Depreciación", fc['depreciacion'])}
            {fila_tabla("(+) Amortización Intangibles", fc['amortizacion'])}
            {fila_tabla("(+/-) Inversiones (Capex)", fc['inversiones'])}
            {fila_tabla("(+/-) Capital de Trabajo", fc['flujo_kw'])}
            {fila_tabla("(+) Venta Activo (neta impuesto)", venta_fila)}
            {fila_tabla("FLUJO DE CAJA LIBRE (sin VT)", fc['flujo_sin_vt'], bold=True, clase="subtotal")}
            {fila_tabla("(+) Valor Terminal (Perpetuidad)", vt_fila, clase="ingreso")}
            {fila_tabla("FLUJO DE CAJA LIBRE (con VT)", fc['flujo_con_vt'], bold=True, clase="total-row")}
          </tbody>
        </table>
      </div>
    </div>
    """


def seccion_indicadores(ind_sin: dict, ind_con: dict, fc: dict) -> str:
    tir_sin = fmt_pct(ind_sin["tir"]) if not (ind_sin["tir"] != ind_sin["tir"]) else "N/D"
    tir_con = fmt_pct(ind_con["tir"]) if not (ind_con["tir"] != ind_con["tir"]) else "N/D"

    color_sin = badge_color(ind_sin["van"])
    color_con = badge_color(ind_con["van"])

    payback_sin = f"Año {ind_sin['payback']}" if ind_sin["payback"] else "No recuperado"
    payback_con = f"Año {ind_con['payback']}" if ind_con["payback"] else "No recuperado"

    return f"""
    <div class="seccion page-break">
      <h2>6. Indicadores de Rentabilidad</h2>

      <div class="grid-2">
        <div class="card kpi-card" style="border-top: 4px solid {color_sin};">
          <h3>Sin Valor Terminal</h3>
          <p class="nota">Horizonte finito · {len(fc['flujo_sin_vt'])-1} años</p>
          <div class="kpi-row">
            <span class="kpi-label">VAN (WACC {ind_sin['wacc']:.0%})</span>
            <span class="kpi-valor" style="color:{color_sin};">{fmt_m(ind_sin['van'])}</span>
          </div>
          <div class="kpi-row">
            <span class="kpi-label">TIR</span>
            <span class="kpi-valor">{tir_sin}</span>
          </div>
          <div class="kpi-row">
            <span class="kpi-label">Payback</span>
            <span class="kpi-valor">{payback_sin}</span>
          </div>
          <div class="decision-badge" style="background:{color_sin};">{ind_sin['decision']}</div>
        </div>

        <div class="card kpi-card" style="border-top: 4px solid {color_con};">
          <h3>Con Valor Terminal (Empresa en Marcha)</h3>
          <p class="nota">FCF Año 6 / WACC = {fmt_m(fc['valor_terminal'])}</p>
          <div class="kpi-row">
            <span class="kpi-label">VAN (WACC {ind_con['wacc']:.0%})</span>
            <span class="kpi-valor" style="color:{color_con};">{fmt_m(ind_con['van'])}</span>
          </div>
          <div class="kpi-row">
            <span class="kpi-label">TIR</span>
            <span class="kpi-valor">{tir_con}</span>
          </div>
          <div class="kpi-row">
            <span class="kpi-label">Payback</span>
            <span class="kpi-valor">{payback_con}</span>
          </div>
          <div class="decision-badge" style="background:{color_con};">{ind_con['decision']}</div>
        </div>
      </div>

      <div class="nota-box" style="margin-top:1.5rem;">
        <strong>Interpretación:</strong> Si el VAN es positivo, el proyecto crea valor por encima del costo de capital
        (WACC = {ind_con['wacc']:.0%}). La TIR representa la tasa de rendimiento intrínseca del proyecto;
        si TIR &gt; WACC, el proyecto es financieramente atractivo.
        El Valor Terminal captura el potencial de la empresa como negocio en marcha más allá del horizonte de evaluación.
      </div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# CSS Corporativo
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap');

/* ── Page setup ────────────────────────────────────────────────────── */
@page {
  size: A4 landscape;
  margin: 15mm 12mm 18mm 12mm;
  @top-center {
    content: "Limited Group S.A. · Evaluación Financiera del Proyecto";
    font-family: 'Open Sans', Arial, sans-serif;
    font-size: 8pt;
    color: #7f8c8d;
  }
  @bottom-right {
    content: "Página " counter(page) " de " counter(pages);
    font-family: 'Open Sans', Arial, sans-serif;
    font-size: 8pt;
    color: #7f8c8d;
  }
  @bottom-left {
    content: "Confidencial · " string(doc-date);
    font-family: 'Open Sans', Arial, sans-serif;
    font-size: 8pt;
    color: #7f8c8d;
  }
}
@page :first { @top-center { content: ""; } @bottom-right { content: ""; } @bottom-left { content: ""; } }

/* ── Variables de color ─────────────────────────────────────────────── */
:root {
  --azul-corp:   #1a3a5c;
  --azul-medio:  #2980b9;
  --azul-claro:  #d6eaf8;
  --gris-linea:  #dde3ea;
  --gris-bg:     #f5f7fa;
  --verde:       #27ae60;
  --rojo:        #e74c3c;
  --texto:       #2c3e50;
  --font-main:   'Montserrat', 'Open Sans', Arial, sans-serif;
}

/* ── Base ───────────────────────────────────────────────────────────── */
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-main);
  font-size: 9pt;
  color: var(--texto);
  line-height: 1.45;
  background: #fff;
}

/* ── Portada ────────────────────────────────────────────────────────── */
.portada {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 95vh;
  text-align: center;
  background: linear-gradient(160deg, var(--azul-corp) 0%, #0d2137 100%);
  color: #fff;
  border-radius: 4px;
  padding: 60px 40px;
  page-break-after: always;
}
.portada-logo {
  width: 80px; height: 80px;
  background: rgba(255,255,255,0.15);
  border: 3px solid rgba(255,255,255,0.4);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 28pt; font-weight: 700; margin-bottom: 24px;
}
.portada-title  { font-size: 28pt; font-weight: 700; margin-bottom: 8px; }
.portada-sub    { font-size: 16pt; font-weight: 400; opacity: 0.85; margin-bottom: 16px; }
.portada-producto { font-size: 10pt; opacity: 0.7; margin-bottom: 32px; }
.portada-meta {
  display: flex; gap: 32px; justify-content: center;
  background: rgba(255,255,255,0.1);
  border-radius: 8px; padding: 12px 24px;
  margin-bottom: 32px; font-size: 10pt;
}
.portada-fecha { font-size: 9pt; opacity: 0.6; }

/* ── Sección ────────────────────────────────────────────────────────── */
.seccion { margin-bottom: 1.5rem; }
.page-break { page-break-before: always; }
.seccion h2 {
  font-size: 12pt;
  font-weight: 700;
  color: var(--azul-corp);
  border-bottom: 3px solid var(--azul-corp);
  padding-bottom: 4px;
  margin-bottom: 12px;
}

/* ── Tablas ─────────────────────────────────────────────────────────── */
.table-wrap { overflow-x: auto; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 8.5pt;
}
th {
  background: var(--azul-corp);
  color: #fff;
  font-weight: 600;
  padding: 6px 8px;
  text-align: right;
  white-space: nowrap;
}
th:first-child { text-align: left; }
td {
  padding: 5px 8px;
  border-bottom: 1px solid var(--gris-linea);
  text-align: right;
  white-space: nowrap;
}
td:first-child { text-align: left; }
tr:nth-child(even) { background: var(--gris-bg); }
tr:hover { background: var(--azul-claro); }

.total-row td   { background: var(--azul-corp); color: #fff; font-weight: 700; border-bottom: none; }
.subtotal td    { background: #d4e6f1; font-weight: 700; }
.ingreso td     { color: #1a6e37; }

/* Tabla KV (clave-valor) */
table.kv { font-size: 8.5pt; }
table.kv td:last-child { text-align: right; font-weight: 600; color: var(--azul-corp); }
table.kv tr.total-row td { background: var(--azul-claro); color: var(--azul-corp); }

/* ── Grid 2 columnas ────────────────────────────────────────────────── */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

/* ── Cards ──────────────────────────────────────────────────────────── */
.card {
  background: var(--gris-bg);
  border: 1px solid var(--gris-linea);
  border-radius: 6px;
  padding: 12px 14px;
}
.card h3 {
  font-size: 9.5pt;
  font-weight: 700;
  color: var(--azul-corp);
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 2px solid var(--azul-medio);
}

/* ── KPI cards ──────────────────────────────────────────────────────── */
.kpi-card { padding: 14px 16px; }
.kpi-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid var(--gris-linea);
}
.kpi-row:last-of-type { border-bottom: none; }
.kpi-label { font-size: 9pt; color: #555; }
.kpi-valor { font-size: 11pt; font-weight: 700; }
.decision-badge {
  margin-top: 12px;
  padding: 6px 12px;
  border-radius: 20px;
  color: #fff;
  font-weight: 700;
  font-size: 8.5pt;
  text-align: center;
  letter-spacing: 0.3px;
}

/* ── Notas ──────────────────────────────────────────────────────────── */
.nota {
  font-size: 8pt;
  color: #7f8c8d;
  margin-bottom: 6px;
  font-style: italic;
}
.nota-box {
  background: #fef9e7;
  border-left: 4px solid #f39c12;
  padding: 8px 12px;
  font-size: 8.5pt;
  border-radius: 0 4px 4px 0;
  margin-top: 8px;
}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Ensamblador HTML completo
# ─────────────────────────────────────────────────────────────────────────────

def construir_html(resultado: dict) -> str:
    cfg      = resultado["config"]
    er       = resultado["estado_resultados"]
    fc       = resultado["flujo_caja"]
    dep_tab  = resultado["depreciacion_tabla"]
    ind_sin  = resultado["indicadores_sin_vt"]
    ind_con  = resultado["indicadores_con_vt"]
    h        = cfg["horizonte_evaluacion"]

    hoy = datetime.date.today().isoformat()

    body = (
        seccion_portada(cfg)
        + seccion_supuestos(cfg)
        + seccion_depreciacion(dep_tab, h)
        + seccion_estado_resultados(er, h, fc["venta_activo"])
        + seccion_capital_trabajo(fc["kw_requerido"], fc["flujo_kw"], h)
        + seccion_flujo_caja(fc, h)
        + seccion_indicadores(ind_sin, ind_con, fc)
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="author" content="Limited Group S.A.">
  <title>Flujo de Caja — {cfg['empresa']['nombre']}</title>
  <style>{CSS}</style>
</head>
<body>
  <div style="display:none;" id="doc-date">{hoy}</div>
  {body}
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Exportar PDF
# ─────────────────────────────────────────────────────────────────────────────

def exportar_pdf(resultado: dict, output_path: str = None) -> bytes:
    """Exporta PDF y retorna bytes (para Flask) o guarda archivo si output_path se proporciona."""
    html_str  = construir_html(resultado)

    if output_path is None:
        # Modo Flask: retornar bytes
        try:
            from weasyprint import HTML as WP_HTML
            return WP_HTML(string=html_str, base_url=".").write_pdf()
        except Exception:
            # Fallback con ReportLab
            import io
            return _exportar_pdf_reportlab_bytes(resultado)

    # Modo archivo: guardar a disco
    html_path = os.path.abspath(output_path.replace(".pdf", "_temp.html"))
    abs_output = os.path.abspath(output_path)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_str)

    generado = False

    # ── 1. Intentar WeasyPrint (requiere pango/glib del sistema) ───────
    try:
        from weasyprint import HTML as WP_HTML
        WP_HTML(string=html_str, base_url=".").write_pdf(abs_output)
        print(f"[PDF] Generado con WeasyPrint: {abs_output}")
        generado = True
    except Exception:
        pass

    # ── 2. Chrome headless (macOS/Linux/Windows) ────────────────────────
    if not generado:
        import subprocess, shutil
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "google-chrome", "chromium-browser", "chromium",
        ]
        chrome_bin = next((p for p in chrome_paths
                           if shutil.which(p) or os.path.exists(p)), None)
        if chrome_bin:
            file_url = f"file://{html_path.replace(' ', '%20')}"
            try:
                subprocess.run([
                    chrome_bin,
                    "--headless=new", "--disable-gpu",
                    "--no-sandbox", "--disable-dev-shm-usage",
                    "--print-to-pdf-no-header",
                    f"--print-to-pdf={abs_output}",
                    file_url,
                ], capture_output=True, timeout=60)
                if os.path.exists(abs_output) and os.path.getsize(abs_output) > 1000:
                    print(f"[PDF] Generado con Chrome headless: {abs_output}")
                    generado = True
            except Exception as e:
                print(f"[PDF] Chrome headless falló: {e}")

    # ── 3. ReportLab como último recurso ────────────────────────────────
    if not generado:
        print("[PDF] Usando ReportLab como fallback...")
        _exportar_pdf_reportlab(resultado, abs_output)

    if os.path.exists(html_path):
        os.remove(html_path)

    return abs_output


def _exportar_pdf_reportlab_bytes(resultado: dict) -> bytes:
    """ReportLab: PDF retornando bytes (para Flask)."""
    import io
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Spacer,
            Paragraph, HRFlowable, PageBreak
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        raise RuntimeError("ReportLab no está disponible.")

    buffer = io.BytesIO()
    cfg     = resultado["config"]
    er      = resultado["estado_resultados"]
    fc      = resultado["flujo_caja"]
    h       = cfg["horizonte_evaluacion"]

    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=12*mm, leftMargin=12*mm,
                            topMargin=15*mm, bottomMargin=18*mm)

    styles = getSampleStyleSheet()
    elements = [Paragraph("PDF Flujo de Caja", styles['Title']), Spacer(1, 12)]

    # Tabla simple de flujo
    filas_fc = [["Concepto"] + [f"Año {i}" for i in range(h + 1)]]
    for label, vals in [("Flujo SIN VT", fc["flujo_sin_vt"]), ("Flujo CON VT", fc["flujo_con_vt"])]:
        filas_fc.append([label] + [fmt_m(vals[i]) for i in range(h + 1)])

    t = Table(filas_fc)
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8),
                           ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
                           ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]))
    elements.append(t)

    doc.build(elements)
    return buffer.getvalue()


def _exportar_pdf_reportlab(resultado: dict, output_path: str):
    """Fallback: PDF básico con ReportLab si WeasyPrint falla."""
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm, mm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Spacer,
            Paragraph, HRFlowable, PageBreak
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        raise RuntimeError("Ni WeasyPrint ni ReportLab están disponibles.")

    cfg     = resultado["config"]
    er      = resultado["estado_resultados"]
    fc      = resultado["flujo_caja"]
    ind_sin = resultado["indicadores_sin_vt"]
    ind_con = resultado["indicadores_con_vt"]
    h       = cfg["horizonte_evaluacion"]

    AZUL   = colors.HexColor("#1a3a5c")
    AZUL2  = colors.HexColor("#2980b9")
    AZULC  = colors.HexColor("#d6eaf8")
    VERDE  = colors.HexColor("#27ae60")
    ROJO   = colors.HexColor("#e74c3c")
    GRIS   = colors.HexColor("#f5f7fa")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=12*mm, leftMargin=12*mm,
        topMargin=15*mm, bottomMargin=18*mm,
    )

    styles = getSampleStyleSheet()
    st_title  = ParagraphStyle("title",  fontSize=20, textColor=colors.white, alignment=TA_CENTER, fontName="Helvetica-Bold")
    st_sub    = ParagraphStyle("sub",    fontSize=12, textColor=colors.white, alignment=TA_CENTER)
    st_h2     = ParagraphStyle("h2",     fontSize=12, textColor=AZUL, fontName="Helvetica-Bold", spaceAfter=6)
    st_nota   = ParagraphStyle("nota",   fontSize=7,  textColor=colors.grey, fontName="Helvetica-Oblique")
    st_normal = styles["Normal"]

    def tabla_rl(datos, col_widths=None, header_row=True):
        t = Table(datos, colWidths=col_widths)
        style_list = [
            ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 0), (-1, -1), 7.5),
            ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#dde3ea")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRIS, colors.white]),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN",       (1, 0), (-1, -1), "RIGHT"),
        ]
        if header_row:
            style_list += [
                ("BACKGROUND",  (0, 0), (-1, 0), AZUL),
                ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, 0), 8),
            ]
        t.setStyle(TableStyle(style_list))
        return t

    elements = []

    # Portada
    portada = Table(
        [[Paragraph(f"<b>{cfg['empresa']['nombre']}</b>", st_title)],
         [Paragraph("Evaluación Financiera del Proyecto", st_sub)],
         [Paragraph(f"{cfg['empresa']['producto']} · {cfg['empresa']['sector']}", st_sub)],
         [Spacer(1, 20)],
         [Paragraph(f"WACC: {cfg['wacc']:.0%}  ·  Impuesto: {cfg['impuestos']['tasa_impositiva']:.0%}  ·  Horizonte: {h} años", st_sub)],
         [Paragraph(datetime.date.today().strftime("%d de %B de %Y"), st_nota)],
        ], colWidths=["100%"])
    portada.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), AZUL),
        ("TOPPADDING",   (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 20),
        ("LEFTPADDING",  (0, 0), (-1, -1), 30),
        ("RIGHTPADDING", (0, 0), (-1, -1), 30),
    ]))
    elements.extend([portada, PageBreak()])

    # Estado de Resultados
    elements.append(Paragraph("Estado de Resultados Proyectado", st_h2))
    years = ["Concepto"] + [f"Año {i}" for i in range(h + 1)]
    filas_er = [years]
    for label, key in [
        ("Ingresos Operativos",            "ingresos"),
        ("(-) Egresos Operativos",         "egresos_op"),
        ("(-) Depreciación",               "depreciacion"),
        ("(-) Amortización",               "amortizacion"),
        ("EBIT",                           "ebit"),
        ("(-) Impuesto (16%)",             "impuesto"),
        ("UTILIDAD NETA",                  "utilidad_neta"),
    ]:
        row = [label] + [fmt_m(er[key][i]) for i in range(h + 1)]
        filas_er.append(row)

    t_er = tabla_rl(filas_er)
    t_er.setStyle(TableStyle([
        ("FONTNAME",   (0, len(filas_er)-1), (-1, len(filas_er)-1), "Helvetica-Bold"),
        ("BACKGROUND", (0, len(filas_er)-1), (-1, len(filas_er)-1), AZUL),
        ("TEXTCOLOR",  (0, len(filas_er)-1), (-1, len(filas_er)-1), colors.white),
    ]))
    elements.extend([t_er, Spacer(1, 12), PageBreak()])

    # Flujo de Caja
    elements.append(Paragraph("Flujo de Caja Libre del Proyecto", st_h2))
    venta_fila = [0.0] * (h + 1)
    venta_fila[fc["venta_activo"]["anno"]] = fc["venta_activo"]["flujo_neto_venta"]
    vt_fila = [0.0] * (h + 1)
    vt_fila[h] = fc["valor_terminal"]

    filas_fc = [["Concepto"] + [f"Año {i}" for i in range(h + 1)]]
    for label, vals in [
        ("(+) Utilidad Neta",                fc["utilidad_neta"]),
        ("(+) Depreciación",                 fc["depreciacion"]),
        ("(+) Amortización",                 fc["amortizacion"]),
        ("(+/-) Inversiones",                fc["inversiones"]),
        ("(+/-) Capital de Trabajo",         fc["flujo_kw"]),
        ("(+) Venta Activo (neto impuesto)", venta_fila),
        ("FCL SIN Valor Terminal",           fc["flujo_sin_vt"]),
        ("(+) Valor Terminal",               vt_fila),
        ("FCL CON Valor Terminal",           fc["flujo_con_vt"]),
    ]:
        filas_fc.append([label] + [fmt_m(vals[i]) for i in range(h + 1)])

    t_fc = tabla_rl(filas_fc)
    for idx, bold_row in [(7, True), (9, True)]:
        t_fc.setStyle(TableStyle([
            ("FONTNAME",   (0, idx), (-1, idx), "Helvetica-Bold"),
            ("BACKGROUND", (0, idx), (-1, idx), AZUL2 if idx == 7 else AZUL),
            ("TEXTCOLOR",  (0, idx), (-1, idx), colors.white),
        ]))
    elements.extend([t_fc, Spacer(1, 12), PageBreak()])

    # Indicadores
    elements.append(Paragraph("Indicadores de Rentabilidad", st_h2))
    color_van = VERDE if ind_con["van"] > 0 else ROJO
    tir_con = fmt_pct(ind_con["tir"])
    tir_sin = fmt_pct(ind_sin["tir"])

    filas_kpi = [
        ["Indicador", "Sin Valor Terminal", "Con Valor Terminal (Empresa en Marcha)"],
        ["VAN", fmt_m(ind_sin["van"]), fmt_m(ind_con["van"])],
        ["TIR", tir_sin, tir_con],
        ["WACC", fmt_pct(ind_sin["wacc"]), fmt_pct(ind_con["wacc"])],
        ["TIR > WACC",
         "SÍ" if not (ind_sin["tir"] != ind_sin["tir"]) and ind_sin["tir"] > ind_sin["wacc"] else "NO",
         "SÍ" if not (ind_con["tir"] != ind_con["tir"]) and ind_con["tir"] > ind_con["wacc"] else "NO"],
        ["Decisión", ind_sin["decision"], ind_con["decision"]],
    ]
    t_kpi = tabla_rl(filas_kpi)
    t_kpi.setStyle(TableStyle([
        ("BACKGROUND", (0, 5), (-1, 5), color_van),
        ("TEXTCOLOR",  (0, 5), (-1, 5), colors.white),
        ("FONTNAME",   (0, 5), (-1, 5), "Helvetica-Bold"),
    ]))
    elements.append(t_kpi)

    doc.build(elements)
    print(f"[PDF] Generado con ReportLab: {output_path}")


if __name__ == "__main__":
    from model import ejecutar_modelo
    resultado = ejecutar_modelo()
    exportar_pdf(resultado, "reporte_flujo_caja.pdf")
