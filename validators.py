"""validators.py — Validación de entrada (Parte 3, aún sin implementar).
 
Qué hace este módulo (POR AHORA):
  - Stub temporal: ambas funciones siempre devuelven "válido" para no
    bloquear el desarrollo de la Parte 2. logic.py ya las llama en el orden
    correcto (fail-closed), así que cuando se implemente de verdad aquí, NO
    hace falta tocar logic.py.
 
TODO Fase 3 (Parte 3 — Robustez):
  - validar_entrada(pregunta):
      * longitud (config.MAX_INPUT_CHARS)
      * vacío / solo espacios
      * patrones de inyección (config.PATRONES_SOSPECHOSOS)
      * fuera de dominio (config.DOMINIO_KEYWORDS)
      * datos sensibles (salario, bonus, datos de terceros) -> derivar,
        no responder con cifras (ver POLITICAS.md)
  - validar_dia(dia):
      * ya valida rango básico 1-5; ampliar si hace falta con
        config.DIAS_ONBOARDING_VALIDOS
"""
 
 
def validar_entrada(pregunta: str) -> tuple[bool, str | None]:
    """TODO Fase 3. Por ahora siempre pasa (fail-open temporal)."""
    return True, None
 
 
def validar_dia(dia: int) -> tuple[bool, str | None]:
    """Valida que el día de onboarding esté en rango 1-5.
 
    TODO Fase 3: usar config.DIAS_ONBOARDING_VALIDOS si se añade lógica
    adicional (p. ej. mensajes de error más ricos, distintos por perfil).
    """
    if not isinstance(dia, int) or dia not in range(1, 6):
        return False, f"Día {dia} fuera de rango (debe ser 1-5)."
    return True, None
