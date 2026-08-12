"""
main.py — Orquestador principal
Limited Group S.A. · Automatización Flujo de Caja

Uso:
  python3 main.py
  python3 main.py --config config.json --output reporte.pdf
"""

import sys
import os
import argparse
import json

def parse_args():
    p = argparse.ArgumentParser(description="Flujo de Caja — Limited Group S.A.")
    p.add_argument("--config", default="config.json", help="Ruta al archivo de configuración")
    p.add_argument("--output", default="reporte_flujo_caja.pdf", help="Ruta del PDF de salida")
    p.add_argument("--solo-consola", action="store_true", help="Solo muestra resultados en consola, sin PDF")
    return p.parse_args()


def imprimir_resumen(resultado: dict):
    cfg     = resultado["config"]
    fc      = resultado["flujo_caja"]
    ind_sin = resultado["indicadores_sin_vt"]
    ind_con = resultado["indicadores_con_vt"]
    h       = cfg["horizonte_evaluacion"]
    sep     = "─" * 70

    print(f"\n{sep}")
    print(f"  {cfg['empresa']['nombre'].upper()}")
    print(f"  Producto: {cfg['empresa']['producto']}")
    print(sep)

    # ── Flujo de caja ──────────────────────────────────────────────────
    print("\n  FLUJO DE CAJA LIBRE (USD)")
    print(f"  {'Año':<8} {'Sin Valor Terminal':>22} {'Con Valor Terminal':>22}")
    print(f"  {'─'*8} {'─'*22} {'─'*22}")
    for i in range(h + 1):
        f_sin = fc["flujo_sin_vt"][i]
        f_con = fc["flujo_con_vt"][i]
        print(f"  Año {i:<4} {f_sin:>22,.0f} {f_con:>22,.0f}")

    # ── Indicadores ────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  INDICADORES DE RENTABILIDAD")
    print(sep)

    import math
    for label, ind in [("Sin Valor Terminal", ind_sin), ("Con Valor Terminal", ind_con)]:
        tir_str = f"{ind['tir']:.2%}" if not math.isnan(ind.get("tir", float("nan"))) else "N/D"
        print(f"\n  [{label}]")
        print(f"    VAN  (WACC={ind['wacc']:.0%}): ${ind['van']:>20,.2f}")
        print(f"    TIR:               {tir_str:>20}")
        print(f"    Decisión:          {ind['decision']}")

    print(f"\n{sep}")
    print(f"  Valor Terminal (Perpetuidad): ${fc['valor_terminal']:>18,.0f}")
    print(f"  Capital de Trabajo inicial:   ${abs(fc['flujo_kw'][0]):>18,.0f}")
    print(f"  Inversión Neta Total:         ${abs(fc['inversiones'][0]):>18,.0f}")
    print(sep)

    # ── Tabla depreciación ─────────────────────────────────────────────
    dep_tab = resultado["depreciacion_tabla"]
    print("\n  DEPRECIACIÓN POR AÑO ($)")
    print(f"  {'Componente':<32} " + " ".join(f"{'Año '+str(i):>12}" for i in range(1, h+1)))
    print(f"  {'─'*32} {'─'*12}" * h)
    for comp, vals in dep_tab.items():
        fila_str = " ".join(f"{vals[i]:>12,.0f}" for i in range(1, h+1))
        bold_mark = "  >>> " if "Total" in comp else "      "
        print(f"{bold_mark}{comp:<30} {fila_str}")


def main():
    args = parse_args()

    # Cambiar al directorio del script para localizar config.json y output
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    config_path = args.config
    output_path = args.output

    print(f"\n{'='*60}")
    print("  FLUJO DE CAJA — LIMITED GROUP S.A.")
    print(f"  Config: {config_path}")
    print(f"{'='*60}")

    # ── 1. Verificar config ────────────────────────────────────────────
    if not os.path.exists(config_path):
        print(f"[ERROR] No se encontró el archivo: {config_path}")
        sys.exit(1)

    print(f"\n[1/3] Cargando configuración desde '{config_path}'...")

    # ── 2. Ejecutar modelo ─────────────────────────────────────────────
    print("[2/3] Ejecutando modelo financiero...")
    try:
        from model import ejecutar_modelo
        resultado = ejecutar_modelo(config_path)
        print("      Modelo calculado correctamente.")
    except Exception as e:
        print(f"[ERROR] Fallo en el modelo: {e}")
        raise

    imprimir_resumen(resultado)

    # ── 3. Generar PDF ─────────────────────────────────────────────────
    if not args.solo_consola:
        print(f"\n[3/3] Generando reporte PDF → '{output_path}'...")
        try:
            from pdf_generator import exportar_pdf
            exportar_pdf(resultado, output_path)
            abs_path = os.path.abspath(output_path)
            print(f"\n✓ Reporte listo: {abs_path}")
        except Exception as e:
            print(f"[ERROR] Fallo en generación PDF: {e}")
            raise
    else:
        print("\n[3/3] Modo consola — PDF omitido.")

    print("\n¡Proceso completado exitosamente!\n")


if __name__ == "__main__":
    main()
