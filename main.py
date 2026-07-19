"""main.py — Demos ejecutables (ejemplo de cómo usar la carga única de docs/faqs)."""

import json

import context
import logic
import state

# Empleados de prueba
with open("data/empleados_demo.json", encoding="utf-8") as f:
    EMPLEADOS = {e["id"]: e for e in json.load(f)}

# Carga ÚNICA de docs/faqs para toda la sesión de demos, evitando releer
# disco en cada llamada a procesar_chat()/procesar_checklist().
DOCS = context.cargar_documentos()
FAQS = context.cargar_faq()


def demo_1_chat():
    print("\n=== Demo 1: conversación (dev junior) ===")
    laura = EMPLEADOS["emp_01"]
    sesion = state.inicializar_estado(laura, dia=1)

    resultado = logic.procesar_chat(
        sesion,
        "¿A qué canales de Slack tengo que unirme?",
        docs=DOCS,
        faqs=FAQS,
    )
    print(resultado)


def demo_2_checklist():
    print("\n=== Demo 2: checklist día 1 ===")
    laura = EMPLEADOS["emp_01"]
    sesion = state.inicializar_estado(laura, dia=1)

    resultado = logic.procesar_checklist(sesion, docs=DOCS, faqs=FAQS)
    print(resultado)


def demo_3_comparativa_perfiles():
    print("\n=== Demo 3: mismo mensaje, comercial vs remoto UE ===")
    pregunta = "¿Cómo pido vacaciones?"

    for emp_id in ("emp_02", "emp_03"):
        empleado = EMPLEADOS[emp_id]
        sesion = state.inicializar_estado(empleado, dia=2)
        resultado = logic.procesar_chat(sesion, pregunta, docs=DOCS, faqs=FAQS)
        print(f"\n--- {empleado['nombre']} ({empleado['perfil']}) ---")
        print(resultado)


if __name__ == "__main__":
    demo_1_chat()
    demo_2_checklist()
    demo_3_comparativa_perfiles()