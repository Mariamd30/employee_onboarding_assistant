"""benchmark.py — Motor del benchmark (Parte 4).

Qué hace este módulo:
  - Carga `data/preguntas_benchmark.json` (mínimo 10 casos).
  - Para cada caso, construye el prompt real de la app reutilizando
    `context.construir_contexto()` y `prompts.build_chat_prompt()` /
    `prompts.build_checklist_prompt()` — el benchmark evalúa el pipeline
    real de selección de contexto + construcción de prompt, no solo al
    modelo desnudo.
  - Llama a cada modelo de `config.BENCHMARK_MODELS` con la MISMA
    temperatura (`config.TEMPERATURE`) y recoge latencia, tokens y
    respuesta (o el JSON, para los casos de tipo "checklist").
  - Los errores de API se capturan por fila sin detener la ejecución.

Para qué sirve:
  - Es la base para `report.py` (CSV + informe) y para rellenar
    `entregables/matriz_decision.md` y `entregables/recomendacion.md`.

Qué NO hace este módulo:
  - No pasa por `logic.py` ni por `validators.py`: llama al modelo
    directamente con el prompt ya construido, porque necesita variar el
    modelo por llamada (cosa que `gemini_client.safe_generate()` de momento
    no soporta — usa siempre `config.MODEL`). 
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from google import genai
from google.genai import types

import context
import prompts
from config import BENCHMARK_DATA_PATH, BENCHMARK_MODELS, TEMPERATURE
from gemini_auth import configurar_gemini_api_key

configurar_gemini_api_key()

DATA_DIR = BENCHMARK_DATA_PATH.parent

_client_instance: genai.Client | None = None


def _client() -> genai.Client:
    global _client_instance
    if _client_instance is None:
        _client_instance = genai.Client()
    return _client_instance


@dataclass
class FilaBenchmark:
    timestamp: str
    caso_id: str
    tipo: str
    empleado_id: str
    dia: int
    modelo: str
    elapsed_ms: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    respuesta: str
    json_valido: bool | None
    docs_usados: str
    error: str | None = None


def _llamar_modelo(prompt: str, model: str, *, json_mode: bool) -> tuple[str, dict]:
    """Mini-cliente propio del benchmark: permite variar el modelo por llamada."""
    started = time.time()
    config_kwargs = {"temperature": TEMPERATURE}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    response = _client().models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    elapsed_ms = int((time.time() - started) * 1000)
    um = response.usage_metadata
    metricas = {
        "elapsed_ms": elapsed_ms,
        "prompt_tokens": getattr(um, "prompt_token_count", None),
        "output_tokens": getattr(um, "candidates_token_count", None),
        "total_tokens": getattr(um, "total_token_count", None),
    }
    return (response.text or "").strip(), metricas


def cargar_casos(ruta=BENCHMARK_DATA_PATH) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("preguntas_benchmark.json debe ser una lista de casos")
    return data


def cargar_empleados() -> dict:
    ruta = DATA_DIR / "empleados_demo.json"
    with ruta.open(encoding="utf-8") as f:
        empleados = json.load(f)
    return {e["id"]: e for e in empleados}


def _construir_prompt(caso: dict, empleado: dict, docs: list[dict], faqs: list[dict]) -> tuple[str, bool, dict]:
    """Construye el prompt real de la app para un caso del benchmark.

    Devuelve (prompt, es_json, contexto_usado).
    """
    dia = caso.get("dia", 1)
    departamento = empleado.get("departamento")
    es_checklist = caso.get("tipo", "chat") == "checklist"

    if es_checklist:
        pregunta_sintetica = f"día {dia} onboarding checklist tareas"
        contexto = context.construir_contexto(pregunta_sintetica, departamento, docs=docs, faqs=faqs)
        prompt = prompts.build_checklist_prompt(empleado, dia, contexto)
    else:
        pregunta = caso["pregunta"]
        contexto = context.construir_contexto(pregunta, departamento, docs=docs, faqs=faqs)
        # Benchmark = 1 turno; no se simula historial previo.
        prompt = prompts.build_chat_prompt(empleado, dia, pregunta, contexto, historial=None)

    return prompt, es_checklist, contexto


def ejecutar_benchmark() -> list[FilaBenchmark]:
    casos = cargar_casos()
    empleados = cargar_empleados()
    # Carga única de docs/FAQ para todo el benchmark (evita releer disco
    # en cada combinación caso × modelo).
    docs = context.cargar_documentos()
    faqs = context.cargar_faq()

    filas: list[FilaBenchmark] = []

    for caso in casos:
        caso_id = caso["id"]
        empleado_id = caso.get("empleado_id", "emp_01")
        empleado = empleados.get(empleado_id)
        if empleado is None:
            print(f"AVISO: empleado {empleado_id!r} no encontrado, se omite caso {caso_id!r}")
            continue

        prompt, json_mode, contexto = _construir_prompt(caso, empleado, docs, faqs)
        docs_usados = ",".join(d["id"] for d in contexto["docs"])
        dia = caso.get("dia", 1)
        tipo = caso.get("tipo", "chat")

        for modelo in BENCHMARK_MODELS:
            ts = datetime.now(timezone.utc).isoformat()
            try:
                texto, m = _llamar_modelo(prompt, modelo, json_mode=json_mode)

                json_valido = None
                if json_mode:
                    try:
                        json.loads(texto)
                        json_valido = True
                    except json.JSONDecodeError:
                        json_valido = False

                filas.append(
                    FilaBenchmark(
                        timestamp=ts,
                        caso_id=caso_id,
                        tipo=tipo,
                        empleado_id=empleado_id,
                        dia=dia,
                        modelo=modelo,
                        elapsed_ms=m["elapsed_ms"],
                        prompt_tokens=m["prompt_tokens"],
                        output_tokens=m["output_tokens"],
                        total_tokens=m["total_tokens"],
                        respuesta=texto,
                        json_valido=json_valido,
                        docs_usados=docs_usados,
                    )
                )
                print(f"OK  {caso_id} × {modelo} ({m['elapsed_ms']} ms)")
            except Exception as exc:  # noqa: BLE001 — benchmark didáctico
                filas.append(
                    FilaBenchmark(
                        timestamp=ts,
                        caso_id=caso_id,
                        tipo=tipo,
                        empleado_id=empleado_id,
                        dia=dia,
                        modelo=modelo,
                        elapsed_ms=0,
                        prompt_tokens=None,
                        output_tokens=None,
                        total_tokens=None,
                        respuesta="",
                        json_valido=None,
                        docs_usados=docs_usados,
                        error=str(exc),
                    )
                )
                print(f"ERR {caso_id} × {modelo}: {exc}")
            # dentro del for modelo in BENCHMARK_MODELS: después de cada llamada:
            time.sleep(13)  # 60s / 5 peticiones ≈ 12s; 13s da margen
    return filas


def filas_a_dicts(filas: list[FilaBenchmark]) -> list[dict]:
    return [asdict(f) for f in filas]
