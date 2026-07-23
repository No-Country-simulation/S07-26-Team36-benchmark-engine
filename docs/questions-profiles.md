# Diseño de Preguntas y Perfiles Cualitativos

**Responsable:** Gio — Data Analyst

---

> Documentación pendiente. Gio completa este archivo con:
> - Las preguntas por dimensión (con opciones y pesos asignados)
> - El mapa de dimensión más débil → perfil de fricción
> - La descripción de qué hace distinto el cuartil superior por perfil

**General:** 
Para lograr que un operador de data center complete el diagnóstico en menos de 10 minutos, la clave es utilizar opciones de respuesta cerradas en una escala progresiva (de menor a mayor madurez / 1 a 4 puntos), orientadas a la acción y al impacto operativo directo.

**Propuesta de Ponderación sobre el 100% del Total**
La ponderación da mayor relevancia a la capacidad de visibilidad y acción rápida (donde ocurre el mayor desperdicio), equilibrando con el costo directo y las barreras estructurales.
| Dimensión | Preguntas | Ponderación | Justificación Estratégica |
| :--- | :---: | :---: | :--- |
| **Visibilidad cross-layer** | P1, P2, P3 | **25%** | Es la base técnica; sin visibilidad integrada entre capas físicas y de TI es imposible optimizar. |
| **Latencia de coordinación** | P6, P7, P8 | **25%** | Mide el tiempo de respuesta operativo frente a desacoples de capacidad/energía. |
| **Atribución de fricción** | P4, P5 | **20%** | Permite traducir el descalce físico-operativo en impacto financiero directo. |
| **Auto-cuantificación** | P9, P10 | **15%** | Refleja si el operador mide activamente la capacidad ociosa e ineficiencia. |
| **Bloqueantes** | P11, P12 | **15%** | Identifica el cuello de botella (humano, contractual o tecnológico) que impide avanzar. |

# Cuestionario de Evaluación: Benchmark de Madurez Operational en Data Centers

> **Instrucciones para el operador:**  
> Por favor, selecciona la opción (1, 2, 3 o 4) que mejor describa la realidad actual de su *facility*. El tiempo estimado de respuesta es de **menos de 10 minutos**.

---

## 1. Visibilidad Cross-Layer (Ponderación: 25%)

### P1. ¿Cómo se monitorea la relación entre el consumo térmico/eléctrico y la carga de procesamiento (*workloads*) de IA?
- [ ] **1.** Silos separados: El equipo de instalaciones (*facility*) y el de TI usan herramientas independientes sin cruce de datos.
- [ ] **2.** Reportes consolidados manualmente de forma periódica (semanal/mensual).
- [ ] **3.** Paneles unificados (*dashboards*) que muestran métricas de energía y carga en tiempo real.
- [ ] **4.** Integración mediante APIs automatizadas que alimentan modelos predictivos de capacidad/enfriamiento.

### P2. ¿Con qué nivel de granularidad física identifican el desperdicio de energía en el *facility*?
- [ ] **1.** Solo a nivel global del edificio/data center (PUE global).
- [ ] **2.** A nivel de sala (*Data Hall*) o fila de *racks*.
- [ ] **3.** A nivel de gabinete/*rack* individual.
- [ ] **4.** A nivel de servidor/chasis y tarjeta (GPU/acelerador) en tiempo real.

### P3. ¿Cómo reacciona la infraestructura física ante cambios abruptos de carga de trabajo de IA (*bursts*)?
- [ ] **1.** De forma totalmente reactiva o manual tras una alarma por sobretemperatura.
- [ ] **2.** Programada mediante reglas o calendarios predefinidos de carga.
- [ ] **3.** Con alertas tempranas automatizadas que notifican al operador antes de saturar la capacidad.
- [ ] **4.** Con orquestación dinámica (ajuste automático de enfriamiento y flujo eléctrico coordinado con la aplicación).

---

## 2. Atribución de Fricción (Ponderación: 20%)

### P4. ¿Cómo cuantifican el costo financiero de la capacidad encendida pero no utilizada (*stranded capacity*)?
- [ ] **1.** No se calcula ni se atribuye a ningún presupuesto o departamento.
- [ ] **2.** Se estiman promedios globales de pérdida en revisiones financieras anuales.
- [ ] **3.** Se calcula el costo por sala o proyecto basándose en consumo estimado.
- [ ] **4.** Se atribuye el costo exacto por capacidad ociosa en tiempo real por proyecto/*workload*.

### P5. ¿Cómo identifican la causa raíz cuando existe una ineficiencia entre la capa física y la capa de cómputo?
- [ ] **1.** Es difícil determinarla; suele haber debate o desacuerdo entre el equipo de *Facility* y el de TI.
- [ ] **2.** Se analiza tras incidentes mediante reuniones *post-mortem* manuales.
- [ ] **3.** Se cuenta con un flujo estandarizado que mapea la causa en cuestión de horas.
- [ ] **4.** Diagnóstico automatizado inmediato (*root-cause analysis*) guiado por software.

---

## 3. Latencia de Coordinación (Ponderación: 25%)

### P6. Cuando se aprovisiona un nuevo *cluster* o servidor de IA, ¿cuánto tiempo toma coordinar la capacidad térmica y eléctrica requerida?
- [ ] **1.** De varias semanas a meses (procesos burocráticos/manuales de aprobación).
- [ ] **2.** De varios días a una semana.
- [ ] **3.** Pocas horas (procesos parcialmente automatizados).
- [ ] **4.** Minutos u homologación instantánea a través de software de gestión unificada.

### P7. Ante una falla de enfriamiento parcial o pico térmico, ¿qué tan rápido responde el software de cómputo para reasignar cargas?
- [ ] **1.** No hay comunicación; el hardware se apaga por protección de temperatura (*thermal throttling/shutdown*).
- [ ] **2.** Intervención humana requerida para apagar o migrar servidores manualmente.
- [ ] **3.** Reglas automatizadas simples (migración programada si la temperatura supera un umbral).
- [ ] **4.** Rebalanceo autónomo de *workloads* en milisegundos sin interrupción del servicio.

### P8. ¿Con qué frecuencia se sincronizan las políticas de ahorro de energía con la programación de tareas de cómputo?
- [ ] **1.** Nunca / Políticas fijas estáticas todo el año.
- [ ] **2.** Ajustes estacionales o mensuales.
- [ ] **3.** Ajustes diarios según tarifas de energía o carga proyectada.
- [ ] **4.** Sincronización continua y en tiempo real (*Smart Grid / Dynamic Power Capping*).

---

## 4. Auto-Cuantificación (Ponderación: 15%)

### P9. ¿Cuentan con un indicador (KPI) específico para medir la "capacidad ociosa pagada y encendida"?
- [ ] **1.** No contamos con una métrica definida para esto.
- [ ] **2.** Usamos indicadores genéricos de la industria (como el PUE) que no capturan la ociosidad del servidor.
- [ ] **3.** Medimos el porcentaje de capacidad no aprovechada de forma periódica.
- [ ] **4.** Contamos con un índice interno en tiempo real que mide directamente la discrepancia entre energía consumida y rendimiento útil produciendo IA.

### P10. ¿Qué porcentaje aproximado de la capacidad de energía/enfriamiento del data center estiman que está encendida sin generar cómputo útil?
- [ ] **1.** Desconocido / No tenemos datos suficientes para estimarlo.
- [ ] **2.** Mayor al 30% de la capacidad total.
- [ ] **3.** Entre 10% y 30%.
- [ ] **4.** Menor al 10% (operación altamente optimizada).

---

## 5. Bloqueantes (Ponderación: 15%)

### P11. ¿Cuál es la principal barrera organizacional para coordinar las operaciones físicas con las de TI?
- [ ] **1.** Silos culturales/Estructura organizativa (*Facility* y TI reportan a áreas sin alineación).
- [ ] **2.** Contratos rígidos con proveedores o Acuerdos de Nivel de Servicio (SLA) inflexibles.
- [ ] **3.** Falta de herramientas tecnológicas que permitan la comunicación entre ambos mundos.
- [ ] **4.** No existen barreras significativas; las áreas trabajan con metas de eficiencia compartidas.

### P12. ¿Qué nivel de automatización tienen permitido aplicar sobre la infraestructura física desde las herramientas de software?
- [ ] **1.** Ninguno; la infraestructura física solo se manipula de forma manual e *in situ*.
- [ ] **2.** Solo monitoreo de lectura; la intervención requiere acción humana directa.
- [ ] **3.** Automatización de seguridad (apagados o mitigaciones de emergencia preprogramadas).
- [ ] **4.** Control dinámico bidireccional totalmente automatizado (*software-defined infrastructure*).

## Estructura de Salida para el Perfil de Fricción

Al procesar las respuestas, cada selección asigna de 1 a 4 puntos. El score ponderado identificará la madurez operacional global y la dimensión con la puntuación más baja revelará el **punto principal de fricción**:

$$\text{Puntaje Dimensión (\%)} = \left( \frac{\sum \text{Puntos obtenidos}}{\text{Puntos máximos posibles}} \right) \times \text{Ponderación Dimensión}$$

* **Ecosistema Reactivo (0% - 40%):** Desacople crítico. Se pierde un porcentaje significativo de la energía contratada.
* **Ecosistema Monitoreado (41% - 70%):** Visibilidad incipiente, pero con alta latencia de acción y silos organizacionales.
* **Ecosistema Optimizado (71% - 100%):** Operación coordinada en tiempo real; mínima fricción física-operativa.
