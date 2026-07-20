"""config.py — Constantes del tutor y reglas de seguridad.

Qué hace este módulo:
  - Define modelo Gemini, perfiles del asistente (`PERFILES`) y `ASSISTANT_CONFIG_DEFAULT`.
  - Guarda constantes de la Fase 2: dominio Python, patrones sospechosos, límites.

Para qué sirve:
  - Un solo sitio para cambiar parámetros sin tocar la lógica de cada función.

Qué NO debes hacer aquí:
  - Normalmente no modificas este archivo en la práctica (salvo experimentos opcionales).
"""
from pathlib import Path
MODEL = "gemini-3-flash-preview"      # confirmar cuál usaréis en Parte 4
TEMPERATURE = 0.2                     # la guía recomienda 0.2 para el benchmark
MAX_TOKENS_INPUT = 8_000
MAX_INPUT_CHARS = 2_000
MAX_TURNOS_HISTORIAL = 4              # límite explícito de la guía

# Máximo de elementos de contexto por turno (acordado en el README: máx. 3
# docs + 2 FAQ) y longitud máxima de cada cuerpo de documento antes de truncar.
MAX_DOCS_POR_TURNO = 3        
MAX_FAQ_POR_TURNO = 2
MAX_DOC_CHARS = 600


# Departamentos "transversales": sus documentos son relevantes para
# cualquier empleado, no solo para quien pertenece a ese departamento
# (vacaciones, conducta, RRHH, beneficios, buddy... aplican a todos).
DEPARTAMENTOS_TRANSVERSALES = {"people"}

# Detección de inyección (Parte 3)
PATRONES_SOSPECHOSOS = (
    "ignora instrucciones",
    "ignore previous",
    "actúa como",
    "actua como",
    "disregard",
    "system:",
    "jailbreak",
)

# TODO Track B: derivar de tags reales en onboarding_docs.json / faq_onboarding.json
DOMINIO_KEYWORDS = (
    
)

# --- Parte 4 (Benchmark) ---
# Añade constantes nuevas al final del
# fichero. MODEL y TEMPERATURE ya existen arriba y se reutilizan tal cual
# (la guía recomienda la MISMA temperatura para todos los modelos del
# benchmark, así que no se define una nueva).

BENCHMARK_MODELS = [
    "gemini-2.5-flash",   # modelo estable, ya probado en producción
    MODEL,                # "gemini-3-flash-preview" — el que usa la app hoy
]

BENCHMARK_DATA_PATH = Path(__file__).parent / "data" / "preguntas_benchmark.json"
OUTPUT_DIR = Path(__file__).parent / "output"
ENTREGABLES_DIR = Path(__file__).parent / "entregables"

MIN_CASOS_BENCHMARK = 10

