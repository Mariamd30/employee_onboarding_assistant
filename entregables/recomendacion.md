# Recomendación — Employee Onboarding Assistant

## Caso de uso

Asistente de onboarding para empleados nuevos de Bridge SA: responde
preguntas libres apoyándose en documentación interna (`onboarding_docs.json`
/ `faq_onboarding.json`) y genera una checklist diaria en JSON, ajustando
tono y contenido al perfil del empleado (dev_junior, comercial, remoto_eu)
y al día de onboarding (1–5). No inventa políticas ni cifras no
documentadas, no responde sobre salarios/datos de terceros, y no atiende a
participantes externos de programas formativos.

## Modelo recomendado para producción

**`gemini-2.5-flash`**, para el chat en tiempo real. En los 12 casos del
benchmark (24 llamadas, 0 errores), obtuvo exactamente la misma Fidelidad,
Relevancia, Tono y Seguridad que `gemini-3-flash-preview`, pero con una
latencia media de **2,5s** frente a **10,1s** del modelo preview — hasta
**11,9× más rápido** en el peor caso (`sales_primera_semana_dia1`: 2,2s vs
26,1s). Para un chat de onboarding en vivo, esa diferencia es decisiva.

## Modelo alternativo (opcional)

No se ha encontrado justificación para usar `gemini-3-flash-preview` ni
siquiera para la generación de checklists en batch: en el único caso de
tipo `checklist` del benchmark, ambos modelos generaron JSON válido con
calidad equivalente (6 tareas vs 5 tareas, ambas correctamente citadas con
`fuente_doc`), y la diferencia de latencia (5,7s vs 6,4s) es mucho menor
aquí que en chat — pero tampoco hay ninguna ventaja de `gemini-3` que la
justifique. Se recomienda usar `gemini-2.5-flash` también para checklists,
salvo que el equipo detecte casos futuros donde el modelo preview aporte
algo que el estable no dé.

## Trade-off principal

`gemini-2.5-flash` gana en **latencia y coste en tokens** (14.628 tokens
totales frente a 19.325 de `gemini-3-flash-preview` en las mismas 12
llamadas, un 32% menos) sin ceder nada medible en fidelidad a la
documentación ni en seguridad. `gemini-3-flash-preview` tiende a dar
respuestas algo más elaboradas (añade matices correctos, como
recomendaciones de privacidad o contactos adicionales), pero ese valor
añadido es marginal comparado con el coste de latencia — y en un producto
de chat en tiempo real, la latencia percibida importa más que un párrafo
extra de cortesía.

## ¿Qué pasaría si duplicáramos el tráfico?

Con `gemini-2.5-flash`, duplicar el tráfico implicaría pasar de ~14.628 a
~29.256 tokens por cada tanda equivalente de 12 conversaciones — un
crecimiento lineal en coste, previsible y manejable. Donde sí habría que
vigilar es en el **límite de peticiones por minuto del nivel gratuito**
(5 req/min por modelo): duplicar el tráfico real de producción superaría
esa cuota rápidamente y empezaríamos a ver los mismos errores 429 que
tuvimos en nuestra primera ejecución del benchmark. Antes de escalar,
habría que pasar a un nivel de pago con cuota más alta o implementar
reintentos con backoff. La latencia por petición no debería degradarse
mientras no se agote esa cuota.

## Riesgo o condición

No usaríamos `gemini-3-flash-preview` para producción salvo que, en una
futura ronda de benchmark (con más casos y ya con `validators.py`
implementado en Parte 3), demuestre una diferencia de fidelidad o
seguridad que compense su latencia — algo que en este benchmark no ha
ocurrido. Además, al ser un modelo "preview", su disponibilidad y precio
pueden cambiar sin aviso, lo que añade riesgo operativo frente a
`gemini-2.5-flash`, ya estable. Antes de desplegar cualquiera de los dos
en producción, conviene corregir el defecto de esquema detectado en el
checklist (`empleado_id` debe ser el id, no el nombre) y volver a probar
los casos límite una vez `validators.py` esté implementado de verdad.
