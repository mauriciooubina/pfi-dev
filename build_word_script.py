import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_documents():
    doc = docx.Document()
    
    # Set page margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Document Styles
    # Color Palette: Primary Navy #0F172A, Accent Blue #2563EB, Muted Gray #475569, Gold #D97706
    COLOR_NAVY = RGBColor(15, 23, 42)
    COLOR_BLUE = RGBColor(37, 99, 235)
    COLOR_GRAY = RGBColor(71, 85, 105)
    COLOR_GOLD = RGBColor(217, 119, 6)
    COLOR_GREEN = RGBColor(16, 185, 129)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_t = p_title.add_run("🎙️ Guion de Oratoria y Discurso para la Defensa Oral 50% (EP2)")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(22)
    run_t.font.bold = True
    run_t.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    run_sub = p_sub.add_run("Proyecto Final de Integración (PFI) — UADE | Tesista: Mauricio Nicolás Oubiña | Tribunal: Prof. Monzón & Prof. Pablo Hernández")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(11)
    run_sub.font.color.rgb = COLOR_BLUE
    p_sub.paragraph_format.space_after = Pt(16)

    # Callout Box: Instrucciones
    table_inst = doc.add_table(rows=1, cols=1)
    table_inst.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_inst = table_inst.cell(0, 0)
    set_cell_background(cell_inst, "F1F5F9")
    set_cell_margins(cell_inst, top=140, bottom=140, left=180, right=180)
    
    p_i = cell_inst.paragraphs[0]
    r_i = p_i.add_run("📌 Instrucciones Pedagógicas de Exposición:")
    r_i.font.bold = True
    r_i.font.size = Pt(11)
    r_i.font.color.rgb = COLOR_NAVY
    
    inst_points = [
        "Tiempo total objetivo: 12 minutos de discurso activo + 3 minutos de margen/reserva (Total 15m).",
        "Hablar a velocidad pausada pero firme (aprox. 130 a 140 palabras por minuto).",
        "El texto encerrado en comillas («...») representa las palabras exactas a pronunciar en voz alta en primera persona.",
        "Utilizar las notas del tutor para hacer énfasis visual o cambios de tono en puntos clave."
    ]
    for ip in inst_points:
        p_p = cell_inst.add_paragraph()
        r_p = p_p.add_run(f"• {ip}")
        r_p.font.size = Pt(10)
        r_p.font.color.rgb = COLOR_GRAY

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Slides Content List
    slides_script = [
        {
            "num": "Slide 1",
            "title": "Carátula e Introducción al Proyecto",
            "time": "00:00 - 01:00 (1 minuto)",
            "visual": "Isologotipo UADE, Título del PFI, Integrante (Mauricio Oubiña), Tribunal (Monzón/Hernández) y logos de Hellfish & Hooligans.",
            "speech": "«Buenas tardes, estimados profesores del tribunal, Profesor Monzón, Profesor Hernández. Mi nombre es Mauricio Oubiña y hoy tengo el agrado de presentarles el avance del 50% de mi Proyecto Final de Integración, titulado: 'Sistema de Predicción de Ausentismo y Métricas de Colas M/M/s para Comercios de Servicios con Agenda Híbrida'.\n\nEl propósito central de esta investigación es resolver una ineficiencia estructural que afecta a miles de Pequeñas y Medianas Empresas de servicios: la pérdida irreparable de capacidad operativa provocada por las inasistencias sin aviso de los clientes, comúnmente denominadas no-shows. A lo largo de esta exposición, abordaremos el diseño de ingeniería, la anonimización bajo Ley 25.326, la formalización estocástica mediante Teoría de Colas y realizaremos una demostración práctica de nuestro prototipo en software.»",
            "tip": "Mantené postura erguida, contacto visual directo con ambos evaluadores y voz pausada pero segura. Transmití profesionalismo desde la primera frase."
        },
        {
            "num": "Slide 2",
            "title": "El Problema Operativo: Pérdida Irrecuperable de Capacidad",
            "time": "01:00 - 02:15 (1.25 minutos)",
            "visual": "Diagrama de bloques horarios de 30 min. Bloque rojo resaltado: 'Silla Vacía = Costo Fijo Incurrido ($0 Ingreso)'. Gráfico de 12% a 22% de no-shows.",
            "speech": "«Para dimensionar el problema, debemos entender la naturaleza económica de un comercio de servicios por turnos: la capacidad productiva es estrictamente perecedera. Si un cliente reserva un turno a las 15:00 horas y no se presenta, esos 30 o 45 minutos del profesional representan una hora de trabajo perdida que jamás se podrá recuperar o inventariar.\n\nActualmente, los comercios adoptan dos soluciones rudimentarias: o cobran señas por adelantado a todos los usuarios —lo que genera fricción y causa la pérdida de clientes habituales— o realizan sobreturnos a ciegas —lo que colapsa la sala de espera y destruye la calidad de atención—. Nuestra propuesta busca romper este dilema mediante un enfoque analítico y proactivo.»",
            "tip": "Hacé énfasis verbal en la palabra 'perecedera'. El jurado académico valora la cita explícita de la teoría de operaciones de servicios."
        },
        {
            "num": "Slide 3",
            "title": "Relevamiento Cualitativo: Hellfish vs. Hooligans",
            "time": "02:15 - 03:30 (1.25 minutos)",
            "visual": "Tabla comparativa enfrentando Hellfish (Página Web propia intensiva + Espontáneos acotados, s=3) y Hooligans (Página Web propia + WhatsApp + Orden de llegada, s=2).",
            "speech": "«Como sustento empírico de nuestro diseño, realizamos entrevistas en profundidad con los dueños de dos comercios reales del sector: Facundo Alvarez de Hellfish Barbershop y Sebastián Fraga de Barbería Hooligans.\n\nEs importante remarcar que ambos comercios disponen de una plataforma web propia para la gestión de turnos, utilizada tanto por los clientes como por el personal para administrar la agenda diaria. La diferencia radica en la dinámica operativa: mientras que en Hellfish la gran mayoría de los usuarios agendan directamente por su sitio web —admitiendo clientes espontáneos de forma acotada cuando la disponibilidad lo permite—, en Hooligans existe una gestión híbrida activa al combinar su plataforma web propia con la recepción manual de reservas por WhatsApp y el ingreso por orden de llegada. Sin embargo, ambos coincidieron plenamente en un punto crítico: no desean penalizar a toda su clientela con señas obligatorias, sino contar con una herramienta inteligente que clasifique el riesgo de cada reserva para intervenir únicamente sobre las agendas críticas.»",
            "tip": "Señalá la tabla comparativa con la mano o puntero. Mencioná por sus nombres a los entrevistados para demostrar trabajo de campo real."
        },
        {
            "num": "Slide 4",
            "title": "Arquitectura en Tres Capas y Flujo ETL",
            "time": "03:30 - 04:45 (1.25 minutos)",
            "visual": "Diagrama C4 Contenedores y DFD ETL. Bloques: React 19 SPA <--> FastAPI REST <--> Python Engine ETL. Endpoints /api/calendar y /api/queues.",
            "speech": "«Para dar soporte a la solución, diseñamos una Arquitectura en Tres Capas con una estricta separación de responsabilidades:\n\nEn la Capa de Presentación implementamos una Single Page Application en React 19 con TypeScript, optimizada para ofrecer una experiencia fluida e interactiva. La Capa de Servicios está construida sobre FastAPI en Python, aprovechando su velocidad de ejecución y validación nativa de esquemas con Pydantic v2.\n\nFinalmente, la Capa Analítica contiene el motor en Python encargado de procesar los datos transaccionales, ejecutar las rutinas de limpieza, efectuar la anonimización criptográfica y calcular las métricas estocásticas del modelo de colas.»",
            "tip": "Mencioná expresamente las tecnologías (React 19, FastAPI, Pydantic v2) para reafirmar la solidez del stack elegido."
        },
        {
            "num": "Slide 5",
            "title": "Ingesta, Aislamiento de Bloques y Ley 25.326",
            "time": "04:45 - 05:45 (1 minuto)",
            "visual": "Ejemplo visual: 'Nombre + Salt Sucursal -> SHA-256 -> Hash 16-hex'. Regla de aislamiento de bloques phone == '0000000000' o 'ALMUERZO'.",
            "speech": "«Un pilar fundamental de nuestra ingeniería de datos es el estricto cumplimiento normativo de la Ley 25.326 de Protección de Datos Personales de la República Argentina.\n\nDurante el proceso ETL en etl_pipeline.py, aplicamos una rutina de anonimización criptográfica irreversible. Cada dato sensible, como el nombre o teléfono del cliente, es procesado mediante el algoritmo SHA-256 combinado con un Salt secreto exclusivo de cada comercio, truncando el digest a 16 caracteres. Esto nos permite mantener la trazabilidad del historial de comportamiento del usuario a lo largo del tiempo sin almacenar jamás información de filiación personal en nuestras bases analíticas.»",
            "tip": "Este punto es muy apreciado por el jurado. Remarcá la frase 'truncado a 16 caracteres hex' e 'irreversibilidad'."
        },
        {
            "num": "Slide 6",
            "title": "Formalización de la Variable Target y (5 Reglas)",
            "time": "05:45 - 07:00 (1.25 minutos)",
            "visual": "Tabla con las 5 Condiciones del Target. Destacar en verde y=0, en rojo y=1, y en naranja la EXCLUSIÓN de cancelaciones ≥ 2 horas.",
            "speech": "«Uno de los mayores aportes metodológicos del hito 50% es la definición rigurosa de la variable objetivo 'y'. En los sistemas reales, el ausentismo no se limita únicamente a que el cliente no aparezca; abarca situaciones operativas complejas.\n\nEstablecimos 5 condiciones lógicas: por un lado, categorizamos como asistencia (y=0) a los turnos pagados y ejecutados. Como no-show (y=1) clasificamos no solo la ausencia física sin pago, sino también las cancelaciones eliminadas por el local tras la inasistencia y aquellas canceladas por el cliente con menos de 2 horas de margen, ya que imposibilitan reasignar la silla.\n\nEs crucial destacar la Condición 5: las cancelaciones realizadas con más de 2 horas de anticipación son excluidas del target de ausentismo, puesto que permitieron al comercio volver a publicar y ocupar el turno, no constituyendo una pérdida irrecuperable.»",
            "tip": "Articulá bien la explicación de por qué la Condición 5 se EXCLUYE de la matriz de ML. Es una pregunta de examen clásica."
        },
        {
            "num": "Slide 7",
            "title": "Baseline Estocástico: Teoría de Colas M/M/s",
            "time": "07:00 - 08:30 (1.5 minutos)",
            "visual": "Fórmulas de M/M/s (ρ, P0, Lq, Wq). Tabla de métricas reales auditadas: Hellfish (λ=1.54, μ=1.64, s=3, ρ=31.3%, Wq=1.38m) y Hooligans (λ=0.96, μ=1.85, s=2, ρ=26.0%, Wq=2.36m).",
            "speech": "«Como baseline cuantitativo para evaluar la operación de los comercios, implementamos el modelo estocástico de Teoría de Colas M/M/s en estado estable, basándonos en la formulación de Hillier & Lieberman.\n\nAl analizar los datos transaccionales procesados de ambos locales en la ventana operativa de 10:00 a 20:00 horas, obtuvimos métricas contundentes:\n\nEn Hellfish, con 3 barberos activos, la tasa de llegada lambda es de 1.54 clientes por hora y la tasa de servicio mu es de 1.64 servicios por hora. Esto arroja un factor de ocupación rho del 31.3% y un tiempo promedio en cola Wq de tan solo 1.38 minutos. En Hooligans, con 2 barberos, la ocupación es del 26.0% con un Wq de 2.36 minutos. Ambos sistemas presentan estabilidad estocástica al ser rho menor a 1.»",
            "tip": "Mencioná con precisión los números auditados (31.3% de ocupación en Hellfish, 26.0% en Hooligans). Muestra dominio absoluto de los datos."
        },
        {
            "num": "Slide 8",
            "title": "Insuficiencia de M/M/s vs. Machine Learning",
            "time": "08:30 - 09:30 (1 minuto)",
            "visual": "Cuadro Comparativo: M/M/s (Supuesto Poisson homogéneo (1-p)λ) vs ML Supervisado (Probabilidad P(y=1|Xi) turno a turno).",
            "speech": "«Aquí llegamos a un punto neurálgico de la tesis: ¿Por qué la Teoría de Colas tradicional es insuficiente para resolver el ausentismo en comercios con agenda?\n\nEn la literatura clásica, el ausentismo se modela simplificadamente reduciendo la tasa de llegada a un flujo efectivo de (1-p)lambda. Sin embargo, este supuesto asume que todos los clientes son idénticos y que el ausentismo es una penalización homogénea y aleatoria. En la práctica, si un usuario falta a su turno reservado de las 16:00 horas, la silla queda vacía de forma forzada; el modelo estocástico no puede prevenir qué turno específico se perderá.\n\nEsta limitación estructural justifica plenamente el salto hacia la segunda etapa de nuestro proyecto en el Hito 75%: el desarrollo de clasificadores supervisados de Machine Learning que evalúen el vector de características de cada reserva individual.»",
            "tip": "Esta transición argumental demuestra madurez metodológica: explicás las virtudes de M/M/s pero fundamentás la necesidad de ML para el 75%."
        },
        {
            "num": "Slide 9",
            "title": "Live Demo Práctica (Paso a Paso de 5 Minutos)",
            "time": "09:30 - 12:30 (3 minutos en Slide + Demo)",
            "visual": "Navegador Web con 2 pestañas abiertas: Swagger UI (FastAPI) e Interfaz React 19.",
            "speech": "«A continuación, pasaremos a la demostración práctica en vivo de nuestro prototipo MVP funcional.\n\n[Paso 1 - Swagger]: Comenzamos en Swagger UI. Ejecutamos los endpoints /api/calendar y /api/queues para verificar que FastAPI retorna los datos de agenda y métricas de colas correctamente serializados.\n\n[Paso 2 - Timeline React]: Cambiamos a la aplicación React. Seleccionamos Hellfish Barbershop y recorremos la columna de la agenda. Notamos cómo cada turno exhibe su etiqueta de riesgo (Alto, Medio, Bajo).\n\n[Paso 3 - Alertas WhatsApp]: En la columna derecha de alertas, seleccionamos un turno de riesgo ALTO y presionamos 'Enviar WhatsApp'. El sistema simula la notificación y despliega el mensaje Toast de confirmación.\n\n[Paso 4 - Pestaña Colas]: Conmutamos a la pestaña de Métricas de Colas M/M/s. Al cambiar de Hellfish a Hooligans, las tarjetas de ocupación y tiempo de espera se recalculan de forma dinámica.\n\n[Paso 5 - Modo Fallback]: Finalmente, ante una eventual caída de backend, el frontend conmuta automáticamente al modo Fallback local, garantizando resiliencia sin interrumpir al usuario.»",
            "tip": "Mantené calma durante la demo. Si algo tarda en cargar o se desconecta, recordá que tenés el modo Fallback en React como resiliencia."
        },
        {
            "num": "Slide 10",
            "title": "Conclusiones Hito 50% y Roadmap Hacia EP3",
            "time": "12:30 - 13:30 (1 minuto)",
            "visual": "Línea de tiempo con checkmarks verdes en los logros del 50% y lista de tareas en desarrollo para 75% / 100%.",
            "speech": "«En síntesis, para esta entrega del 50% hemos alcanzado con éxito todos los objetivos fijados: consolidamos el relevamiento cualitativo en comercios reales, estructuramos un pipeline ETL robusto con anonimización legal bajo Ley 25.326, formalizamos la variable target y establecimos el baseline estocástico M/M/s sobre datos reales.\n\nDe cara a los próximos hitos, abordaremos el entrenamiento y tuneo de clasificadores XGBoost supervisados, la serialización del modelo inferencial y la migración a una infraestructura containerizada en PostgreSQL.\n\nQuedo a la entera disposición del tribunal para iniciar la demostración en vivo y responder a sus apreciables preguntas. Muchas gracias.»",
            "tip": "Cerrá con tono firme, agradeciendo al tribunal y abriendo la etapa de preguntas."
        }
    ]

    for slide in slides_script:
        # Heading 1
        h1 = doc.add_heading(level=1)
        r_h1 = h1.add_run(f"📌 {slide['num']}: {slide['title']}")
        r_h1.font.name = "Arial"
        r_h1.font.size = Pt(14)
        r_h1.font.bold = True
        r_h1.font.color.rgb = COLOR_NAVY
        h1.paragraph_format.space_before = Pt(14)
        h1.paragraph_format.space_after = Pt(4)

        # Meta table
        meta_table = doc.add_table(rows=2, cols=2)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Meta 1: Time
        cell_t = meta_table.cell(0, 0)
        set_cell_background(cell_t, "FEF3C7") # Light Amber
        set_cell_margins(cell_t, top=60, bottom=60, left=100, right=100)
        p_t = cell_t.paragraphs[0]
        r_t1 = p_t.add_run("⏱️ Tiempo Recomendado: ")
        r_t1.font.bold = True
        r_t1.font.size = Pt(10)
        r_t2 = p_t.add_run(slide['time'])
        r_t2.font.size = Pt(10)

        # Meta 2: Visuals
        cell_v = meta_table.cell(0, 1)
        set_cell_background(cell_v, "F1F5F9")
        set_cell_margins(cell_v, top=60, bottom=60, left=100, right=100)
        p_v = cell_v.paragraphs[0]
        r_v1 = p_v.add_run("🖼️ Qué Mostrar en Pantalla: ")
        r_v1.font.bold = True
        r_v1.font.size = Pt(10)
        r_v2 = p_v.add_run(slide['visual'])
        r_v2.font.size = Pt(10)

        # Speech Box
        cell_sp = meta_table.cell(1, 0)
        meta_table.cell(1, 0).merge(meta_table.cell(1, 1))
        set_cell_background(cell_sp, "FAFAFA")
        set_cell_margins(cell_sp, top=120, bottom=120, left=140, right=140)
        
        p_sp = cell_sp.paragraphs[0]
        r_sp1 = p_sp.add_run("🗣️ GUION VERBATIM (Qué decir en voz alta):\n")
        r_sp1.font.bold = True
        r_sp1.font.size = Pt(10)
        r_sp1.font.color.rgb = COLOR_BLUE
        
        r_sp2 = p_sp.add_run(slide['speech'])
        r_sp2.font.size = Pt(11)
        r_sp2.font.italic = True
        r_sp2.font.color.rgb = COLOR_NAVY

        # Tutor Tip
        p_tip = doc.add_paragraph()
        p_tip.paragraph_format.space_before = Pt(6)
        p_tip.paragraph_format.space_after = Pt(12)
        r_tp1 = p_tip.add_run("💡 Tip del Tutor: ")
        r_tp1.font.bold = True
        r_tp1.font.size = Pt(10)
        r_tp1.font.color.rgb = COLOR_GOLD
        
        r_tp2 = p_tip.add_run(slide['tip'])
        r_tp2.font.size = Pt(10)
        r_tp2.font.color.rgb = COLOR_GRAY

    # ==========================================
    # BACKUP SLIDES SECTION
    # ==========================================
    h_bk = doc.add_heading(level=1)
    r_hb = h_bk.add_run("🏛️ Diapositivas de Respaldo (Backup Slides para Q&A del Jurado)")
    r_hb.font.name = "Arial"
    r_hb.font.size = Pt(16)
    r_hb.font.bold = True
    r_hb.font.color.rgb = COLOR_NAVY
    h_bk.paragraph_format.space_before = Pt(20)

    backups = [
        {
            "num": "Backup Slide B1",
            "title": "Lógica Metodológica de las 5 Condiciones del Target y",
            "q": "¿Cómo definieron la variable objetivo y? ¿Por qué no consideraron ausentismo únicamente a los turnos no asistidos?",
            "speech": "«Estimado tribunal, clasificar el ausentismo mediante una regla simple de 'asistió / no asistió' genera un sesgo severo en comercios de servicios:\n1. Cancelaciones Tardías (< 2h): El impacto económico es idéntico a un no-show físico. El profesional queda ocioso y no hay tiempo suficiente para reasignar la silla en la web (y = 1).\n2. Eliminación por el Comercio: Ocurre cuando el cliente no viene y el encargado borra la cita manualmente (deleted_by != client), configurando un ausentismo real (y = 1).\n3. Exclusión de Cancelaciones Anticipadas (≥ 2h): Se retiran del target de ML porque el comercio reabrió ese bloque y recuperó el turno, no constituyendo una pérdida irrecuperable.»"
        },
        {
            "num": "Backup Slide B2",
            "title": "Justificación Teórica Avanzada: M/M/s vs. Machine Learning",
            "q": "¿Por qué afirman que la Teoría de Colas no alcanza? ¿No se podría ajustar un modelo M/M/s con ausentismo?",
            "speech": "«La Teoría de Colas clásica M/M/s es una herramienta estocástica brillante para dimensionar la capacidad agregada en estado estable, pero presenta tres limitaciones estructurales para agendas discretas:\n1. Supuesto de Homogeneidad: M/M/s asume que el ausentismo es una reducción homogénea (1-p)λ y que todos los clientes tienen la misma probabilidad p.\n2. Pérdida por Bloques Discretos: Un no-show provoca una pérdida irrecuperable de un bloque horario exacto (ej. 30 min), dejando al profesional ocioso de forma forzada.\n3. Complementariedad: M/M/s nos aporta el marco macro estocástico (ρ, Wq), mientras que requerimos clasificadores de ML supervisado (XGBoost) para computar la probabilidad individual P(y=1 | Xi) de cada reserva.»"
        },
        {
            "num": "Backup Slide B3",
            "title": "Cumplimiento de la Ley 25.326 y Criptografía Aplicada",
            "q": "¿Cómo garantizan que la anonimización cumple realmente con la Ley 25.326 y que no se puede revertir?",
            "speech": "«El cumplimiento de la Ley N° 25.326 se fundamenta en la disociación e irreversibilidad de los datos personales:\n1. Hash SHA-256 con Salt Exclusivo: Cada comercio posee una clave salt secreta exclusiva. Se evita el uso de hashes simples expuestos a tablas Rainbow.\n2. Truncamiento a 16 Hexadecimales (64 bits): Al truncar el digest a 16 caracteres hex, se destruye la entropía necesaria para impedir cualquier intento de ingeniería inversa, manteniendo colisiones nulas a escala local.\n3. Purga en Memoria: Nombres y teléfonos crudos se eliminan de la memoria en Pandas antes de exportar la matriz procesada analítica.»"
        }
    ]

    for b in backups:
        h2 = doc.add_heading(level=2)
        r_h2 = h2.add_run(f"📌 {b['num']}: {b['title']}")
        r_h2.font.name = "Arial"
        r_h2.font.size = Pt(13)
        r_h2.font.bold = True
        r_h2.font.color.rgb = COLOR_BLUE
        h2.paragraph_format.space_before = Pt(10)

        p_q = doc.add_paragraph()
        r_q1 = p_q.add_run("❓ Pregunta Probable del Jurado: ")
        r_q1.font.bold = True
        r_q1.font.size = Pt(10)
        r_q1.font.color.rgb = COLOR_GOLD
        r_q2 = p_q.add_run(b['q'])
        r_q2.font.size = Pt(10)
        r_q2.font.italic = True

        tb_b = doc.add_table(rows=1, cols=1)
        tb_b.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell_b = tb_b.cell(0, 0)
        set_cell_background(cell_b, "F8FAFC")
        set_cell_margins(cell_b, top=100, bottom=100, left=140, right=140)
        
        p_bs = cell_b.paragraphs[0]
        r_bs1 = p_bs.add_run("🗣️ ARGUMENTACIÓN DEFENSIVA (Qué responder en voz alta):\n")
        r_bs1.font.bold = True
        r_bs1.font.size = Pt(10)
        r_bs1.font.color.rgb = COLOR_NAVY
        
        r_bs2 = p_bs.add_run(b['speech'])
        r_bs2.font.size = Pt(10.5)
        r_bs2.font.italic = True
        r_bs2.font.color.rgb = COLOR_NAVY

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Save Word Document (.docx)
    out_docx_pfi = "/Users/mauriciooubina/Desktop/Workspace/pfi/GUION_ORATORIA_DEFENSA_50.docx"
    out_docx_latex = "/Users/mauriciooubina/Downloads/UADE_PFI_Template-develop/GUION_ORATORIA_DEFENSA_50.docx"
    
    doc.save(out_docx_pfi)
    doc.save(out_docx_latex)

    # Save Markdown Document (.md)
    md_content = "# 🎙️ Guion de Oratoria y Discurso para la Defensa Oral 50% (EP2)\n\n"
    md_content += "> **Proyecto:** Sistema de Predicción de Ausentismo y Métricas de Colas $M/M/s$ para Comercios de Servicios con Agenda Híbrida  \n"
    md_content += "> **Tesista:** Mauricio Nicolás Oubiña | **Tribunal Evaluador:** Prof. Monzón & Prof. Pablo Hernández  \n\n"
    
    for slide in slides_script:
        md_content += f"--- \n\n## 📌 {slide['num']}: {slide['title']}\n"
        md_content += f"- **⏱️ Tiempo Recomendado:** `{slide['time']}`\n"
        md_content += f"- **🖼️ Qué Mostrar en Pantalla:** {slide['visual']}\n\n"
        md_content += "### 🗣️ GUION VERBATIM (Qué decir en voz alta):\n"
        md_content += f"> {slide['speech'].replace('\n', '\n> ')}\n\n"
        md_content += f"💡 **Tip del Tutor:** {slide['tip']}\n\n"

    md_content += "---\n\n# 🏛️ Diapositivas de Respaldo (Backup Slides para Q&A)\n\n"
    for b in backups:
        md_content += f"## 📌 {b['num']}: {b['title']}\n"
        md_content += f"- **❓ Pregunta Probable del Jurado:** *{b['q']}*\n\n"
        md_content += "### 🗣️ ARGUMENTACIÓN DEFENSIVA (Qué responder):\n"
        md_content += f"> {b['speech'].replace('\n', '\n> ')}\n\n"

    out_md_pfi = "/Users/mauriciooubina/Desktop/Workspace/pfi/GUION_ORATORIA_DEFENSA_50.md"
    out_md_latex = "/Users/mauriciooubina/Downloads/UADE_PFI_Template-develop/GUION_ORATORIA_DEFENSA_50.md"

    with open(out_md_pfi, 'w', encoding='utf-8') as f:
        f.write(md_content)
    with open(out_md_latex, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"Successfully generated script files:\n - {out_docx_pfi}\n - {out_docx_latex}\n - {out_md_pfi}\n - {out_md_latex}")

if __name__ == "__main__":
    create_documents()
