"""
generar_html.py — Genera el HTML del reporte para conversión a PDF con Chrome.
"""
import os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

from model import ejecutar_modelo
from pdf_generator import construir_html

resultado = ejecutar_modelo()
html = construir_html(resultado)

out_path = os.path.join(script_dir, "reporte_flujo_caja.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML generado: {out_path}")
