# Employee Onboarding Assistant — Bridge SA

Copiloto que acompaña a los empleados nuevos de **Bridge SA** (empresa ficticia) durante sus primeros días. Responde dudas apoyándose en documentación interna, genera checklists diarias en JSON y sabe cuándo derivar a People, IT o al manager/buddy del empleado.

Proyecto desarrollado como parte del bootcamp, integrando: Prompt & Context Engineering, Assistant Engineering & Robustez, y evaluación/benchmark de modelos.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Arquitectura](#-arquitectura)
- [Instalación y configuración](#-instalación-y-configuración)
- [Ejecución de las demos](#-ejecución-de-las-demos)
- [Estrategia de selección de contexto](#-estrategia-de-selección-de-contexto)
- [Robustez y seguridad](#-robustez-y-seguridad)
- [Benchmark y elección de modelo](#-benchmark-y-elección-de-modelo)
- [Flujo de trabajo del equipo](#-flujo-de-trabajo-del-equipo)

## 🎯 Funcionalidades

1. **Conversación (chat)**: el empleado pregunta libremente y el asistente responde en texto, citando documentación relevante y manteniendo hasta 4 turnos de historial.
2. **Checklist de la semana 1 (JSON)**: dado un empleado y un día de onboarding (1–5), el asistente devuelve un plan estructurado de tareas, cada una justificada con su documento fuente.

Ambas funcionalidades tienen en cuenta el **día de onboarding** (1–5) y el **perfil del empleado** (dev junior, comercial, remoto UE) para ajustar tono y contenido.

## 🏗 Arquitectura

Arquitectura modular por responsabilidades, sin script monolítico. Cada fichero tiene una única responsabilidad:

| Fichero | Responsabilidad |
|---|---|
| `gemini_auth.py` | Carga y validación de credenciales (`GEMINI_API_KEY`) |
| `gemini_client.py` | Cliente del LLM: llamadas a la API, parámetros del modelo |
| `context.py` | Selección de contexto: filtrado de docs/FAQ, truncado, historial acotado |
| `prompts.py` | Construcción de prompts dinámicos (system prompt, delimitadores) |
| `validators.py` | Validación de entrada y reglas fail-closed (Parte 3) |
| `logic.py` | Lógica de negocio: orquesta chat y generación del checklist JSON |
| `state.py` | Estado del empleado (perfil, día de onboarding, historial) |
| `benchmark.py` | Ejecución del benchmark comparando modelos (Parte 4) |
| `main.py` | Demos ejecutables de principio a fin |

> _Completar según avance la Parte 2: detallar cómo se comunican entre sí estos módulos (p. ej. `logic.py` llama a `context.py` → `prompts.py` → `gemini_client.py`)._

```
.
├── data/                     # Datos de partida (lore, docs, FAQ, empleados, casos trampa)
├── docs/                     # Documentación adicional (política de escalado, etc.)
│   └── politica-escalado.md
├── entregables/               # Plantillas de entrega (matriz de decisión, rúbrica, recomendación)
├── output/                    # Resultados del benchmark (CSV, informe) — Parte 4
├── gemini_auth.py
├── gemini_client.py
├── context.py
├── prompts.py
├── validators.py
├── logic.py
├── state.py
├── benchmark.py
├── main.py                    # Demos ejecutables
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Instalación y configuración

### Requisitos previos
- Python 3.10+
- Una API key de Google AI Studio (`GEMINI_API_KEY`)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Mariamd30/employee_onboarding_assistant
cd employee-onboarding-assistant

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir vuestra GEMINI_API_KEY real
```

**Nunca subáis vuestro `.env` con claves reales al repositorio.** Está incluido en `.gitignore`.

## ▶️ Ejecución de las demos

```bash
python main.py
```

El script ejecuta como mínimo:
- **Demo 1**: conversación de 1 turno (empleado dev junior).
- **Demo 2**: checklist JSON para el día 1.
- **Demo 3**: mismo mensaje con empleado comercial vs remoto UE (respuestas distintas).

## 🧠 Estrategia de selección de contexto

> _Completar en la Parte 2._ Documentar aquí: máximo de documentos/FAQ enviados por turno, criterio de filtrado (departamento, keywords), truncado de textos largos, y cómo se acota el historial conversacional (máx. 4 turnos).

## 🔒 Robustez y seguridad

Principio rector: **fail-closed** — si la validación de entrada falla, se rechaza la petición sin llamar al modelo.

**El asistente SÍ ayuda con:**

- Herramientas corporativas y primeros pasos
- Cultura de Bridge SA
- Vacaciones según documentación
- A quién contactar / cómo escalar

**El asistente NO debe:**

- Inventar políticas, plazos o cifras no documentadas
- Responder sobre salarios o datos de otros empleados
- Atender a participantes externos de los programas formativos

Ver [`docs/politica-escalado.md`](docs/politica-escalado.md) para el detalle de cuándo derivar a People, IT, manager/buddy o al buzón `onboarding@bridgesa.example`. **Esta política debe estar acordada por todo el equipo antes de implementar la lógica de la Parte 3.**

> _Completar en la Parte 3_: comparativa vulnerable vs. seguro, y enlace a `data/casos_trampa.json` con los 5 casos trampa propios.

## 📊 Benchmark y elección de modelo

> _Completar en la Parte 4._ Resultados en `output/`, decisión justificada en `entregables/matriz_decision.md` y `entregables/recomendacion.md`.

## 👥 Equipo

| Desarrollador/a |
|---|
| María Muriel Delgado |
| Javier Corchado |
| Yordanos Lopez Diaz |
| Alejandro Dietta Martin |

## 🔀 Flujo de trabajo del equipo

- Ramas: `main` (estable) ← `develop` (integración) ← `feature/*` (trabajo individual)
- Commits siguiendo [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)
- Toda PR requiere al menos 1 revisión aprobada antes de mergear
- Reparto de partes:

| Parte | Responsable |
|---|---|
| Setup + Parte 1 (contexto y datos) | [ya hecho] |
| Parte 2 · Track A — Cliente y estado (`gemini_auth.py`, `gemini_client.py`, `state.py`) | [Alejandro Dietta] |
| Parte 2 · Track B — Contenido y reglas (`context.py`, `prompts.py`, `validators.py`) | [Maria Murial] |
| Parte 2 · Integración (`logic.py`, `main.py`) | Ambos, tras cerrar A y B |
| Parte 3 (robustez) | _por asignar_ |
| Parte 4 (benchmark) | _por asignar_ |


> Cada miembro lidera al menos una parte y revisa las PRs de las demás, cumpliendo la regla mínima de una PR revisada y mergeada por persona.