"""context.py — Selección de contexto para el Employee Onboarding Assistant.

Qué hace este módulo:
  - `cargar_documentos()` / `cargar_faq()` leen `data/onboarding_docs.json` y
    `data/faq_onboarding.json`.
  - `construir_contexto()` elige, para una pregunta y un departamento dados,
    como máximo `MAX_DOCS_POR_TURNO` documentos y `MAX_FAQ_POR_TURNO` entradas de FAQ (sin
    volcar todo el JSON en el prompt), y trunca cuerpos largos.

Para qué sirve:
  - No enviar todos los documentos en cada llamada (ahorro de tokens y ruido),
    tal y como pide el enunciado de la Parte 2.

Qué NO hace este módulo:
  - No construye el prompt final (eso es `prompts.py`).
  - No valida la entrada del usuario (eso es `validators.py`).
  - No decide si hay que escalar a RRHH/IT/People (eso vive en la
    documentación seleccionada + `prompts.py`, que instruye al modelo a citar
    fuentes y derivar cuando corresponda).
"""

import json
from pathlib import Path

from config import MAX_DOCS_POR_TURNO, MAX_FAQ_POR_TURNO, MAX_DOC_CHARS, DEPARTAMENTOS_TRANSVERSALES

DATA_DIR = Path(__file__).parent / "data"
DOCS_PATH = DATA_DIR / "onboarding_docs.json"
FAQ_PATH = DATA_DIR / "faq_onboarding.json"


def cargar_documentos(ruta: Path = DOCS_PATH) -> list[dict]:
    """Carga `onboarding_docs.json` desde disco."""
    with ruta.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("onboarding_docs.json debe ser una lista de documentos")
    return data


def cargar_faq(ruta: Path = FAQ_PATH) -> list[dict]:
    """Carga `faq_onboarding.json` desde disco."""
    with ruta.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("faq_onboarding.json debe ser una lista de entradas")
    return data


def _truncar(texto: str, max_chars: int = MAX_DOC_CHARS) -> str:
    """Recorta un texto largo añadiendo '...' si hace falta."""
    texto = texto or ""
    if len(texto) <= max_chars:
        return texto
    return texto[:max_chars].rstrip() + "..."


def _puntuar_documento(doc: dict, pregunta: str, departamento: str | None) -> int:
    """Puntúa un documento por relevancia respecto a pregunta/departamento.

    - +3 si el departamento del documento coincide con el del empleado.
    - +3 si el departamento del documento es transversal (people).
    - +2 por cada tag del documento que aparece literalmente en la pregunta.
    """
    score = 0
    doc_depto = doc.get("departamento", "")

    if departamento and doc_depto == departamento:
        score += 3
    if doc_depto in DEPARTAMENTOS_TRANSVERSALES:
        score += 3

    q = (pregunta or "").lower()
    for tag in doc.get("tags", []):
        if tag.lower().replace("_", " ") in q or tag.lower() in q:
            score += 2

    return score


def _puntuar_faq(entry: dict, pregunta: str) -> int:
    """Puntúa una entrada de FAQ por coincidencia de tags/palabras con la pregunta."""
    score = 0
    q = (pregunta or "").lower()
    for tag in entry.get("tags", []):
        if tag.lower().replace("_", " ") in q or tag.lower() in q:
            score += 2
    # Coincidencia simple de palabras sueltas (>3 letras) entre pregunta y la
    # pregunta guardada en el FAQ, para casos sin tags que la cubran.
    palabras_pregunta = {w for w in q.split() if len(w) > 3}
    palabras_faq = {w for w in entry.get("pregunta", "").lower().split() if len(w) > 3}
    score += len(palabras_pregunta & palabras_faq)
    return score


def seleccionar_documentos(
    pregunta: str,
    departamento: str | None,
    docs: list[dict],
    max_docs: int = MAX_DOCS_POR_TURNO,
) -> list[dict]:
    """Elige como máximo `max_docs` documentos relevantes, con el cuerpo truncado."""
    puntuados = [(_puntuar_documento(d, pregunta, departamento), d) for d in docs]
    puntuados = [(s, d) for s, d in puntuados if s > 0]
    puntuados.sort(key=lambda x: x[0], reverse=True)

    seleccion = []
    for _, doc in puntuados[:max_docs]:
        doc_truncado = dict(doc)
        doc_truncado["cuerpo"] = _truncar(doc.get("cuerpo", ""))
        seleccion.append(doc_truncado)
    return seleccion


def seleccionar_faq(
    pregunta: str,
    faqs: list[dict],
    max_entradas: int = MAX_FAQ_POR_TURNO,
) -> list[dict]:
    """Elige como máximo `max_entradas` entradas de FAQ relevantes."""
    puntuadas = [(_puntuar_faq(e, pregunta), e) for e in faqs]
    puntuadas = [(s, e) for s, e in puntuadas if s > 0]
    puntuadas.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in puntuadas[:max_entradas]]


def construir_contexto(
    pregunta: str,
    departamento: str | None = None,
    docs: list[dict] | None = None,
    faqs: list[dict] | None = None,
) -> dict:
    """Punto de entrada único para `logic.py`.

    Devuelve `{"docs": [...], "faqs": [...]}` ya filtrado y truncado, listo
    para pasar a `prompts.py`. Si no se pasan `docs`/`faqs`, se cargan desde
    `data/` (útil para no repetir la carga en cada llamada si el orquestador
    ya los tiene cacheados).
    """
    docs = docs if docs is not None else cargar_documentos()
    faqs = faqs if faqs is not None else cargar_faq()

    return {
        "docs": seleccionar_documentos(pregunta, departamento, docs),
        "faqs": seleccionar_faq(pregunta, faqs),
    }