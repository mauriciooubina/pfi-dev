import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

def create_deck():
    prs = Presentation()
    # Set 16:9 widescreen dimensions (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6] # Blank slide layout

    # Color Palette Definitions
    COLOR_BG = RGBColor(15, 23, 42)         # Slate 900 (Dark Navy)
    COLOR_CARD = RGBColor(30, 41, 59)       # Slate 800 (Darker Slate)
    COLOR_CARD_BORDER = RGBColor(51, 65, 85)# Slate 700
    COLOR_ACCENT = RGBColor(37, 99, 235)    # Royal Blue
    COLOR_ACCENT_LIGHT = RGBColor(96, 165, 250) # Light Blue
    COLOR_TEXT_MAIN = RGBColor(248, 250, 252) # Off White
    COLOR_TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400
    COLOR_GOLD = RGBColor(245, 158, 11)     # Amber 500
    COLOR_GREEN = RGBColor(16, 185, 129)    # Emerald 500
    COLOR_RED = RGBColor(239, 68, 68)       # Red 500

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()

    def add_header(slide, badge_text, title_text):
        add_background(slide)
        
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.5), Inches(3.2), Inches(0.35))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_ACCENT
        badge.line.fill.background()
        tf = badge.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = badge_text.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.alignment = PP_ALIGN.CENTER
        
        # Title
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.9), Inches(11.7), Inches(0.6))
        tf_t = txBox.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_MAIN

    def add_speaker_notes(slide, text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = text

    # ==========================================
    # SLIDE 1: Carátula
    # ==========================================
    slide1 = prs.slides.add_slide(blank_slide_layout)
    add_background(slide1)
    
    # Large Decorative Banner Shape
    banner = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.3), Inches(7.5))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_ACCENT
    banner.line.fill.background()

    # Title box
    tbox = slide1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(2.2))
    tf = tbox.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "Sistema de Predicción de Ausentismo y Métricas de Colas M/M/s"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEXT_MAIN
    
    p2 = tf.add_paragraph()
    p2.text = "Para Comercios de Servicios con Agenda Híbrida — Defensa Oral Hito 50% (EP2)"
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_ACCENT_LIGHT
    p2.space_before = Pt(12)

    # Info Card Box
    card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.8), Inches(11.3), Inches(2.8))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = COLOR_CARD_BORDER

    tf_c = card.text_frame
    tf_c.word_wrap = True
    
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "🎓 Proyecto Final de Integración (PFI) — UADE 2026"
    p_c1.font.size = Pt(16)
    p_c1.font.bold = True
    p_c1.font.color.rgb = COLOR_GOLD

    items = [
        "Autor / Tesista: Mauricio Nicolás Oubiña",
        "Tribunal Evaluador: Prof. Monzón & Prof. Pablo Hernández",
        "Comercios Analizados: Hellfish Barbershop & Barbería Hooligans",
        "Alcance EP2 (50%): Relevamiento, Ley 25.326, Baseline M/M/s, Reglas Target y, MVP Prototipo React+FastAPI"
    ]
    for it in items:
        p_item = tf_c.add_paragraph()
        p_item.text = f"• {it}"
        p_item.font.size = Pt(14)
        p_item.font.color.rgb = COLOR_TEXT_MAIN
        p_item.space_before = Pt(6)

    add_speaker_notes(slide1, """Buenas tardes, estimados profesores del tribunal, Profesor Monzón, Profesor Hernández. Mi nombre es Mauricio Oubiña y hoy tengo el agrado de presentarles el avance del 50% de mi Proyecto Final de Integración, titulado: 'Sistema de Predicción de Ausentismo y Métricas de Colas M/M/s para Comercios de Servicios con Agenda Híbrida'.

El propósito central de esta investigación es resolver una ineficiencia estructural que afecta a miles de Pymes de servicios: la pérdida irreparable de capacidad operativa provocada por las inasistencias sin aviso (no-shows). A lo largo de esta exposición, abordaremos el diseño de ingeniería, la anonimización bajo Ley 25.326, la formalización estocástica mediante Teoría de Colas y realizaremos una demostración práctica de nuestro prototipo en software.""")

    # ==========================================
    # SLIDE 2: El Problema Operativo y Económico
    # ==========================================
    slide2 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide2, "IMPACTO OPERATIVO Y ECONÓMICO", "El Problema: Pérdida Irrecuperable de Capacidad en Agendas Híbridas")

    # 3 Cards Layout
    card_width = Inches(3.64)
    card_height = Inches(5.0)
    card_top = Inches(1.8)

    # Card 1: Naturaleza Perecedera
    c1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), card_top, card_width, card_height)
    c1.fill.solid()
    c1.fill.fore_color.rgb = COLOR_CARD
    c1.line.color.rgb = COLOR_RED
    tf = c1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🔴 Capacidad Perecedera"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_RED
    bullets1 = [
        "El tiempo de un profesional no se puede almacenar ni inventariar.",
        "Un turno de 30 min sin cliente equivale a $0 ingreso con costo fijo 100% incurrido.",
        "Perishability of Services (Stevenson, 2021)."
    ]
    for b in bullets1:
        p_b = tf.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    # Card 2: Métrica Sectorial
    c2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.84), card_top, card_width, card_height)
    c2.fill.solid()
    c2.fill.fore_color.rgb = COLOR_CARD
    c2.line.color.rgb = COLOR_GOLD
    tf = c2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚠️ 12% a 22% Ausentismo"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_GOLD
    bullets2 = [
        "Alta tasa de no-shows en comercios de estética y cuidado personal.",
        "Agendas híbridas (WhatsApp + Web) generan fricción y olvidos.",
        "Reservas inmediatas (1 a 3 días) concentran el mayor riesgo de inasistencia."
    ]
    for b in bullets2:
        p_b = tf.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    # Card 3: Soluciones Rudimentarias
    c3 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.88), card_top, card_width, card_height)
    c3.fill.solid()
    c3.fill.fore_color.rgb = COLOR_CARD
    c3.line.color.rgb = COLOR_ACCENT_LIGHT
    tf = c3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "⚡ Dilema del Mercado"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_LIGHT
    bullets3 = [
        "Seña Obligatoria Masiva: Provoca fricción y fuga de clientes habituales.",
        "Sobreturnos a Ciega: Generan demoras, colapso de sala y destruyen la calidad.",
        "Solución Propuesta: Mitigación analítica proactiva solo sobre reservas de ALTO riesgo."
    ]
    for b in bullets3:
        p_b = tf.add_paragraph()
        p_b.text = f"• {b}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    add_speaker_notes(slide2, """Para dimensionar el problema, debemos entender la naturaleza económica de un comercio de servicios por turnos: la capacidad productiva es estrictamente perecedera. Si un cliente reserva un turno a las 15:00 horas y no se presenta, esos 30 o 45 minutos del profesional representan una hora de trabajo perdida que jamás se podrá recuperar o inventariar.

Actualmente, los comercios adoptan dos soluciones rudimentarias: o cobran señas por adelantado a todos los usuarios —lo que genera fricción y causa la pérdida de clientes habituales— o realizan sobreturnos a ciegas —lo que colapsa la sala de espera y destruye la calidad de atención—. Nuestra propuesta busca romper este dilema mediante un enfoque analítico y proactivo.""")

    # ==========================================
    # SLIDE 3: Relevamiento Cualitativo
    # ==========================================
    slide3 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide3, "INVESTIGACIÓN EN CAMPO", "Estudio Comparativo: Hellfish Barbershop vs. Barbería Hooligans")

    # Table creation
    x, y, cx, cy = Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8)
    shape = slide3.shapes.add_table(5, 3, x, y, cx, cy)
    table = shape.table
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(4.25)
    table.columns[2].width = Inches(4.25)

    headers = ["Variable de Estudio", "Hellfish Barbershop (Facundo Alvarez)", "Barbería Hooligans (Sebastián Fraga)"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_ACCENT
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = COLOR_TEXT_MAIN

    rows_data = [
        ("Plataforma de Agendamiento", "Página Web propia (Uso intensivo + Espontáneos acotados)", "Página Web propia (Modelo híbrido con WhatsApp y Orden de llegada)"),
        ("Política de Sobreturnos", "Rechazada (Protege calidad y puntualidad)", "Acotada (Aplicada solo en clientes impuntuales)"),
        ("Cobro de Seña Previa", "Descartada masivamente (Evita fricción)", "Cautela por temor a migración a competidores"),
        ("Servidores Activos en Turno", "s = 3 barberos activos", "s = 2 barberos activos")
    ]
    for row_idx, row in enumerate(rows_data, start=1):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD if row_idx % 2 == 1 else COLOR_CARD_BORDER
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_TEXT_MAIN

    add_speaker_notes(slide3, """Como sustento empírico de nuestro diseño, realizamos entrevistas en profundidad con los dueños de dos comercios reales del sector: Facundo Alvarez de Hellfish y Sebastián Fraga de Hooligans.

El relevamiento reveló una marcada diferencia en la madurez digital: Hellfish opera con una plataforma web propia donde el cliente agenda de forma autónoma, mientras que Hooligans utiliza un modelo híbrido basado en WhatsApp y atención presencial. Sin embargo, ambos coincidieron plenamente en un punto crítico: no desean penalizar a toda su clientela con señas obligatorias, sino contar con una herramienta inteligente que clasifique el riesgo de cada reserva para intervenir únicamente sobre las agendas críticas.""")

    # ==========================================
    # SLIDE 4: Arquitectura del Sistema
    # ==========================================
    slide4 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide4, "DISEÑO DE INGENIERÍA", "Arquitectura en Tres Capas y Flujo ETL Analítico")

    # 3 Layers Horizontal Boxes
    box_top = Inches(1.8)
    box_h = Inches(4.8)
    box_w = Inches(3.64)

    # Layer 1
    l1 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), box_top, box_w, box_h)
    l1.fill.solid()
    l1.fill.fore_color.rgb = COLOR_CARD
    l1.line.color.rgb = COLOR_ACCENT
    tf = l1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Capa de Presentación"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_ACCENT_LIGHT
    items1 = [
        "React 19 + TypeScript + Vite",
        "Vanilla CSS (Design Tokens)",
        "Dashboard interactivo 2 pestañas (Agenda & Colas M/M/s)",
        "Modo Fallback Resiliente ante caídas de backend"
    ]
    for it in items1:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Layer 2
    l2 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.84), box_top, box_w, box_h)
    l2.fill.solid()
    l2.fill.fore_color.rgb = COLOR_CARD
    l2.line.color.rgb = COLOR_GREEN
    tf = l2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Capa de Servicios"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_GREEN
    items2 = [
        "FastAPI (Python 3.11) + Uvicorn",
        "Esquemas Pydantic v2 DTOs",
        "CORS Middleware configurado",
        "Endpoints REST auditados:",
        "  └ GET /api/calendar",
        "  └ GET /api/queues"
    ]
    for it in items2:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Layer 3
    l3 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.88), box_top, box_w, box_h)
    l3.fill.solid()
    l3.fill.fore_color.rgb = COLOR_CARD
    l3.line.color.rgb = COLOR_GOLD
    tf = l3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Capa Analítica y ETL"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_GOLD
    items3 = [
        "Engine Python (Pandas / NumPy)",
        "Pipeline ETL (etl_pipeline.py)",
        "Anonimización SHA-256 (utils.py)",
        "Cálculo M/M/s (queuing_theory.py)",
        "Persistencia en Matrices CSV/JSON"
    ]
    for it in items3:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    add_speaker_notes(slide4, """Para dar soporte a la solución, diseñamos una Arquitectura en Tres Capas con una estricta separación de responsabilidades:

En la Capa de Presentación implementamos una Single Page Application en React 19 con TypeScript, optimizada para ofrecer una experiencia fluida e interactiva. La Capa de Servicios está construida sobre FastAPI en Python, aprovechando su velocidad de ejecución y validación nativa de esquemas con Pydantic v2.

Finalmente, la Capa Analítica contiene el motor en Python encargado de procesar los datos transaccionales, ejecutar las rutinas de limpieza, efectuar la anonimización criptográfica y calcular las métricas estocásticas del modelo de colas.""")

    # ==========================================
    # SLIDE 5: Ingesta, Aislamiento y Ley 25.326
    # ==========================================
    slide5 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide5, "CUMPLIMIENTO NORMATIVO Y ETL", "Ingesta de Datos, Aislamiento de Bloques y Anonimización (Ley 25.326)")

    # 2 Large Cards
    w_c = Inches(5.6)
    h_c = Inches(4.8)
    top_c = Inches(1.8)

    # Box 1: Aislamiento Bloques
    b1 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_c, w_c, h_c)
    b1.fill.solid()
    b1.fill.fore_color.rgb = COLOR_CARD
    b1.line.color.rgb = COLOR_GOLD
    tf = b1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🔒 Aislamiento de Bloques Operativos"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_GOLD
    it1 = [
        "Filtro Core en etl_pipeline.py:",
        "Identifica registros de control donde phone == '0000000000' o client contiene ['ALMUERZO', 'HORARIO', 'BLOQUEO'].",
        "Desacopla turnos técnicos de la agenda comercial real.",
        "Guarda bloqueos aislados en consolidated_blocks.csv para cálculo de ociosidad analítica posterior."
    ]
    for it in it1:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(13)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Box 2: Anonimización Criptográfica
    b2 = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), top_c, w_c, h_c)
    b2.fill.solid()
    b2.fill.fore_color.rgb = COLOR_CARD
    b2.line.color.rgb = COLOR_GREEN
    tf = b2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🛡️ Criptografía SHA-256 + Salt (Ley 25.326)"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_GREEN
    it2 = [
        "Ley N° 25.326 de Protección de Datos Personales (Argentina).",
        "Algoritmo SHA-256 + Salt único por sucursal.",
        "Digest truncado a 16 caracteres hexadecimales (a3f89e11c4b209d7).",
        "Eliminación estricta de columnas client y phone antes del export analítico.",
        "Garantiza trazabilidad de recurrencia sin almacenar filiación personal."
    ]
    for it in it2:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(13)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    add_speaker_notes(slide5, """Un pilar fundamental de nuestra ingeniería de datos es el estricto cumplimiento normativo de la Ley 25.326 de Protección de Datos Personales de la República Argentina.

Durante el proceso ETL en etl_pipeline.py, aplicamos una rutina de anonimización criptográfica irreversible. Cada dato sensible, como el nombre o teléfono del cliente, es procesado mediante el algoritmo SHA-256 combinado con un Salt secreto exclusivo de cada comercio, truncando el digest a 16 caracteres. Esto nos permite mantener la trazabilidad del historial de comportamiento del usuario a lo largo del tiempo sin almacenar jamás información de filiación personal en nuestras bases analíticas.""")

    # ==========================================
    # SLIDE 6: Target y (5 Reglas)
    # ==========================================
    slide6 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide6, "MODELADO DE DATOS", "Formalización de la Variable Objetivo (y ∈ {0, 1}) y Reglas de Etiquetado")

    # Table layout of 5 conditions
    x, y, cx, cy = Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8)
    shape = slide6.shapes.add_table(6, 4, x, y, cx, cy)
    table = shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.2)
    table.columns[2].width = Inches(4.5)
    table.columns[3].width = Inches(2.8)

    headers = ["Condición Lógica", "Etiqueta Target", "Regla Transaccional Auditada", "Resultado Operativo"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_ACCENT
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT_MAIN

    rows_data = [
        ("Condición 1", "y = 0 (Asistencia)", "deleted_at IS NULL y paid == True", "Turno completado y cobrado"),
        ("Condición 2", "y = 1 (No-Show Absoluto)", "deleted_at IS NULL y paid == False", "Cliente no vino sin aviso"),
        ("Condición 3", "y = 1 (Proxy Eliminación)", "deleted_at IS NOT NULL y deleted_by != client", "Eliminado por local tras ausentarse"),
        ("Condición 4", "y = 1 (Proxy Cancelación)", "deleted_at IS NOT NULL, deleted_by == client, Δt < 2h", "Canceló con menos de 2h de antelación"),
        ("Condición 5", "EXCLUSIÓN ML", "deleted_at IS NOT NULL, deleted_by == client, Δt ≥ 2h", "Canceló a tiempo (agenda reasignable)")
    ]
    for row_idx, row in enumerate(rows_data, start=1):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            bg_color = COLOR_CARD if row_idx < 5 else RGBColor(45, 30, 20)
            if col_idx == 1:
                if "y = 0" in val:
                    bg_color = RGBColor(16, 85, 55)
                elif "y = 1" in val:
                    bg_color = RGBColor(95, 30, 30)
                elif "EXCLUSIÓN" in val:
                    bg_color = RGBColor(120, 75, 20)
            cell.fill.fore_color.rgb = bg_color
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.font.color.rgb = COLOR_TEXT_MAIN

    add_speaker_notes(slide6, """Uno de los mayores aportes metodológicos del hito 50% es la definición rigurosa de la variable objetivo 'y'. En los sistemas reales, el ausentismo no se limita únicamente a que el cliente no aparezca; abarca situaciones operativas complejas.

Establecimos 5 condiciones lógicas: por un lado, categorizamos como asistencia (y=0) a los turnos pagados y ejecutados. Como no-show (y=1) clasificamos no solo la ausencia física sin pago, sino también las cancelaciones eliminadas por el local tras la inasistencia y aquellas canceladas por el cliente con menos de 2 horas de margen, ya que imposibilitan reasignar la silla.

Es crucial destacar la Condición 5: las cancelaciones realizadas con más de 2 horas de anticipación son excluidas del target de ausentismo, puesto que permitieron al comercio volver a publicar y ocupar el turno, no constituyendo una pérdida irrecuperable.""")

    # ==========================================
    # SLIDE 7: Baseline M/M/s
    # ==========================================
    slide7 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide7, "ANÁLISIS ESTOCÁSTICO QUANT", "Baseline Cuantitativo: Modelo de Teoría de Colas M/M/s")

    # Table of audited results
    x, y, cx, cy = Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8)
    shape = slide7.shapes.add_table(8, 3, x, y, cx, cy)
    table = shape.table
    table.columns[0].width = Inches(4.5)
    table.columns[1].width = Inches(3.6)
    table.columns[2].width = Inches(3.6)

    headers = ["Métrica Estocástica / Parámetro M/M/s", "Hellfish Barbershop (Auditado)", "Barbería Hooligans (Auditado)"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_ACCENT
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_TEXT_MAIN

    rows_data = [
        ("Servidores Activos (s)", "s = 3 barberos", "s = 2 barberos"),
        ("Tasa de Llegada en Ventana Operativa (λ)", "1.5372 clientes / hora", "0.9605 clientes / hora"),
        ("Tasa de Servicio por Profesional (μ)", "1.6369 servicios / hora", "1.8458 servicios / hora"),
        ("Factor de Ocupación del Sistema (ρ)", "31.30% (0.3130)", "26.02% (0.2602)"),
        ("Probabilidad Sistema Desocupado (P0)", "38.75% (0.3875)", "58.71% (0.5871)"),
        ("Clientes Promedio en Cola (Lq)", "0.0355 clientes", "0.0378 clientes"),
        ("Tiempo Medio de Espera en Cola (Wq)", "1.38 minutos", "2.36 minutos")
    ]
    for row_idx, row in enumerate(rows_data, start=1):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_CARD if row_idx % 2 == 1 else COLOR_CARD_BORDER
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.font.color.rgb = COLOR_TEXT_MAIN

    add_speaker_notes(slide7, """Como baseline cuantitativo para evaluar la operación de los comercios, implementamos el modelo estocástico de Teoría de Colas M/M/s en estado estable, basándonos en la formulación de Hillier & Lieberman.

Al analizar los datos transaccionales procesados de ambos locales en la ventana operativa de 10:00 a 20:00 horas, obtuvimos métricas contundentes:

En Hellfish, con 3 barberos activos, la tasa de llegada lambda es de 1.54 clientes por hora y la tasa de servicio mu es de 1.64 servicios por hora. Esto arroja un factor de ocupación rho del 31.3% y un tiempo promedio en cola Wq de tan solo 1.38 minutos. En Hooligans, con 2 barberos, la ocupación es del 26.0% con un Wq de 2.36 minutos. Ambos sistemas presentan estabilidad estocástica al ser rho menor a 1.""")

    # ==========================================
    # SLIDE 8: M/M/s vs. Machine Learning
    # ==========================================
    slide8 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide8, "BRECHA METODOLÓGICA", "Insuficiencia Metodológica de M/M/s y Justificación de Machine Learning")

    # 2 Comparison Columns
    w_col = Inches(5.6)
    h_col = Inches(4.8)
    top_col = Inches(1.8)

    # Box 1: M/M/s Limits
    b1 = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_col, w_col, h_col)
    b1.fill.solid()
    b1.fill.fore_color.rgb = COLOR_CARD
    b1.line.color.rgb = COLOR_RED
    tf = b1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "❌ Limitaciones Estructurales de M/M/s"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_RED
    it1 = [
        "Supuesto de Homogeneidad: Trata el ausentismo como una reducción fija (1-p)λ en la llegada.",
        "Sin Historial Individual: No distingue entre un cliente recurrente puntual y uno con faltas previas.",
        "Agendas por Bloques Discretos: El no-show vacía un bloque exacto de 30 min, no reduce suavemente la carga.",
        "M/M/s calcula la utilización global (ρ), pero no previene QUÉ turno específico se perderá."
    ]
    for it in it1:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(13)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Box 2: ML Justification
    b2 = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), top_col, w_col, h_col)
    b2.fill.solid()
    b2.fill.fore_color.rgb = COLOR_CARD
    b2.line.color.rgb = COLOR_GREEN
    tf = b2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "✅ Solución Mediante ML Supervisado (75%)"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_GREEN
    it2 = [
        "Predicción Individualizada: Evalúa la probabilidad condicional P(y=1 | X_i) para cada reserva.",
        "Matriz de Características: Incorpora lead_time, horario, día de semana, canal de reserva e historial.",
        "Clasificadores Supervisados: XGBoost / Random Forest (Fase 75% / EP3).",
        "Permite mitigar proactivamente solo sobre las reservas de riesgo ALTO sin penalizar al resto."
    ]
    for it in it2:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(13)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    add_speaker_notes(slide8, """Aquí llegamos a un punto neurálgico de la tesis: ¿Por qué la Teoría de Colas tradicional es insuficiente para resolver el ausentismo en comercios con agenda?

En la literatura clásica, el ausentismo se modela simplificadamente reduciendo la tasa de llegada a un flujo efectivo de (1-p)lambda. Sin embargo, este supuesto asume que todos los clientes son idénticos y que el ausentismo es una penalización homogénea y aleatoria. En la práctica, si un usuario falta a su turno reservado de las 16:00 horas, la silla queda vacía de forma forzada; el modelo estocástico no puede prevenir qué turno específico se perderá.

Esta limitación estructural justifica plenamente el salto hacia la segunda etapa de nuestro proyecto en el Hito 75%: el desarrollo de clasificadores supervisados de Machine Learning que evalúen el vector de características de cada reserva individual.""")

    # ==========================================
    # SLIDE 9: Live Demo MVP
    # ==========================================
    slide9 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide9, "DEMOSTRACIÓN EN VIVO (MVP)", "Demostración Práctica del Prototipo Funcional (React 19 + FastAPI)")

    # 3 Steps Cards
    card_w = Inches(3.64)
    card_h = Inches(4.8)
    card_t = Inches(1.8)

    # Step 1
    c1 = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), card_t, card_w, card_h)
    c1.fill.solid()
    c1.fill.fore_color.rgb = COLOR_CARD
    c1.line.color.rgb = COLOR_ACCENT_LIGHT
    tf = c1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Capa API Swagger"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_ACCENT_LIGHT
    it1 = [
        "FastAPI OpenAPI Docs (localhost:8000/docs).",
        "Endpoint GET /api/calendar.",
        "Endpoint GET /api/queues.",
        "Respuesta JSON validada por Pydantic v2."
    ]
    for it in it1:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Step 2
    c2 = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.84), card_t, card_w, card_h)
    c2.fill.solid()
    c2.fill.fore_color.rgb = COLOR_CARD
    c2.line.color.rgb = COLOR_GOLD
    tf = c2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Dashboard Agenda & Alertas"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_GOLD
    it2 = [
        "React SPA (localhost:5173).",
        "Timeline cronológico de turnos anonimizados.",
        "Tarjetas de riesgo de ausentismo (Alto, Medio, Bajo).",
        "Botón 'Enviar WhatsApp' con notificación Toast popup."
    ]
    for it in it2:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Step 3
    c3 = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.88), card_t, card_w, card_h)
    c3.fill.solid()
    c3.fill.fore_color.rgb = COLOR_CARD
    c3.line.color.rgb = COLOR_GREEN
    tf = c3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Vista Colas & Fallback"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_GREEN
    it3 = [
        "Pestaña Métricas M/M/s.",
        "Conmutación dinámica entre Hellfish y Hooligans.",
        "Resiliencia Fallback ante desconexión de backend (Graceful Degradation)."
    ]
    for it in it3:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(12)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    add_speaker_notes(slide9, """A continuación, pasaremos a la demostración práctica en vivo de nuestro prototipo MVP funcional. Veremos en pantalla la integración completa entre la SPA en React 19 y los servicios API expuestos por FastAPI en Python, demostrando cómo la plataforma visualiza la agenda operativa, calcula el riesgo simulado de ausentismo y despliega el panel de métricas de Teoría de Colas.""")

    # ==========================================
    # SLIDE 10: Conclusiones y Roadmap
    # ==========================================
    slide10 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide10, "CONCLUSIONES Y ROADMAP", "Síntesis del Hito 50% (EP2) y Hoja de Ruta Hacia la Entrega Final")

    # 2 Columns: Accomplished vs Future
    w_c = Inches(5.6)
    h_c = Inches(4.8)
    top_c = Inches(1.8)

    # Completed 50%
    b1 = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_c, w_c, h_c)
    b1.fill.solid()
    b1.fill.fore_color.rgb = COLOR_CARD
    b1.line.color.rgb = COLOR_GREEN
    tf = b1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "✅ Hito 50% (EP2) — Logros Cumplidos"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_GREEN
    it1 = [
        "Relevamiento Cualitativo: Entrevistas a Hellfish y Hooligans completadas.",
        "Pipeline ETL & Anonimización: SHA-256 + Salt por sucursal (Ley 25.326).",
        "Formalización del Target y: 5 reglas determinísticas con exclusión ≥ 2h.",
        "Baseline M/M/s: Métricas λ, μ, ρ, Wq estocásticas calculadas sobre data real.",
        "Prototipo Web MVP: React 19 + FastAPI + Modo Fallback operativo."
    ]
    for it in it1:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(13)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    # Roadmap 75% / 100%
    b2 = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), top_c, w_c, h_c)
    b2.fill.solid()
    b2.fill.fore_color.rgb = COLOR_CARD
    b2.line.color.rgb = COLOR_ACCENT_LIGHT
    tf = b2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🚀 Roadmap Hito 75% / 100% (EP3)"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_ACCENT_LIGHT
    it2 = [
        "Entrenamiento ML Supervisado: XGBoost & Random Forest con SMOTE.",
        "Evaluación de Modelos: Curvas ROC-AUC, Precisión, Recall y F1-Score.",
        "Serialización Inferencial: Integración de binarios .joblib en FastAPI.",
        "Persistencia Relacional: Migración a PostgreSQL containerizado en Docker.",
        "Pruebas Integrales: Cobertura de tests E2E y evaluación final de usabilidad."
    ]
    for it in it2:
        p_i = tf.add_paragraph()
        p_i.text = f"• {it}"
        p_i.font.size = Pt(13)
        p_i.font.color.rgb = COLOR_TEXT_MAIN
        p_i.space_before = Pt(6)

    add_speaker_notes(slide10, """En síntesis, para esta entrega del 50% hemos alcanzado con éxito todos los objetivos fijados: consolidamos el relevamiento cualitativo en comercios reales, estructuramos un pipeline ETL robusto con anonimización legal bajo Ley 25.326, formalizamos la variable target y establecimos el baseline estocástico M/M/s sobre datos reales.

De cara a los próximos hitos, abordaremos el entrenamiento y tuneo de clasificadores XGBoost supervisados, la serialización del modelo inferencial y la migración a una infraestructura containerizada en PostgreSQL.

Quedo a la entera disposición del tribunal para iniciar la demostración en vivo y responder a sus apreciables preguntas. Muchas gracias.""")

    # ==========================================
    # BACKUP SLIDE B1: Target y
    # ==========================================
    sb1 = prs.slides.add_slide(blank_slide_layout)
    add_header(sb1, "BACKUP SLIDE B1 — PREGUNTAS DEL JURADO", "Defensa Metodológica: Lógica de las 5 Condiciones de la Variable Target y")

    card = sb1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = COLOR_GOLD
    tf = card.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "📌 Pregunta Frecuente: ¿Por qué considerar ausentismo a cancelaciones tardías o eliminaciones del local?"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_GOLD

    points = [
        "1. Cancelaciones Tardías (< 2 horas): El impacto económico es idéntico a un no-show físico. El profesional queda ocioso y no hay ventana temporal suficiente para publicar y reasignar el turno en la web.",
        "2. Eliminaciones por el Local (deleted_by != client): Ocurren cuando el cliente no se presenta y el encargado borra la cita manualmente de la agenda. Constituyen ausentismo real no pagado.",
        "3. Exclusión de Cancelaciones Anticipadas (≥ 2 horas): Se retiran de la matriz de ML porque el comercio recuperó el bloque horario y no sufrió pérdida irreparable. Penalizarlas sesgaría al clasificador."
    ]
    for pt in points:
        p_pt = tf.add_paragraph()
        p_pt.text = pt
        p_pt.font.size = Pt(13)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_before = Pt(8)

    add_speaker_notes(sb1, """Estimado tribunal, clasificar el ausentismo mediante una regla simple de 'asistió / no asistió' genera un sesgo severo en los datos transaccionales de comercios de servicios:

1. Cancelaciones Tardías (Condición 4): Si un cliente cancela su turno 15 minutos antes de la cita, operativamente el impacto económico es idéntico a un no-show absoluto: el profesional queda ocioso y no hay tiempo físico para reasignar la silla. Por ello, catalogamos las cancelaciones con margen menor a 2 horas como proxy de ausentismo (y = 1).

2. Eliminación por el Comercio (Condición 3): Muchas veces el cliente no viene y el encargado elimina la cita del sistema manualmente. Ese evento aparece con deleted_at NOT NULL pero deleted_by != client, configurando un ausentismo real.

3. Exclusión de Cancelaciones Anticipadas (Condición 5): Por el contrario, si el cliente canceló con más de 2 horas de anticipación, el comercio reabrió ese bloque en su web y logró ocupar la silla. Excluir estas filas de la matriz de entrenamiento de ML previene que el modelo penalice a clientes que operaron correctamente dentro del reglamento del comercio.""")

    # ==========================================
    # BACKUP SLIDE B2: M/M/s vs ML
    # ==========================================
    sb2 = prs.slides.add_slide(blank_slide_layout)
    add_header(sb2, "BACKUP SLIDE B2 — PREGUNTAS DEL JURADO", "Justificación Teórica Avanzada: Baseline M/M/s vs. Machine Learning Supervisado")

    card = sb2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = COLOR_ACCENT_LIGHT
    tf = card.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "📌 Pregunta Frecuente: ¿Por qué la Teoría de Colas no puede resolver el problema por sí sola?"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_ACCENT_LIGHT

    points = [
        "1. Desagregación de Poisson: M/M/s modela el ausentismo como un flujo efectivo (1-p)λ. Asume que todas las llegadas son aleatorias continuas y que la probabilidad p es idéntica para todos los clientes.",
        "2. Agendas Híbridas Discretas: Las barberías operan en bloques fijos. Un no-show provoca una pérdida irrecuperable de un bloque exacto de tiempo, dejando al servidor ocioso de forma forzada.",
        "3. Complementariedad Metodológica: M/M/s nos aporta el marco macro estocástico (ρ, Wq), mientras que ML supervisado aporta el scoring micro por reserva individual P(y=1 | X_i)."
    ]
    for pt in points:
        p_pt = tf.add_paragraph()
        p_pt.text = pt
        p_pt.font.size = Pt(13)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_before = Pt(8)

    add_speaker_notes(sb2, """La Teoría de Colas clásica M/M/s es una herramienta estocástica brillante para dimensionar la capacidad agregada en estado estable, pero presenta tres limitaciones estructurales insalvables para la gestión individual de agendas:

1. Supuesto de Homogeneidad: M/M/s asume que todas las llegadas siguen un proceso de Poisson continuo y que todos los clientes tienen la misma probabilidad 'p' de ausentarse. No permite incorporar variables de comportamiento individual como el historial de puntualidad o el canal de agendamiento.

2. Pérdida por Bloques Discretos: En un comercio con agenda, las citas están empaquetadas en bloques (ej. 30 min). El ausentismo no reduce suavemente la carga de trabajo; deja un hueco de tiempo exacto e irrecuperable.

3. Solución Propuesta: El modelo M/M/s nos otorga un baseline cuantitativo global para conocer la utilización del negocio (rho), pero requerimos clasificadores de Aprendizaje Automático supervisado (como XGBoost) para computar la probabilidad condicional P(y=1 | X_i) para el vector de características de cada cliente específico.""")

    # ==========================================
    # BACKUP SLIDE B3: Ley 25.326
    # ==========================================
    sb3 = prs.slides.add_slide(blank_slide_layout)
    add_header(sb3, "BACKUP SLIDE B3 — PREGUNTAS DEL JURADO", "Cumplimiento de la Ley 25.326 y Criptografía Aplicada")

    card = sb3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD
    card.line.color.rgb = COLOR_GREEN
    tf = card.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "📌 Pregunta Frecuente: ¿Cómo garantizan la irreversibilidad de los datos personales?"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_GREEN

    points = [
        "1. Hash SHA-256 con Salt Específico: Cada comercio posee una clave salt secreta. Se evita el uso de hashes simples expuestos a tablas Rainbow o fuerza bruta.",
        "2. Truncamiento a 16 Hex (64 bits): Al truncar la salida de SHA-256 a 16 caracteres hex, se destruye la entropía suficiente para impedir la ingeniería inversa, preservando colisiones nulas a escala local.",
        "3. Purga en Memoria: Nombres y teléfonos en texto plano son eliminados de la memoria en Pandas antes de exportar cualquier matriz de entrenamiento."
    ]
    for pt in points:
        p_pt = tf.add_paragraph()
        p_pt.text = pt
        p_pt.font.size = Pt(13)
        p_pt.font.color.rgb = COLOR_TEXT_MAIN
        p_pt.space_before = Pt(8)

    add_speaker_notes(sb3, """El cumplimiento de la Ley N° 25.326 de Protección de Datos Personales se fundamenta en el principio de disociación e irreversibilidad de la información:

1. Criptografía con Salt Exclusivo: No aplicamos una función Hash simple sobre el nombre o teléfono, ya que sería vulnerable a ataques de fuerza bruta o tablas Rainbow. Combinamos cada dato con un Salt secreto y único por sucursal generado aleatoriamente.

2. Truncamiento a 16 Caracteres Hexadecimales: Al truncar la salida de SHA-256 a 16 dígitos hex, reducimos el espacio de búsqueda manteniendo una colisión prácticamente nula para la escala de clientes del comercio (2^64 combinaciones posibles), imposibilitando cualquier intento de ingeniería inversa.

3. Omisión en Persistencia Analítica: Las columnas crudas 'client' y 'phone' se eliminan completamente de la memoria en Pandas antes de exportar la matriz procesada processed_appointments_matrix.csv. La base analítica contiene únicamente identidades disociadas.""")

    # Save outputs
    out_pfi = "/Users/mauriciooubina/Desktop/Workspace/pfi/Presentacion_Defensa_50_PFI.pptx"
    out_latex = "/Users/mauriciooubina/Downloads/UADE_PFI_Template-develop/Presentacion_Defensa_50_PFI.pptx"

    prs.save(out_pfi)
    prs.save(out_latex)
    print(f"Successfully generated PowerPoint presentations:\n - {out_pfi}\n - {out_latex}")

if __name__ == "__main__":
    create_deck()
