"""
model.py — Motor financiero del Flujo de Caja
Limited Group S.A. · Evaluación de Proyecto 6 años
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np
import numpy_financial as npf


def cargar_config(path: str = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# Parámetros derivados
# ─────────────────────────────────────────────────────────────────────────────

def calcular_unidades(cfg: dict) -> List[int]:
    """Demanda por año (índice 0 = Año 0, sin operación)."""
    base = cfg["demanda"]["unidades_base"]
    inc  = cfg["demanda"]["incremento_anno_4"]
    a_inc = cfg["demanda"]["anno_incremento"]
    h = cfg["horizonte_evaluacion"]
    return [0] + [
        int(base * (1 + inc)) if (i >= a_inc) else base
        for i in range(1, h + 1)
    ]


def calcular_precios(cfg: dict) -> List[float]:
    p1 = cfg["precios"]["precio_annos_1_2"]
    p2 = cfg["precios"]["precio_anno_3_adelante"]
    ac = cfg["precios"]["anno_cambio_precio"]
    h  = cfg["horizonte_evaluacion"]
    return [0] + [p2 if i >= ac else p1 for i in range(1, h + 1)]


def calcular_ingresos(cfg: dict) -> List[float]:
    u = calcular_unidades(cfg)
    p = calcular_precios(cfg)
    return [u[i] * p[i] for i in range(len(u))]


# ─────────────────────────────────────────────────────────────────────────────
# Costos
# ─────────────────────────────────────────────────────────────────────────────

def calcular_costos_variables(cfg: dict) -> List[float]:
    cv = cfg["costos_variables"]
    u  = calcular_unidades(cfg)
    h  = cfg["horizonte_evaluacion"]
    a_imp = cv["anno_inicio_importacion"]
    cvu_base = cv["mano_de_obra"] + cv["materiales_base"]     + cv["costos_indirectos"]
    cvu_imp  = cv["mano_de_obra"] + cv["materiales_importados"] + cv["costos_indirectos"]
    return [0] + [
        u[i] * (cvu_imp if i >= a_imp else cvu_base)
        for i in range(1, h + 1)
    ]


def calcular_costos_fijos(cfg: dict) -> List[float]:
    cf = cfg["costos_fijos"]
    h  = cfg["horizonte_evaluacion"]
    a  = cf["anno_inicio_incremento"]
    base = cf["costo_fijo_fabricacion_base"]
    inc  = cf["incremento_ampliacion"]
    return [0] + [base + inc if i >= a else base for i in range(1, h + 1)]


def calcular_gastos_admon(cfg: dict) -> List[float]:
    cf = cfg["costos_fijos"]
    h  = cfg["horizonte_evaluacion"]
    a  = cf["anno_inicio_gastos_ampliados"]
    base = cf["gastos_admon_ventas_base"]
    amp  = cf["gastos_admon_ventas_ampliados"]
    return [0] + [amp if i >= a else base for i in range(1, h + 1)]


def calcular_comisiones(cfg: dict) -> List[float]:
    ingresos = calcular_ingresos(cfg)
    pct = cfg["costos_fijos"]["comision_ventas_pct"]
    return [ing * pct for ing in ingresos]


def calcular_egresos_desembolsables(cfg: dict) -> List[float]:
    cv  = calcular_costos_variables(cfg)
    cf  = calcular_costos_fijos(cfg)
    ga  = calcular_gastos_admon(cfg)
    com = calcular_comisiones(cfg)
    h   = cfg["horizonte_evaluacion"]
    return [cv[i] + cf[i] + ga[i] + com[i] for i in range(h + 1)]


# ─────────────────────────────────────────────────────────────────────────────
# Depreciación y amortización
# ─────────────────────────────────────────────────────────────────────────────

def calcular_depreciacion(cfg: dict) -> List[float]:
    """Depreciación total por año. Año 0 = 0."""
    d   = cfg["depreciacion"]
    inv = cfg["inversion_inicial"]
    amp = cfg["ampliacion"]
    rep = cfg["reemplazo_maquinaria"]
    h   = cfg["horizonte_evaluacion"]

    dep_anual = {
        "obras_base":    inv["obras_fisicas"] / d["obras_fisicas_annos"],
        "obras_amp":     amp["obras_fisicas_adicionales"] / d["obras_fisicas_annos"],
        "maq1":          inv["maquinaria_1"] / d["maquinaria_annos"],
        "maq1_rep":      rep["costo_reemplazo"] / d["maquinaria_annos"],
        "maq2":          inv["maquinaria_2"] / d["maquinaria_annos"],
        "maq_adic":      amp["maquinaria_adicional"] / d["maquinaria_annos"],
    }

    resultado = [0.0]
    for i in range(1, h + 1):
        dep = dep_anual["obras_base"] + dep_anual["maq2"]

        if i >= amp["anno"] + 1:            # Obras amp. se deprecian a partir del año siguiente a la inversión
            dep += dep_anual["obras_amp"]
        if i >= amp["anno"] + 1:            # Maq adicional desde año 4
            dep += dep_anual["maq_adic"]

        if i <= rep["annos_usados"]:         # Maquinaria 1 original (años 1-4)
            dep += dep_anual["maq1"]
        if i > rep["annos_usados"]:          # Maquinaria 1 reemplazo (años 5-6)
            dep += dep_anual["maq1_rep"]

        resultado.append(dep)

    return resultado


def calcular_amortizacion(cfg: dict) -> List[float]:
    """Amortización lineal de intangibles (años 1-5)."""
    inv  = cfg["inversion_inicial"]
    d    = cfg["depreciacion"]
    h    = cfg["horizonte_evaluacion"]
    cuota = inv["intangibles_total"] / d["intangibles_amortizacion_annos"]
    return [0.0] + [
        cuota if i <= d["intangibles_amortizacion_annos"] else 0.0
        for i in range(1, h + 1)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Capital de Trabajo
# ─────────────────────────────────────────────────────────────────────────────

def calcular_capital_de_trabajo(cfg: dict) -> Dict[str, List[float]]:
    """
    KW invertido al INICIO de cada año para cubrir las operaciones de ese año.
    Convenio: inversión en período t cubre operaciones del período t+1.
      Año 0 → cubre Año 1
      Año 2 → cubre incremento del Año 3
      Año 3 → cubre incremento del Año 4
      Año 6 → recuperación total
    """
    egresos = calcular_egresos_desembolsables(cfg)
    frac    = cfg["capital_de_trabajo"]["fraccion"]
    h       = cfg["horizonte_evaluacion"]

    # kw_req[t] = KW que hay que tener disponible al inicio del año t+1
    # (se invierte al final del año t)
    kw_req = [egresos[min(i + 1, h)] * frac for i in range(h + 1)]
    kw_req[h] = 0.0   # Al final del proyecto no se requiere más KW

    flujo_kw = [0.0] * (h + 1)
    flujo_kw[0] = -kw_req[0]            # Inversión pre-operativa

    for i in range(1, h):
        delta = kw_req[i] - kw_req[i - 1]
        if delta > 0:
            flujo_kw[i] = -delta        # Solo se invierte si aumenta

    # Recuperación completa en el último período
    flujo_kw[h] = kw_req[h - 1]

    # Nivel requerido por año (para el reporte)
    kw_nivel = [egresos[min(i + 1, h)] * frac for i in range(h + 1)]
    kw_nivel[h] = kw_req[h - 1]

    return {
        "kw_requerido":  kw_nivel,
        "flujo_kw":      flujo_kw,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Valor libro activo en venta / Resultado en disposición
# ─────────────────────────────────────────────────────────────────────────────

def calcular_venta_activo(cfg: dict) -> Dict[str, float]:
    """
    Maquinaria 1: vendida al final del año 4 para reemplazo en año 5.
    Costo original: $10M | Vida contable: 10 años | Años usados: 4
    """
    rep    = cfg["reemplazo_maquinaria"]
    d      = cfg["depreciacion"]
    tax    = cfg["impuestos"]["tasa_impositiva"]

    costo          = rep["costo_reemplazo"]          # mismo costo que la original
    dep_acum       = costo / d["maquinaria_annos"] * rep["annos_usados"]
    valor_libro    = costo - dep_acum
    precio_venta   = rep["valor_salvamento_maquina_vieja"]
    ganancia_perd  = precio_venta - valor_libro
    impuesto_disp  = ganancia_perd * tax             # negativo = ahorro fiscal
    flujo_neto     = precio_venta - impuesto_disp

    return {
        "anno":           rep["anno_venta"],
        "costo":          costo,
        "dep_acumulada":  dep_acum,
        "valor_libro":    valor_libro,
        "precio_venta":   precio_venta,
        "ganancia_perd":  ganancia_perd,
        "impuesto":       impuesto_disp,
        "flujo_neto_venta": flujo_neto,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Estado de Resultados
# ─────────────────────────────────────────────────────────────────────────────

def calcular_estado_resultados(cfg: dict) -> Dict[str, List[float]]:
    ingresos  = calcular_ingresos(cfg)
    egresos   = calcular_egresos_desembolsables(cfg)
    dep       = calcular_depreciacion(cfg)
    amort     = calcular_amortizacion(cfg)
    tax_rate  = cfg["impuestos"]["tasa_impositiva"]
    h         = cfg["horizonte_evaluacion"]

    ebit, impuesto, utilidad_neta = [], [], []
    for i in range(h + 1):
        e = ingresos[i] - egresos[i] - dep[i] - amort[i]
        t = max(0.0, e * tax_rate)
        ebit.append(e)
        impuesto.append(-t)
        utilidad_neta.append(e - t)

    return {
        "ingresos":       ingresos,
        "egresos_op":     [-e for e in egresos],
        "depreciacion":   [-d for d in dep],
        "amortizacion":   [-a for a in amort],
        "ebit":           ebit,
        "impuesto":       impuesto,
        "utilidad_neta":  utilidad_neta,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Depreciación por componente (tabla detallada)
# ─────────────────────────────────────────────────────────────────────────────

def tabla_depreciacion_detallada(cfg: dict) -> Dict[str, List[float]]:
    d   = cfg["depreciacion"]
    inv = cfg["inversion_inicial"]
    amp = cfg["ampliacion"]
    rep = cfg["reemplazo_maquinaria"]
    h   = cfg["horizonte_evaluacion"]

    filas = {
        "Obras físicas base":          (inv["obras_fisicas"],              d["obras_fisicas_annos"], 1),
        "Obras físicas ampliación":    (amp["obras_fisicas_adicionales"],  d["obras_fisicas_annos"], amp["anno"] + 1),
        "Maquinaria 2":                (inv["maquinaria_2"],               d["maquinaria_annos"],    1),
        "Maquinaria 1 (original)":     (inv["maquinaria_1"],               d["maquinaria_annos"],    1),
        "Maquinaria 1 (reemplazo)":    (rep["costo_reemplazo"],            d["maquinaria_annos"],    rep["annos_usados"] + 1),
        "Maquinaria adicional":        (amp["maquinaria_adicional"],       d["maquinaria_annos"],    amp["anno"] + 1),
    }

    tabla: Dict[str, List[float]] = {}
    for nombre, (costo, vida, anno_inicio) in filas.items():
        cuota = costo / vida
        fila  = [0.0]
        for i in range(1, h + 1):
            if nombre == "Maquinaria 1 (original)":
                fila.append(cuota if i <= rep["annos_usados"] else 0.0)
            elif nombre == "Maquinaria 1 (reemplazo)":
                fila.append(cuota if i >= anno_inicio else 0.0)
            else:
                fila.append(cuota if i >= anno_inicio else 0.0)
        tabla[nombre] = fila

    tabla["Total Depreciación"] = [
        sum(tabla[k][i] for k in tabla) for i in range(h + 1)
    ]
    return tabla


# ─────────────────────────────────────────────────────────────────────────────
# Inversiones
# ─────────────────────────────────────────────────────────────────────────────

def calcular_inversiones(cfg: dict) -> List[float]:
    inv = cfg["inversion_inicial"]
    amp = cfg["ampliacion"]
    rep = cfg["reemplazo_maquinaria"]
    h   = cfg["horizonte_evaluacion"]

    flujo = [0.0] * (h + 1)
    flujo[0]              = -inv["total_inversion_neta"]
    flujo[amp["anno"]]   += -amp["total"]
    flujo[rep["anno_compra"]] += -rep["costo_reemplazo"]
    return flujo


# ─────────────────────────────────────────────────────────────────────────────
# Valor Terminal (empresa como negocio en marcha)
# ─────────────────────────────────────────────────────────────────────────────

def calcular_valor_terminal(cfg: dict, fcf_operativo_ultimo: float) -> float:
    """
    Perpetuidad: VT = FCF_operativo_año6 / WACC
    FCF operativo = UTILIDAD_NETA + DEP + AMORT (sin reinversiones)
    """
    wacc = cfg["wacc"]
    return fcf_operativo_ultimo / wacc


# ─────────────────────────────────────────────────────────────────────────────
# Flujo de Caja Libre del Proyecto
# ─────────────────────────────────────────────────────────────────────────────

def calcular_flujo_caja(cfg: dict) -> Dict:
    er     = calcular_estado_resultados(cfg)
    dep    = calcular_depreciacion(cfg)
    amort  = calcular_amortizacion(cfg)
    inv    = calcular_inversiones(cfg)
    kw_d   = calcular_capital_de_trabajo(cfg)
    venta  = calcular_venta_activo(cfg)
    h      = cfg["horizonte_evaluacion"]

    flujo = [0.0] * (h + 1)
    for i in range(h + 1):
        flujo[i] = (
            er["utilidad_neta"][i]  # Utilidad Neta después de impuesto
            + dep[i]                # Add-back depreciación (no caja)
            + amort[i]              # Add-back amortización (no caja)
        )

    # Inversiones (capex y ampliaciones)
    for i in range(h + 1):
        flujo[i] += inv[i]

    # Capital de trabajo
    for i in range(h + 1):
        flujo[i] += kw_d["flujo_kw"][i]

    # Venta de activo fijo (neta de impuesto) en año 4
    a_venta = venta["anno"]
    flujo[a_venta] += venta["flujo_neto_venta"]

    # Valor Terminal en año 6 (empresa continúa)
    fcf_op_ultimo = er["utilidad_neta"][h] + dep[h] + amort[h]
    vt = calcular_valor_terminal(cfg, fcf_op_ultimo)

    flujo_con_vt  = flujo.copy()
    flujo_con_vt[h] += vt

    return {
        "utilidad_neta":   er["utilidad_neta"],
        "depreciacion":    dep,
        "amortizacion":    amort,
        "inversiones":     inv,
        "flujo_kw":        kw_d["flujo_kw"],
        "kw_requerido":    kw_d["kw_requerido"],
        "venta_activo":    venta,
        "flujo_sin_vt":    flujo,
        "valor_terminal":  vt,
        "flujo_con_vt":    flujo_con_vt,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Indicadores VAN y TIR
# ─────────────────────────────────────────────────────────────────────────────

def calcular_indicadores(cfg: dict, flujos: List[float]) -> Dict[str, float]:
    wacc = cfg["wacc"]
    van  = float(npf.npv(wacc, flujos))

    # Intentar TIR
    try:
        tir = float(npf.irr(flujos))
    except Exception:
        tir = float("nan")

    # Período de recuperación simple
    acum  = 0.0
    payback = None
    for i, f in enumerate(flujos):
        acum += f
        if acum >= 0 and payback is None:
            payback = i

    # VAN descontado de cada período
    pv_por_periodo = [
        flujos[i] / (1 + wacc) ** i for i in range(len(flujos))
    ]

    return {
        "wacc":            wacc,
        "van":             van,
        "tir":             tir,
        "payback":         payback,
        "pv_por_periodo":  pv_por_periodo,
        "decision":        "VIABLE - Crea valor" if van > 0 else "NO VIABLE - Destruye valor",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada: genera el modelo completo
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_modelo(config_path: str = "config.json") -> Dict:
    cfg = cargar_config(config_path)
    er  = calcular_estado_resultados(cfg)
    fc  = calcular_flujo_caja(cfg)
    dep_tabla = tabla_depreciacion_detallada(cfg)

    indicadores_sin_vt = calcular_indicadores(cfg, fc["flujo_sin_vt"])
    indicadores_con_vt = calcular_indicadores(cfg, fc["flujo_con_vt"])

    return {
        "config":               cfg,
        "ingresos":             er["ingresos"],
        "costos_variables":     calcular_costos_variables(cfg),
        "costos_fijos":         calcular_costos_fijos(cfg),
        "gastos_admon":         calcular_gastos_admon(cfg),
        "comisiones":           calcular_comisiones(cfg),
        "egresos_desembolsables": calcular_egresos_desembolsables(cfg),
        "estado_resultados":    er,
        "depreciacion_tabla":   dep_tabla,
        "flujo_caja":           fc,
        "indicadores_sin_vt":   indicadores_sin_vt,
        "indicadores_con_vt":   indicadores_con_vt,
        "unidades":             calcular_unidades(cfg),
        "precios":              calcular_precios(cfg),
    }


if __name__ == "__main__":
    import pprint
    resultado = ejecutar_modelo()
    fc = resultado["flujo_caja"]
    ind = resultado["indicadores_con_vt"]

    print("\n=== FLUJO DE CAJA (con Valor Terminal) ===")
    for i, f in enumerate(fc["flujo_con_vt"]):
        print(f"  Año {i}: ${f:>20,.0f}")

    print(f"\n  VAN  (WACC={ind['wacc']:.0%}): ${ind['van']:>20,.0f}")
    print(f"  TIR:                   {ind['tir']:.2%}" if not np.isnan(ind['tir']) else "  TIR: N/D")
    print(f"  Decisión: {ind['decision']}")
