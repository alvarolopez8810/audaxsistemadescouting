from fpdf import FPDF
from PIL import Image
import os
import pandas as pd
from datetime import datetime

def setup_fonts(pdf):
    """Setup fonts, using only built-in fonts for maximum compatibility"""
    # Use Helvetica as it's a standard built-in font in fpdf2
    font_name = 'helvetica'
    pdf.set_font(font_name, '', 10)
    return font_name

class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')
        self.width = 210  # A4 width in mm
        self.height = 297  # A4 height in mm
        self.margin = 20  # 20mm margins
        self.column_width = (self.width - 2 * self.margin - 20) / 3  # 3 columns with 10mm gap
        
        # Setup fonts with emoji support if possible
        self.font_name = setup_fonts(self.pdf)
        
    def draw_progress_bar(self, x, y, width, height, percentage, color=(70, 130, 180)):
        """Dibuja una barra de progreso con borde y relleno"""
        # Borde
        self.pdf.set_draw_color(200, 200, 200)
        self.pdf.rect(x, y, width, height)
        
        # Relleno
        fill_width = (width * percentage) / 100
        self.pdf.set_fill_color(*color)
        self.pdf.rect(x, y, fill_width, height, 'F')
        
        # Texto del porcentaje
        self.pdf.set_xy(x, y)
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font(self.font_name, 'B', 8)
        self.pdf.cell(width, height, f"{percentage:.1f}%", 0, 0, 'C')
        self.pdf.set_text_color(0, 0, 0)  # Reset text color

    def add_header_section(self, player_data):
        """Header verde con título principal"""
        self.pdf.set_fill_color(200, 230, 200)  # Verde claro
        self.pdf.rect(0, 0, self.width, 40, 'F')  # Rectángulo de fondo
        
        # Título - using only built-in font styles
        self.pdf.set_xy(0, 10)
        self.pdf.set_font('helvetica', 'B', 16)  # Using direct font name
        self.pdf.cell(self.width, 10, f"{player_data['jugador']} - FIRMAR - MEJORA PLANTILLA", 0, 1, 'C')
        
        # Línea decorativa
        self.pdf.set_draw_color(0, 100, 0)
        self.pdf.line(self.margin, 30, self.width - self.margin, 30)
        
        self.pdf.set_y(45)  # Espacio después del header
        
        # Reset to regular font
        self.pdf.set_font('helvetica', '', 10)

    def add_personal_info(self, player_data):
        """Columna 1: Información personal con foto"""
        x = self.margin
        y = 60  # Ajustar según sea necesario
        
        # Foto del jugador (si existe)
        if 'imagen_path' in player_data and player_data['imagen_path'] and os.path.exists(player_data['imagen_path']):
            try:
                # Redimensionar imagen manteniendo la relación de aspecto
                img = Image.open(player_data['imagen_path'])
                img.thumbnail((60, 80))  # Tamaño máximo 60x80 píxeles
                img_path = f"temp_{os.path.basename(player_data['imagen_path'])}"
                img.save(img_path)  # Guardar temporalmente la imagen redimensionada
                
                self.pdf.image(img_path, x, y, 50)  # Ancho fijo de 50mm
                y += 60  # Ajustar posición Y después de la imagen
                
                # Eliminar archivo temporal
                os.remove(img_path)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
        
        # Información personal - Reemplazando emojis con texto
        self.pdf.set_font('helvetica', '', 10)
        info_items = [
            ("[Edad]", f"Edad: {player_data['edad']} años"),
            ("[Pais]", f"Nacionalidad: {player_data['nacionalidad']}"),
            ("[Pie]", f"Pie hábil: {player_data['pie']}"),
            ("[Altura]", f"Talla: {player_data['talla']} cm")
        ]
        
        for emoji, text in info_items:
            self.pdf.set_x(x)
            self.pdf.cell(10, 8, emoji, 0, 0, 'L')
            self.pdf.cell(0, 8, text, 0, 1, 'L')
            y += 7  # Espacio entre líneas
        
        # Sección de valoración global
        self.pdf.set_x(x)
        self.pdf.set_font(self.font_name, 'B', 10)
        self.pdf.cell(0, 10, "Valoración Global:", 0, 1)
        
        # Barra de progreso para valoración global
        valoracion_global = float(player_data.get('valoracion_global', 0))
        self.draw_progress_bar(x, y, 80, 8, valoracion_global, (70, 130, 180))
        self.pdf.set_font(self.font_name, '', 8)
        self.pdf.set_xy(x + 85, y)
        self.pdf.cell(0, 8, f"{valoracion_global}%", 0, 1)
        
        # Sección de firma
        self.pdf.set_y(self.pdf.get_y() + 10)
        self.pdf.set_font(self.font_name, 'I', 8)
        self.pdf.cell(0, 5, "Firma del ojeador: __________________________", 0, 1)
        self.pdf.cell(0, 5, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)

    def add_club_info(self, player_data):
        """Columna 2: Información del club y contrato"""
        x = self.margin + self.column_width + 10  # 10mm de separación
        y = 50  # Misma altura que la columna 1
        
        self.pdf.set_font('helvetica', 'B', 12)
        self.pdf.set_xy(x, y - 15)
        self.pdf.cell(self.column_width, 10, "Club y Contrato", 0, 1, 'L')
        
        # Información del club - Reemplazando emojis con texto
        self.pdf.set_font('helvetica', '', 10)
        info_items = [
            ("[Club]", f"Club actual: {player_data['club_actual']}"),
            ("[Liga]", f"Liga: {player_data['liga']}"),
            ("[Fecha]", f"Fin de contrato: {player_data['fin_contrato']}"),
            ("[Agente]", f"Agente: {player_data['agente']}"),
            ("[Tel]", f"Teléfono: {player_data['telefono_agente']}")
        ]
        
        for emoji, text in info_items:
            self.pdf.set_x(x)
            self.pdf.cell(10, 8, emoji, 0, 0, 'L')
            self.pdf.cell(0, 8, text, 0, 1, 'L')
            y += 7  # Espacio entre líneas
        
        # Sección de valoración de mercado
        self.pdf.set_x(x)
        self.pdf.set_font(self.font_name, 'B', 10)
        self.pdf.cell(0, 10, "Valor de mercado estimado:", 0, 1)
        
        # Barra de progreso para valor de mercado
        valor_mercado = float(player_data.get('valor_mercado', 0))
        self.draw_progress_bar(x, y, 80, 8, valor_mercado, (60, 179, 113))  # Verde
        self.pdf.set_font(self.font_name, '', 8)
        self.pdf.set_xy(x + 85, y)
        self.pdf.cell(0, 8, f"${valor_mercado:,.0f}M", 0, 1)
        
        # Sección de firma
        self.pdf.set_y(self.pdf.get_y() + 10)
        self.pdf.set_font(self.font_name, 'I', 8)
        self.pdf.cell(0, 5, "Firma del director deportivo: __________________", 0, 1)

    def add_positions(self, player_data):
        """Columna 3: Posiciones del jugador"""
        x = self.margin + (self.column_width + 10) * 2
        y = 50  # Misma altura que las otras columnas
        
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_xy(x, y - 15)
        self.pdf.cell(self.column_width, 10, "Posiciones", 0, 1, 'L')
        
        self.pdf.set_font('helvetica', '', 10)
        positions = [
            ("[Principal]", f"Posición principal: {player_data['posicion_principal']}"),
            ("[Secundaria]", f"Posición secundaria: {player_data.get('posicion_secundaria', 'No especificada')}")
        ]
        
        for icon, text in positions:
            self.pdf.set_xy(x, y)
            self.pdf.cell(10, 8, icon, 0, 0)
            self.pdf.multi_cell(self.column_width - 10, 8, text, 0, 'L')
            y += 10
            
        # Espacio para evaluaciones
        y += 10
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.set_xy(x, y)
        self.pdf.cell(self.column_width, 10, "Evaluación AUDAX", 0, 1, 'L')
        
        # Cálculo de la puntuación AUDAX
        rendimiento = player_data.get('rendimiento', 0)
        potencial = player_data.get('potencial', 0)
        adaptabilidad = player_data.get('adaptabilidad', 0)
        audax_score = ((rendimiento + potencial + adaptabilidad) / 18) * 10
        
        # Barra de progreso AUDAX
        self.pdf.set_font('Arial', '', 10)
        self.pdf.set_xy(x, y + 15)
        self.pdf.cell(40, 6, f"Puntuación: {audax_score:.1f}/10", 0, 1)
        self.draw_progress_bar(x, y + 22, self.column_width, 8, audax_score * 10)
        
        return y + 40

    def add_metrics_section(self, player_data):
        """Sección de métricas principales"""
        # Título de la sección
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 15, "Métricas Principales", 0, 1, 'C')
        
        # Configuración de columnas
        col_width = (self.width - 2 * self.margin - 20) / 3  # 3 columnas con 10mm de separación
        x = self.margin
        y = self.pdf.get_y()
        
        # Datos de las métricas
        metrics = [
            {"title": "RENDIMIENTO", "value": player_data.get('rendimiento', 0), "max": 6},
            {"title": "POTENCIAL", "value": player_data.get('potencial', 0), "max": 6},
            {"title": "ADAPTABILIDAD", "value": player_data.get('adaptabilidad', 0), "max": 6}
        ]
        
        # Dibujar las 3 métricas
        for i, metric in enumerate(metrics):
            current_x = x + (col_width + 10) * i
            
            # Fondo de la tarjeta
            self.pdf.set_fill_color(245, 245, 245)
            self.pdf.rect(current_x, y, col_width, 40, 'F')
            
            # Título
            self.pdf.set_font('Arial', 'B', 10)
            self.pdf.set_xy(current_x, y + 5)
            self.pdf.cell(col_width, 6, metric['title'], 0, 1, 'C')
            
            # Valor numérico
            self.pdf.set_font('Arial', 'B', 16)
            self.pdf.set_xy(current_x, y + 12)
            self.pdf.cell(col_width, 10, f"{metric['value']}/{metric['max']}", 0, 1, 'C')
            
            # Barra de progreso
            percentage = (metric['value'] / metric['max']) * 100
            self.draw_progress_bar(current_x + 10, y + 25, col_width - 20, 8, percentage)
        
        self.pdf.set_y(y + 50)  # Espacio después de la sección

    def add_technical_evaluations(self, player_data):
        """Sección de evaluaciones técnicas"""
        # Título de la sección
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 15, "Evaluaciones Técnicas", 0, 1, 'C')
        
        # Configuración
        y = self.pdf.get_y()
        bar_width = 100
        
        # Lista de evaluaciones
        evaluations = [
            ("Técnica", player_data.get('evaluacion_tecnica', 0)),
            ("Táctica", player_data.get('evaluacion_tactica', 0)),
            ("Física", player_data.get('evaluacion_fisica', 0)),
            ("Mental", player_data.get('evaluacion_mental', 0))
        ]
        
        # Dibujar cada evaluación
        for i, (name, value) in enumerate(evaluations):
            current_y = y + (i * 15)
            
            # Nombre de la evaluación
            self.pdf.set_font('Arial', '', 10)
            self.pdf.set_xy(self.margin, current_y)
            self.pdf.cell(40, 10, name, 0, 0)
            
            # Valor numérico
            self.pdf.set_x(self.margin + 40)
            self.pdf.cell(20, 10, f"{value}/6", 0, 0, 'R')
            
            # Barra de progreso
            percentage = (value / 6) * 100
            self.draw_progress_bar(self.margin + 65, current_y + 3, bar_width, 8, percentage)
        
        self.pdf.set_y(y + 70)  # Espacio después de la sección

    def add_conclusions(self, player_data):
        """Sección de conclusiones con 3 columnas"""
        # Título de la sección
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 15, "Conclusiones", 0, 1, 'C')
        
        # Configuración de columnas
        col_width = (self.width - 2 * self.margin - 20) / 3  # 3 columnas con 10mm de separación
        x = self.margin
        y = self.pdf.get_y()
        
        # Secciones
        sections = [
            {"title": "Descripción General", "content": player_data.get('descripcion_general', '')},
            {"title": "Historial Médico", "content": player_data.get('historial_lesiones', '')},
            {"title": "Referencias Adicionales", "content": player_data.get('referencias', '')}
        ]
        
        # Dibujar las 3 columnas
        for i, section in enumerate(sections):
            current_x = x + (col_width + 10) * i
            
            # Título de la sección
            self.pdf.set_font('Arial', 'B', 10)
            self.pdf.set_xy(current_x, y)
            self.pdf.cell(col_width, 8, section['title'], 'B', 1)  # Línea inferior
            
            # Contenido
            self.pdf.set_xy(current_x, y + 10)
            self.pdf.set_font('Arial', '', 9)
            
            # Manejar texto largo con saltos de línea
            text = section['content'] if section['content'] else "Sin información disponible"
            self.pdf.multi_cell(col_width, 5, text, 0, 'L')
        
        self.pdf.set_y(y + 80)  # Espacio después de la sección

    def generate_pdf(self, player_data, output_path):
        """Genera el PDF completo"""
        # Configuración inicial
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Secciones del informe
        self.add_header_section(player_data)
        
        # Primera fila: 3 columnas
        self.add_personal_info(player_data)
        self.add_club_info(player_data)
        final_y = self.add_positions(player_data)
        
        # Asegurar que estemos en una posición consistente después de las columnas
        self.pdf.set_y(final_y)
        
        # Secciones adicionales
        self.add_metrics_section(player_data)
        self.add_technical_evaluations(player_data)
        
        # Nueva página para las conclusiones
        self.pdf.add_page()
        self.add_conclusions(player_data)
        
        # Guardar el PDF
        self.pdf.output(output_path, 'F')
        return output_path

def clean_data(value):
    """Limpia los datos para mostrar en el PDF"""
    if pd.isna(value) or value == '' or value == 0:
        return "Sin información disponible"
    return str(value)

def get_player_data(df, jugador_seleccionado):
    """Obtiene y limpia los datos del jugador seleccionado"""
    try:
        row = df[df['jugador'] == jugador_seleccionado].iloc[0]
        return {
            'jugador': row['jugador'],
            'edad': clean_data(row.get('edad', '')),
            'talla': f"{clean_data(row.get('talla', ''))} cm",
            'nacionalidad': clean_data(row.get('nacionalidad', '')),
            'pie': clean_data(row.get('pie', '')),
            'club_actual': clean_data(row.get('club_actual', '')),
            'liga': clean_data(row.get('liga', '')),
            'fin_contrato': clean_data(row.get('fin_contrato', '')),
            'agente': clean_data(row.get('agente', '')),
            'telefono_agente': clean_data(row.get('telefono_agente', '')),
            'posicion_principal': clean_data(row.get('posicion_principal', '')),
            'posicion_secundaria': clean_data(row.get('posicion_secundaria', '')),
            'rendimiento': float(row.get('rendimiento', 0)),
            'potencial': float(row.get('potencial', 0)),
            'adaptabilidad': float(row.get('adaptabilidad', 0)),
            'evaluacion_tecnica': float(row.get('evaluacion_tecnica', 0)),
            'evaluacion_tactica': float(row.get('evaluacion_tactica', 0)),
            'evaluacion_fisica': float(row.get('evaluacion_fisica', 0)),
            'evaluacion_mental': float(row.get('evaluacion_mental', 0)),
            'descripcion_general': clean_data(row.get('descripcion_general', '')),
            'historial_lesiones': clean_data(row.get('historial_lesiones', '')),
            'referencias': clean_data(row.get('referencias', '')),
            'imagen_path': row.get('imagen_path', '')
        }
    except Exception as e:
        print(f"Error al obtener datos del jugador: {e}")
        return None
