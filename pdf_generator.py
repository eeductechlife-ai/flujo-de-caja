"""
pdf_generator.py — Generador de Reporte PDF Corporativo
Limited Group S.A. · Flujo de Caja
Usa WeasyPrint (HTML + CSS Paged Media) para PDF vectorial nativo.
"""

import os
import re
import datetime
from typing import Dict, List

_MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _fecha_larga_es(d: datetime.date = None) -> str:
    """Fecha en español sin depender del locale del sistema (Render puede no tenerlo)."""
    d = d or datetime.date.today()
    return f"{d.day} de {_MESES_ES[d.month - 1]} de {d.year}"


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


# ─────────────────────────────────────────────────────────────────────────────
# Reporte PDF profesional con ReportLab (motor por defecto en la nube/Render)
# Genera el documento COMPLETO multipágina — puro Python, sin dependencias de SO.
# ─────────────────────────────────────────────────────────────────────────────

# Paleta corporativa (reutilizada en portada, encabezados y badges)
_AZUL   = "#1a3a5c"
_AZUL2  = "#2980b9"
_AZULC  = "#d6eaf8"
_VERDE  = "#27ae60"
_ROJO   = "#c0392b"
_GRIS   = "#f5f7fa"
_LINEA  = "#dde3ea"
_TEXTO  = "#2c3e50"
_GRISTX = "#7f8c8d"


def _es_nan(x) -> bool:
    return isinstance(x, float) and x != x


class _NumberedCanvas:
    """Canvas que dibuja encabezado + pie con 'Página X de Y' en cada hoja
    (excepto la portada). Se construye dinámicamente para heredar del Canvas real."""
    pass


def _make_numbered_canvas():
    from reportlab.pdfgen import canvas as _canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    import datetime as _dt

    ancho, alto = landscape(A4)
    fecha = _dt.date.today().strftime("%d/%m/%Y")

    class NumberedCanvas(_canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._saved)
            for i, state in enumerate(self._saved, start=1):
                self.__dict__.update(state)
                self._decorar(i, total)
                super().showPage()
            super().save()

        def _decorar(self, page_num, total):
            # La portada (página 1) va sin encabezado/pie
            if page_num == 1:
                return
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor(_GRISTX))
            # Encabezado
            self.drawCentredString(
                ancho / 2.0, alto - 10 * mm,
                "Limited Group S.A. · Evaluación Financiera del Proyecto")
            self.setStrokeColor(colors.HexColor(_LINEA))
            self.setLineWidth(0.5)
            self.line(12 * mm, alto - 12 * mm, ancho - 12 * mm, alto - 12 * mm)
            # Pie
            self.line(12 * mm, 12 * mm, ancho - 12 * mm, 12 * mm)
            self.drawString(12 * mm, 8 * mm, f"Confidencial · {fecha}")
            self.drawRightString(ancho - 12 * mm, 8 * mm,
                                 f"Página {page_num} de {total}")
            self.restoreState()

    return NumberedCanvas


def _construir_story(resultado: dict):
    """Construye la lista de flowables del reporte profesional completo.
    Reutilizada tanto por el modo bytes (Flask/nube) como por el modo archivo."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        Table, TableStyle, Spacer, Paragraph, PageBreak, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    cfg     = resultado["config"]
    er      = resultado["estado_resultados"]
    fc      = resultado["flujo_caja"]
    dep_tab = resultado.get("depreciacion_tabla", {})
    ind_sin = resultado["indicadores_sin_vt"]
    ind_con = resultado["indicadores_con_vt"]
    h       = cfg["horizonte_evaluacion"]
    ancho, _ = landscape(A4)
    util = ancho - 24 * mm  # ancho útil entre márgenes

    AZUL  = colors.HexColor(_AZUL)
    AZUL2 = colors.HexColor(_AZUL2)
    AZULC = colors.HexColor(_AZULC)
    VERDE = colors.HexColor(_VERDE)
    ROJO  = colors.HexColor(_ROJO)
    GRIS  = colors.HexColor(_GRIS)
    LINEA = colors.HexColor(_LINEA)

    st = getSampleStyleSheet()
    st_title = ParagraphStyle("t", fontSize=26, textColor=colors.white,
                              alignment=TA_CENTER, fontName="Helvetica-Bold", leading=30)
    st_sub   = ParagraphStyle("s", fontSize=13, textColor=colors.white,
                              alignment=TA_CENTER, leading=18)
    st_sub2  = ParagraphStyle("s2", fontSize=10, textColor=colors.Color(1, 1, 1, 0.8),
                              alignment=TA_CENTER, leading=15)
    st_meta  = ParagraphStyle("m", fontSize=10, textColor=colors.white, alignment=TA_CENTER)
    st_h2    = ParagraphStyle("h2", fontSize=13, textColor=AZUL,
                              fontName="Helvetica-Bold", spaceAfter=8, spaceBefore=2)
    st_nota  = ParagraphStyle("n", fontSize=8, textColor=colors.HexColor(_GRISTX),
                              fontName="Helvetica-Oblique", spaceAfter=6)
    st_intro = ParagraphStyle("i", fontSize=9, textColor=colors.HexColor(_TEXTO),
                              leading=13, spaceBefore=4)

    def h2(txt):
        # Encabezado de sección con línea inferior corporativa
        p = Paragraph(txt, st_h2)
        linea = Table([[""]], colWidths=[util], rowHeights=[2])
        linea.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AZUL),
                                   ("TOPPADDING", (0, 0), (-1, -1), 0),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        return [p, linea, Spacer(1, 8)]

    def tabla(datos, negativos_idx=None, col0_ratio=0.20):
        """Tabla financiera estándar. negativos_idx: matriz de bool (misma forma
        que datos) marcando celdas negativas para pintarlas en rojo."""
        ncols = len(datos[0])
        w0 = util * col0_ratio
        wr = (util - w0) / (ncols - 1) if ncols > 1 else util
        col_widths = [w0] + [wr] * (ncols - 1)
        t = Table(datos, colWidths=col_widths, repeatRows=1)
        estilo = [
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), AZUL),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS]),
            ("GRID", (0, 0), (-1, -1), 0.3, LINEA),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        if negativos_idx:
            for ri, fila in enumerate(negativos_idx):
                for ci, neg in enumerate(fila):
                    if neg:
                        estilo.append(("TEXTCOLOR", (ci, ri), (ci, ri), ROJO))
        t.setStyle(TableStyle(estilo))
        return t

    def marca_negativos(datos, valores):
        """Genera matriz de negativos a partir de la matriz de valores crudos."""
        idx = [[False] * len(datos[0])]  # header
        for fila in valores:
            idx.append([False] + [(isinstance(v, (int, float)) and not _es_nan(v) and v < 0) for v in fila])
        return idx

    story = []

    # ── 1. PORTADA ──────────────────────────────────────────────────────
    emp = cfg.get("empresa", {})
    nombre  = emp.get("nombre", "Limited Group S.A.")
    prod    = emp.get("producto", "—")
    sector  = emp.get("sector", "—")
    fecha_larga = _fecha_larga_es()

    meta_txt = (f"Horizonte de Evaluación: {h} años &nbsp;·&nbsp; "
                f"WACC: {cfg.get('wacc', 0):.0%} &nbsp;·&nbsp; "
                f"Impuesto: {cfg.get('impuestos', {}).get('tasa_impositiva', 0):.0%}")

    portada = Table([
        [Paragraph("LG", ParagraphStyle("lg", fontSize=24, textColor=colors.white,
                                        alignment=TA_CENTER, fontName="Helvetica-Bold"))],
        [Spacer(1, 16)],
        [Paragraph(nombre, st_title)],
        [Paragraph("Evaluación Financiera del Proyecto", st_sub)],
        [Spacer(1, 8)],
        [Paragraph(f"Producto: {prod} &nbsp;·&nbsp; Sector: {sector}", st_sub2)],
        [Spacer(1, 26)],
        [Paragraph(meta_txt, st_meta)],
        [Spacer(1, 26)],
        [Paragraph(fecha_larga, st_sub2)],
    ], colWidths=[util])
    portada.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (0, 0), 70),
        ("BOTTOMPADDING", (0, -1), (0, -1), 70),
    ]))
    story += [portada, PageBreak()]

    # ── 2. RESUMEN EJECUTIVO (KPIs) ─────────────────────────────────────
    sec_resumen = h2("Resumen Ejecutivo")
    van = ind_con.get("van", 0)
    tir = ind_con.get("tir", 0)
    wacc = ind_con.get("wacc", 0)
    payback = ind_con.get("payback")
    decision = ind_con.get("decision", "—")
    color_dec = VERDE if (van or 0) > 0 else ROJO

    def kpi_cell(label, valor, color=None):
        cl = ParagraphStyle("kl", fontSize=8.5, textColor=colors.HexColor(_GRISTX),
                            alignment=TA_CENTER, spaceAfter=4)
        cv = ParagraphStyle("kv", fontSize=17, fontName="Helvetica-Bold",
                            textColor=color or AZUL, alignment=TA_CENTER, leading=20)
        return [Paragraph(label, cl), Paragraph(valor, cv)]

    tir_txt = "N/D" if _es_nan(tir) else f"{tir:.2%}"
    pb_txt = f"Año {payback}" if payback else "No recuperado"
    kpis = Table([[
        kpi_cell("VAN (con Valor Terminal)", fmt_m(van), VERDE if (van or 0) > 0 else ROJO),
        kpi_cell("TIR", tir_txt),
        kpi_cell("WACC", f"{wacc:.2%}"),
        kpi_cell("Payback", pb_txt),
    ]], colWidths=[util / 4.0] * 4)
    kpis.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRIS),
        ("BOX", (0, 0), (-1, -1), 0.5, LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    sec_resumen += [kpis, Spacer(1, 10)]

    # Badge de decisión
    badge = Table([[Paragraph(f"DECISIÓN: {decision}",
                              ParagraphStyle("bd", fontSize=11, textColor=colors.white,
                                             alignment=TA_CENTER, fontName="Helvetica-Bold"))]],
                  colWidths=[util])
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_dec),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    sec_resumen += [badge, Spacer(1, 12)]

    interp = (f"El proyecto presenta un VAN de <b>{fmt_m(van)}</b> descontado al WACC de "
              f"<b>{wacc:.1%}</b>. "
              + ("Al ser el VAN positivo, el proyecto <b>crea valor</b> por encima del costo de "
                 "capital y es financieramente atractivo. "
                 if (van or 0) > 0 else
                 "Al ser el VAN negativo, el proyecto <b>destruye valor</b> frente al costo de capital. ")
              + (f"La TIR de <b>{tir_txt}</b> "
                 + ("supera" if (not _es_nan(tir) and tir > wacc) else "no supera")
                 + " al WACC. " if not _es_nan(tir) else "")
              + (f"La inversión se recupera en el <b>{pb_txt.lower()}</b>." if payback else ""))
    sec_resumen += [Paragraph(interp, st_intro)]

    # ── 3. ESTADO DE RESULTADOS ─────────────────────────────────────────
    sec_er = h2("Estado de Resultados Proyectado")
    anos = ["Concepto"] + [f"Año {i}" for i in range(h + 1)]

    # Filas: si el Excel trae el desglose de costos, se usa; si no, egresos_op.
    if "costo_variable" in er:
        er_defs = [
            ("Ingresos Operativos", "ingresos"),
            ("(-) Costo Variable Fabricación", "costo_variable"),
            ("(-) Costo Fijo Fabricación", "costo_fijo"),
            ("(-) Gastos Admón. y Ventas", "gastos_admon"),
            ("(-) Comisiones por Venta", "comisiones"),
            ("(-) Depreciación", "depreciacion"),
            ("(-) Amortización Intangibles", "amortizacion"),
            ("EBIT (Utilidad antes de Impuestos)", "ebit"),
            ("(-) Impuesto de Renta", "impuesto"),
            ("UTILIDAD NETA", "utilidad_neta"),
        ]
    else:
        er_defs = [
            ("Ingresos Operativos", "ingresos"),
            ("(-) Costos y Gastos Operativos", "egresos_op"),
            ("(-) Depreciación", "depreciacion"),
            ("(-) Amortización Intangibles", "amortizacion"),
            ("EBIT (Utilidad antes de Impuestos)", "ebit"),
            ("(-) Impuesto de Renta", "impuesto"),
            ("UTILIDAD NETA", "utilidad_neta"),
        ]
    er_defs = [(lbl, k) for (lbl, k) in er_defs if k in er and er[k] is not None]

    filas_er, valores_er = [anos], []
    for lbl, k in er_defs:
        vals = [er[k][i] if i < len(er[k]) else 0 for i in range(h + 1)]
        valores_er.append(vals)
        filas_er.append([lbl] + [fmt_m(v) for v in vals])

    t_er = tabla(filas_er, marca_negativos(filas_er, valores_er))
    # Resaltar EBIT (subtotal) y UTILIDAD NETA (total)
    idx_ebit = next((i + 1 for i, (l, k) in enumerate(er_defs) if k == "ebit"), None)
    idx_un = len(er_defs)
    extra = []
    if idx_ebit:
        extra += [("BACKGROUND", (0, idx_ebit), (-1, idx_ebit), AZULC),
                  ("FONTNAME", (0, idx_ebit), (-1, idx_ebit), "Helvetica-Bold")]
    extra += [("BACKGROUND", (0, idx_un), (-1, idx_un), AZUL),
              ("TEXTCOLOR", (0, idx_un), (-1, idx_un), colors.white),
              ("FONTNAME", (0, idx_un), (-1, idx_un), "Helvetica-Bold")]
    t_er.setStyle(TableStyle(extra))
    sec_er += [t_er]

    # ── 4. FLUJO DE CAJA LIBRE ──────────────────────────────────────────
    sec_fc = h2("Flujo de Caja Libre del Proyecto")
    venta_fila = [0.0] * (h + 1)
    va = fc.get("venta_activo", {})
    if va.get("anno") is not None and va.get("anno") <= h:
        venta_fila[va["anno"]] = va.get("flujo_neto_venta", 0)
    vt_fila = [0.0] * (h + 1)
    vt_fila[h] = fc.get("valor_terminal", 0)

    fc_defs = [
        ("(+) Utilidad Neta", fc["utilidad_neta"]),
        ("(+) Depreciación", fc["depreciacion"]),
        ("(+) Amortización Intangibles", fc["amortizacion"]),
        ("(+/-) Inversiones (Capex)", fc["inversiones"]),
        ("(+/-) Capital de Trabajo", fc["flujo_kw"]),
        ("(+) Venta Activo (neta de impuesto)", venta_fila),
        ("FLUJO DE CAJA LIBRE (sin VT)", fc["flujo_sin_vt"]),
        ("(+) Valor Terminal (Perpetuidad)", vt_fila),
        ("FLUJO DE CAJA LIBRE (con VT)", fc["flujo_con_vt"]),
    ]
    filas_fc, valores_fc = [anos], []
    for lbl, serie in fc_defs:
        vals = [serie[i] if i < len(serie) else 0 for i in range(h + 1)]
        valores_fc.append(vals)
        filas_fc.append([lbl] + [fmt_m(v) for v in vals])

    t_fc = tabla(filas_fc, marca_negativos(filas_fc, valores_fc))
    # Fila 7 = FCL sin VT (subtotal), fila 9 = FCL con VT (total)
    t_fc.setStyle(TableStyle([
        ("BACKGROUND", (0, 7), (-1, 7), AZULC),
        ("FONTNAME", (0, 7), (-1, 7), "Helvetica-Bold"),
        ("BACKGROUND", (0, 9), (-1, 9), AZUL),
        ("TEXTCOLOR", (0, 9), (-1, 9), colors.white),
        ("FONTNAME", (0, 9), (-1, 9), "Helvetica-Bold"),
    ]))
    sec_fc += [t_fc]

    # ── 5. DEPRECIACIÓN Y AMORTIZACIÓN ──────────────────────────────────
    sec_dep = []
    if dep_tab:
        sec_dep = h2("Tabla de Depreciación y Amortización")
        sec_dep += [Paragraph("Cargos anuales por depreciación de activos fijos y "
                            "amortización de intangibles.", st_nota)]
        comps = [k for k in dep_tab if k != "Total Depreciación"]
        filas_dep = [anos]
        for comp in comps:
            serie = dep_tab[comp]
            vals = [serie[i] if i < len(serie) else 0 for i in range(h + 1)]
            filas_dep.append([comp] + [fmt_m(v) if v else "—" for v in vals])
        if "Total Depreciación" in dep_tab:
            serie = dep_tab["Total Depreciación"]
            vals = [serie[i] if i < len(serie) else 0 for i in range(h + 1)]
            filas_dep.append(["Total Depreciación"] + [fmt_m(v) for v in vals])
        t_dep = tabla(filas_dep)
        ultima = len(filas_dep) - 1
        t_dep.setStyle(TableStyle([
            ("BACKGROUND", (0, ultima), (-1, ultima), AZUL),
            ("TEXTCOLOR", (0, ultima), (-1, ultima), colors.white),
            ("FONTNAME", (0, ultima), (-1, ultima), "Helvetica-Bold"),
        ]))
        sec_dep += [t_dep]

    # ── 6. INDICADORES DE RENTABILIDAD ──────────────────────────────────
    sec_ind = h2("Indicadores de Rentabilidad")
    tir_s = "N/D" if _es_nan(ind_sin.get("tir", float('nan'))) else f"{ind_sin['tir']:.2%}"
    tir_c = "N/D" if _es_nan(ind_con.get("tir", float('nan'))) else f"{ind_con['tir']:.2%}"

    def cmp_tir_wacc(ind):
        t, w = ind.get("tir"), ind.get("wacc", 0)
        if t is None or _es_nan(t):
            return "N/D"
        return "SÍ  (TIR > WACC)" if t > w else "NO  (TIR ≤ WACC)"

    filas_kpi = [
        ["Indicador", "Sin Valor Terminal", "Con Valor Terminal (Empresa en Marcha)"],
        ["VAN", fmt_m(ind_sin.get("van")), fmt_m(ind_con.get("van"))],
        ["TIR", tir_s, tir_c],
        ["WACC", f"{ind_sin.get('wacc', 0):.2%}", f"{ind_con.get('wacc', 0):.2%}"],
        ["Payback", f"Año {ind_sin['payback']}" if ind_sin.get("payback") else "No recuperado",
                    f"Año {ind_con['payback']}" if ind_con.get("payback") else "No recuperado"],
        ["¿Proyecto atractivo?", cmp_tir_wacc(ind_sin), cmp_tir_wacc(ind_con)],
        ["Decisión", ind_sin.get("decision", "—"), ind_con.get("decision", "—")],
    ]
    t_kpi = tabla(filas_kpi, col0_ratio=0.28)
    fdec = len(filas_kpi) - 1
    c_sin = VERDE if (ind_sin.get("van") or 0) > 0 else ROJO
    c_con = VERDE if (ind_con.get("van") or 0) > 0 else ROJO
    t_kpi.setStyle(TableStyle([
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (1, fdec), (1, fdec), c_sin),
        ("BACKGROUND", (2, fdec), (2, fdec), c_con),
        ("TEXTCOLOR", (1, fdec), (-1, fdec), colors.white),
        ("FONTNAME", (0, fdec), (-1, fdec), "Helvetica-Bold"),
    ]))
    sec_ind += [t_kpi, Spacer(1, 12)]

    nota = ("<b>Interpretación:</b> un VAN positivo indica que el proyecto genera valor por "
            "encima del costo de capital (WACC). La TIR es la tasa de rendimiento intrínseca; "
            "si TIR &gt; WACC el proyecto es atractivo. El Valor Terminal captura el potencial "
            "de la empresa como negocio en marcha más allá del horizonte de evaluación.")
    caja = Table([[Paragraph(nota, st_intro)]], colWidths=[util])
    caja.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef9e7")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#f39c12")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    sec_ind += [caja]

    # ── Ensamblado: cada sección entera (nunca se parte) y 2 por hoja si caben ──
    # KeepTogether mantiene la sección completa; al no forzar saltos de página,
    # ReportLab coloca la siguiente sección en la misma hoja cuando hay espacio.
    for sec in (sec_resumen, sec_er, sec_fc, sec_dep, sec_ind):
        if not sec:
            continue
        story.append(KeepTogether(sec))
        story.append(Spacer(1, 22))

    return story


def _exportar_pdf_reportlab_bytes(resultado: dict) -> bytes:
    """ReportLab: PDF profesional COMPLETO retornando bytes (para Flask/nube)."""
    import io
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        rightMargin=12 * mm, leftMargin=12 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="Flujo de Caja — Evaluación Financiera",
        author="Limited Group S.A.",
    )
    doc.build(_construir_story(resultado), canvasmaker=_make_numbered_canvas())
    return buffer.getvalue()


def _exportar_pdf_reportlab(resultado: dict, output_path: str):
    """ReportLab: PDF profesional COMPLETO a disco (mismo contenido que el modo bytes)."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate

    doc = SimpleDocTemplate(
        output_path, pagesize=landscape(A4),
        rightMargin=12 * mm, leftMargin=12 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="Flujo de Caja — Evaluación Financiera",
        author="Limited Group S.A.",
    )
    doc.build(_construir_story(resultado), canvasmaker=_make_numbered_canvas())
    print(f"[PDF] Generado con ReportLab: {output_path}")




if __name__ == "__main__":
    from model import ejecutar_modelo
    resultado = ejecutar_modelo()
    exportar_pdf(resultado, "reporte_flujo_caja.pdf")
