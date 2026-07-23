"""report.py — Generación de CSV e informe a partir del benchmark (Parte 4).

Qué hace este módulo:
  - `guardar_csv()` exporta todas las filas del benchmark a `output/`.
  - `generar_reporte_md()` produce un informe Markdown con latencia media,
    tokens de salida medios y % de JSON válido por modelo (para los casos
    de tipo "checklist"), más el listado de errores.

Para qué sirve:
  - Punto de partida para rellenar `entregables/matriz_decision.md` y
    `entregables/recomendacion.md` con datos reales en vez de intuición.

Qué NO hace este módulo:
  - No evalúa fidelidad/tono/seguridad (columnas de `rubrica_benchmark.md`)
    — eso requiere leer las respuestas y puntuarlas manualmente 1–3, ya que
    es un juicio de contenido que no se puede automatizar sin otro LLM
    evaluador (fuera del alcance de esta práctica).
"""

import csv
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from benchmark import FilaBenchmark
from config import BENCHMARK_MODELS, OUTPUT_DIR, TEMPERATURE


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def guardar_csv(filas: list[FilaBenchmark]) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"benchmark_{_stamp()}.csv"
    if not filas:
        path.write_text("", encoding="utf-8")
        return path

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(filas[0]).keys()))
        writer.writeheader()
        for fila in filas:
            writer.writerow(asdict(fila))
    return path


def _resumen_por_modelo(filas: list[FilaBenchmark]) -> dict[str, dict[str, float]]:
    ok = [f for f in filas if not f.error]
    lat: dict[str, list[int]] = defaultdict(list)
    out_tok: dict[str, list[int]] = defaultdict(list)
    total_tok: dict[str, list[int]] = defaultdict(list)
    json_casos: dict[str, list[bool]] = defaultdict(list)

    for f in ok:
        lat[f.modelo].append(f.elapsed_ms)
        if f.output_tokens is not None:
            out_tok[f.modelo].append(f.output_tokens)
        if f.total_tokens is not None:
            total_tok[f.modelo].append(f.total_tokens)
        if f.json_valido is not None:
            json_casos[f.modelo].append(f.json_valido)

    resumen: dict[str, dict[str, float]] = {}
    for modelo in BENCHMARK_MODELS:
        json_lista = json_casos.get(modelo, [])
        resumen[modelo] = {
            "runs_ok": float(len(lat.get(modelo, []))),
            "elapsed_ms_media": mean(lat[modelo]) if lat.get(modelo) else 0.0,
            "output_tokens_media": mean(out_tok[modelo]) if out_tok.get(modelo) else 0.0,
            "total_tokens_medio": mean(total_tok[modelo]) if total_tok.get(modelo) else 0.0,
            "json_valido_pct": (sum(json_lista) / len(json_lista) * 100) if json_lista else -1.0,
        }
    return resumen


def generar_reporte_md(filas: list[FilaBenchmark], csv_path: Path) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"report_{_stamp()}.md"
    resumen = _resumen_por_modelo(filas)
    errores = [f for f in filas if f.error]
    total_tokens_todas_filas = sum(f.total_tokens or 0 for f in filas if not f.error)

    lineas = [
        "# Informe de benchmark — Employee Onboarding Assistant (Bridge SA)",
        "",
        f"- Generado: {datetime.now(timezone.utc).isoformat()}",
        f"- Temperatura: {TEMPERATURE}",
        f"- Modelos: {', '.join(BENCHMARK_MODELS)}",
        f"- Casos ejecutados: {len({f.caso_id for f in filas})}",
        f"- CSV: `{csv_path.name}`",
        "",
        "## Latencia, tokens y % JSON válido (solo casos 'checklist') por modelo",
        "",
        "| Modelo | Runs OK | ms media | out tokens media | total tokens medio | % JSON válido |",
        "|--------|---------|----------|--------------------|--------------------|-----------------|",
    ]

    for modelo in BENCHMARK_MODELS:
        r = resumen[modelo]
        pct = "N/A" if r["json_valido_pct"] < 0 else f"{r['json_valido_pct']:.0f}%"
        lineas.append(
            f"| {modelo} | {int(r['runs_ok'])} | {r['elapsed_ms_media']:.0f} | "
            f"{r['output_tokens_media']:.1f} | {r['total_tokens_medio']:.1f} | {pct} |"
        )

    lineas.extend(
        [
            "",
            "## ¿Qué pasaría si duplicáramos el tráfico?",
            "",
            f"Este benchmark consumió aproximadamente **{total_tokens_todas_filas} tokens** "
            f"en total para {len({f.caso_id for f in filas})} casos × {len(BENCHMARK_MODELS)} modelos. "
            "Duplicar el tráfico de producción implicaría, en primera aproximación, duplicar "
            "también el consumo de tokens (y por tanto el coste) de forma lineal, salvo que se "
            "introduzca cacheo de contexto repetido o se reduzca el tamaño de `MAX_DOC_CHARS`/"
            "`MAX_DOCS_POR_TURNO`. La latencia percibida por usuario no debería degradarse mientras "
            "no se agote la cuota de peticiones concurrentes del proveedor; conviene vigilar los "
            "límites de rate-limit del modelo elegido antes de escalar. (Completar con cifras reales "
            "del CSV al redactar `entregables/recomendacion.md`.)",
            "",
            "## Errores",
            "",
        ]
    )
    if errores:
        for e in errores:
            lineas.append(f"- `{e.caso_id}` × `{e.modelo}`: {e.error}")
    else:
        lineas.append("Ninguno.")

    lineas.extend(
        [
            "",
            "## Siguiente paso",
            "",
            "1. Abre el CSV y puntúa cada fila 1–3 en Fidelidad / Relevancia / Tono / Seguridad "
            "(ver `entregables/rubrica_benchmark.md`).",
            "2. Completa `entregables/matriz_decision.md` con el modelo ganador por caso.",
            "3. Escribe la recomendación final en `entregables/recomendacion.md`.",
            "",
        ]
    )

    path.write_text("\n".join(lineas), encoding="utf-8")
    return path
