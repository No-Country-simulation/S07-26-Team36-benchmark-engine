from fpdf import FPDF

class InstructivoPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(249, 115, 22)
        self.cell(0, 10, 'Benchmark de Madurez - Data Centers', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Instructivo de Usuario', align='C', new_x='LMARGIN', new_y='NEXT')
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='C')

    def section(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, title, new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        self.cell(indent, 5, '')
        self.cell(5, 5, '- ')
        self.multi_cell(0, 5, text)
        self.ln(1)


pdf = InstructivoPDF()
pdf.alias_nb_pages()
pdf.add_page()

pdf.set_font('Helvetica', 'B', 18)
pdf.set_text_color(40, 40, 40)
pdf.cell(0, 12, 'Guia Paso a Paso para Operadores', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(4)

pdf.body('Este instructivo te guia a traves del Benchmark de Madurez Operacional para Data Centers.')
pdf.body('Tiempo estimado: menos de 10 minutos. 12 preguntas. Resultado inmediato con PDF descargable.')

pdf.section('1. Acceso al Benchmark')
pdf.body('Abri el formulario web en tu navegador:')
pdf.body('   Produccion: https://s07-26-team36-benchmark-engine-565u.onrender.com')
pdf.body('   Local: http://localhost:8000')
pdf.body('Veras la pantalla de inicio con una descripcion general y el boton "Iniciar diagnostico".')

pdf.section('2. Boton de Instrucciones (Opcional)')
pdf.body('Antes de empezar, podes hacer clic en "Ver instrucciones completas" para ver:')
pdf.bullet('Que mide cada una de las 5 dimensiones')
pdf.bullet('Como interpretar la escala 1-4')
pdf.bullet('Que recibis al final (score, percentil, perfil, PDF)')
pdf.bullet('Metodologia del rebalanceo dinamico (N/(N+K))')
pdf.bullet('Privacidad: respuestas 100% anonimas')

pdf.section('3. Completar el Cuestionario')
pdf.body('El benchmark tiene 5 pasos (uno por dimension). En cada paso:')
pdf.bullet('Leer la introduccion de la dimension (que mide y por que importa)')
pdf.bullet('Responder 2-3 preguntas seleccionando una opcion (1 a 4)')
pdf.bullet('Escala: 1 = incipiente/reactivo  |  4 = optimizado/autonomo')
pdf.bullet('Usar el icono "?" junto a cada pregunta para ver ayuda contextual')
pdf.bullet('Clic en "Siguiente" para avanzar; "Anterior" para corregir')
pdf.body('Todas las preguntas son obligatorias. No hay respuestas correctas/incorrectas: selecciona la que refleje la realidad actual de tu facility.')

pdf.section('4. Las 5 Dimensiones (Resumen)')
pdf.bullet('Visibilidad Cross-Layer (25%): P1-P3. Monitoreo unificado energia/cooling vs workloads, granularidad, reaccion a bursts de IA.')
pdf.bullet('Atribucion de Friccion (20%): P4-P5. Costo financiero de stranded capacity, root-cause de ineficiencias fisicas-TI.')
pdf.bullet('Latencia de Coordinacion (25%): P6-P8. Tiempo para aprovisionar, respuesta a fallas cooling, sincronizacion politicas energia-computo.')
pdf.bullet('Auto-Cuantificacion (15%): P9-P10. KPI de capacidad ociosa, % estimado de stranded capacity.')
pdf.bullet('Bloqueantes (15%): P11-P12. Barreras organizacionales, nivel de automatizacion permitida sobre infraestructura fisica.')

pdf.section('5. Resultado Inmediato')
pdf.body('Al terminar, veras:')
pdf.bullet('Score total (0-100) y percentil global (ej. "superas al 67% de la industria")')
pdf.bullet('Grafico de anillo con tu puntuacion')
pdf.bullet('Desglose por dimension con barras; la mas debil marcada como "Punto debil"')
pdf.bullet('Tu perfil de friccion principal (ej. "Operador a ciegas", "El apagafuegos")')
pdf.bullet('Descripcion del problema y recomendacion: "Que hace el cuartil superior"')
pdf.bullet('Metadatos: N respuestas en dataset, % peso datos primarios')

pdf.section('6. Descargar Reporte PDF')
pdf.body('Hace clic en el boton "Descargar PDF" (o usa la API: GET /api/v1/report/{id}/pdf).')
pdf.body('El PDF incluye: resumen ejecutivo, desglose por dimension, perfil de friccion, recomendacion cuartil superior, contexto del dataset y metodologia.')

pdf.section('7. Dashboard Publico')
pdf.body('Visita /dashboard para ver estadisticas agregadas del dataset en tiempo real:')
pdf.bullet('Total de respuestas, score promedio/mediano, percentil promedio')
pdf.bullet('Distribucion de scores por rangos (0-20, 20-40, 40-60, 60-80, 80-100)')
pdf.bullet('Dimension mas debil frecuente y perfiles de friccion mas comunes')
pdf.bullet('Peso actual de datos primarios en el rebalanceo (N/(N+K))')

pdf.section('8. Preguntas Frecuentes')
pdf.bullet('P: ¿Mis datos son privados? R: Si, 100% anonimos. Solo se agregan al dataset para mejorar el benchmark.')
pdf.bullet('P: ¿Puedo repetir el benchmark? R: Si, cuantas veces quieras. Cada envio genera un nuevo submission ID.')
pdf.bullet('P: ¿Que significa el percentil? R: Porcentaje de operadores en la distribucion de referencia que tienen score MENOR al tuyo.')
pdf.bullet('P: ¿Como mejora la precision? R: Con cada respuesta nueva, el peso de datos primarios sube (formula N/(N+50)).')

pdf.section('9. Soporte y Contacto')
pdf.body('Repositorio: https://github.com/No-Country-simulation/S07-26-Team36-benchmark-engine.git')
pdf.body('Equipo: Gustavo (Data Scientist), Gio (Data Analyst), Marisol (Functional Analyst)')


pdf_bytes = pdf.output(dest='S')
if isinstance(pdf_bytes, str):
    pdf_bytes = pdf_bytes.encode('latin-1')
elif isinstance(pdf_bytes, bytearray):
    pdf_bytes = bytes(pdf_bytes)

with open('Instructivo_Usuario.pdf', 'wb') as f:
    f.write(pdf_bytes)

print('PDF generado: Instructivo_Usuario.pdf')