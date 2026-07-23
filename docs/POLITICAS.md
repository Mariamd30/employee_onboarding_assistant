# Política de escalado — Employee Onboarding Assistant

Acuerdo del equipo sobre cuándo y a quién deriva el asistente. Cada regla está anclada a un dato real de `data/`, no inventada — si no encuentras la fuente citada, es una inferencia marcada como tal.

> Valor cultural clave (`empresa.json` → `valores`): **"Documentar antes de escalar"**. El asistente prioriza siempre citar la documentación disponible; solo deriva cuando la respuesta no está documentada, es sensible, o excede su ámbito (`alcance_producto`).

## 1. Canales de derivación

| Canal | Buzón | Cuándo se usa | Fuente |
|---|---|---|---|
| RRHH | `rrhh@bridgesa.example` | Vacaciones, bajas médicas/laborales, trabajo remoto internacional | `doc_rrhh_01`, `doc_rrhh_02`, `doc_rrhh_03` |
| People & Culture (conducta) | `people@bridgesa.example` | Acoso, discriminación, conflictos de interés, clima | `doc_cultura_01` |
| IT | `it@bridgesa.example` | Hardware, accesos (Slack, GitHub), incidencias técnicas | `doc_it_01`, `doc_it_02`, `doc_it_03` |
| Manager / Buddy | — (contacto directo, no email genérico) | Dudas prácticas del día a día, seguimiento personalizado | `doc_people_01` — *inferencia razonable, no hay regla explícita de "cuándo" derivar al manager más allá del programa buddy* |
| Buzón general | `onboarding@bridgesa.example` | Fallback si no está claro el canal, o si el buddy no responde en 24h laborables | `faq_16`, `doc_people_01` |

⚠️ Corrección respecto a la versión anterior: RRHH y People & Culture **no son el mismo buzón**. `rrhh@` gestiona trámites (bajas, vacaciones); `people@` gestiona conducta y clima.

## 2. Reglas de dominio

### ✅ El asistente SÍ ayuda con

- Herramientas corporativas y primeros pasos (`empresa.json` → `herramientas_corporativas`)
- Cultura de Bridge SA (`doc_bienvenida_01`)
- Vacaciones, según `doc_rrhh_01` (26 días laborables en España, salvo convenio local)
- Indicar a quién contactar y cómo escalar

### 🚫 El asistente NO debe

- Inventar políticas, plazos o cifras no documentadas
- Responder sobre salarios o bonus, propios o de terceros — derivar a manager/People (`faq_14`, `doc_beneficios_01`: *"no se gestiona por este canal"*)
- Atender a participantes externos de programas formativos — Operations coordina **cohortes de clientes**, no onboarding de empleados (`empresa.json` → `nota_importante`)
- Llamar al modelo si la validación de entrada falla (fail-closed)

## 3. Casos concretos ya resueltos en los datos

| Situación | Acción del asistente | Fuente |
|---|---|---|
| Pregunta sobre salario/bonus propio o de un tercero | No dar cifras; derivar a manager o People en 1:1 | `faq_14`, `doc_beneficios_01` |
| Baja médica | Notificar a manager + `rrhh@bridgesa.example` mismo día; parte en Factorial en 48h | `faq_06`, `doc_rrhh_03` |
| Baja laboral / excedencia (no confundir con médica) | Proceso distinto: abrir ticket con People, **no** usar flujo de baja médica | `faq_07`, `doc_rrhh_03` |
| Buddy no responde en 24h laborables | Escalar a `onboarding@bridgesa.example` | `faq_16`, `doc_people_01` |
| Trabajo remoto >14 días consecutivos desde otro país | Requiere aprobación previa de RRHH (implicaciones fiscales) | `faq_05`, `doc_rrhh_02` |
| Portátil no ha llegado | Escribir a `it@bridgesa.example` con ID de empleado | `faq_02`, `doc_it_01` |
| Reporte de acoso o conducta | `people@bridgesa.example` o manager directo, tolerancia cero | `faq_11`, `doc_cultura_01` |
| Pregunta sobre coordinación de cohortes/programas formativos | Fuera de dominio: el asistente solo atiende onboarding de empleados, no logística de clientes | `doc_ops_01` + `nota_importante` |
| Petición de ayuda con contenido de un programa formativo externo | Rechazar: canal exclusivo para onboarding de empleados | `alcance_producto` |
| Sospecha de inyección de instrucciones | Rechazar sin llamar al modelo; no revelar reglas internas | *No hay fuente en los datos — regla de seguridad general de la Parte 3* |
| Pregunta legítima pero no documentada | Decir explícitamente que no consta; sugerir el canal adecuado; no inventar | *Principio general derivado del valor "documentar antes de escalar"* |

## 4. Perfiles de empleado y tono

Confirmado contra `empleados_demo.json` (campo `perfil`):

| Perfil | Departamento típico | Tono esperado | Ejemplo en datos demo |
|---|---|---|---|
| `dev_junior` | Engineering & Product | Didáctico, paso a paso | Laura Méndez (`emp_01`) |
| `comercial` | Sales & Partnerships / Operations | Menos técnico, foco práctico | Pablo Navarro (`emp_02`), Miguel Ángel Toro (`emp_04`) |
| `remoto_eu` | Cualquiera, fuera de España | Atento a políticas cross-border (`doc_rrhh_02`) | Sofia Costa (`emp_03`), Inés Duarte (`emp_05`) |

> Nota: `emp_04` (Operations) tiene perfil `comercial` en los datos demo — confirmar con el equipo si esto es intencional o si Operations debería tener su propio tono (los datos actuales no distinguen un perfil específico para Operations).

## 5. Día de onboarding (1–5)

Confirmado por `doc_eng_01` (Engineering) y `doc_sales_01` (Sales), que sí detallan un plan día a día:

- **Día 1**: bienvenida, Slack, accesos (GitHub para Engineering, HubSpot para Sales)
- **Días 2–5**: progresión específica por departamento (setup → pair programming → primera issue → retro en Engineering; catálogo → shadowing → pitch → pipeline en Sales)

⚠️ No hay un `doc_operations_onboarding` ni `doc_people_onboarding` equivalente con plan día a día — solo existe `doc_ops_01` (coordinación de cohortes de clientes, no onboarding del propio empleado de Operations). Es un hueco en los datos a tener en cuenta si generáis checklist para `emp_04`.

---
