from fpdf import FPDF
from datetime import datetime
import os

class PDFGenerator(FPDF):
    def __init__(self):
        super().__init__()
        self.default_font = 'helvetica'  # Fuente por defecto
        self.setup_unicode_font()
        self.set_font(self.default_font, '', 10)  # Establecer fuente por defecto
    
    def setup_unicode_font(self):
        """Configura una fuente Unicode para soportar emojis y caracteres especiales"""
        try:
            # Rutas donde podrían estar instaladas las fuentes DejaVu
            dejavu_paths = [
                '/Library/Fonts/DejaVuSans.ttf',  # macOS
                '/System/Library/Fonts/DejaVuSans.ttf',  # Alternativa macOS
                'C:/Windows/Fonts/DejaVuSans.ttf',  # Windows
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
            ]
            
            # Buscar la fuente DejaVu
            for font_path in dejavu_paths:
                if os.path.exists(font_path):
                    try:
                        self.add_font('DejaVu', '', font_path, uni=True)
                        bold_path = font_path.replace('.ttf', '-Bold.ttf')
                        if os.path.exists(bold_path):
                            self.add_font('DejaVu', 'B', bold_path, uni=True)
                        self.default_font = 'DejaVu'
                        print(f"Usando fuente: {font_path}")
                        return
                    except Exception as e:
                        print(f"Error al cargar fuente {font_path}: {e}")
            
            # Si no se encuentra DejaVu, usar solo la versión normal de Arial Unicode
            # sin intentar usar negrita, ya que puede no estar disponible
            arial_paths = [
                '/Library/Fonts/Arial Unicode.ttf',  # macOS
                'C:/Windows/Fonts/ARIALUNI.TTF',    # Windows
                '/usr/share/fonts/truetype/ariblk.ttf'  # Linux
            ]
            
            for font_path in arial_paths:
                if os.path.exists(font_path):
                    try:
                        self.add_font('ArialUnicode', '', font_path, uni=True)
                        # No registramos la versión en negrita para evitar errores
                        self.default_font = 'ArialUnicode'
                        print(f"Usando fuente: {font_path} (solo normal, sin negrita)")
                        return
                    except Exception as e:
                        print(f"Error al cargar fuente {font_path}: {e}")
            
            # Si no se encuentra ninguna fuente Unicode, usar Helvetica
            print("No se encontró ninguna fuente Unicode, usando Helvetica (soporte limitado)")
            self.default_font = 'helvetica'
            
        except Exception as e:
            print(f"Error en setup_unicode_font: {e}")
            self.default_font = 'helvetica'
    
    def safe_text(self, text):
        """Limpia el texto de caracteres problemáticos si no se puede usar Unicode"""
        if not isinstance(text, str):
            text = str(text)
            
        # Si estamos usando una fuente Unicode, devolver el texto tal cual
        if hasattr(self, 'default_font') and self.default_font in ['DejaVu', 'ArialUnicode']:
            return text
        
        # Reemplazar emojis comunes por texto
        emoji_replacements = {
            '📅': '[Fecha]',
            '⭐': '[Estrella]',
            '✅': '[Check]',
            '❌': '[X]',
            '🔥': '[Fuego]',
            '💡': '[Idea]',
            '📝': '[Nota]',
            '🎯': '[Objetivo]',
            '🚀': '[Cohete]',
            '📊': '[Gráfico]',
            '👕': '[Camiseta]',
            '🏆': '[Trofeo]',
            '👤': '[Usuario]',
            '📞': '[Teléfono]',
            '🌍': '[Mundo]',
            '⚽': '[Balón]',
            '📏': '[Regla]',
            '🔷': '[Diamante]'
        }
        
        for emoji, replacement in emoji_replacements.items():
            text = text.replace(emoji, replacement)
        
        return text
    
    def add_header_section(self, player_data):
        """Añade el encabezado del reporte"""
        self.set_fill_color(200, 230, 200)  # Verde claro
        self.rect(0, 0, self.w, 40, 'F')  # Rectángulo de fondo
        
        # Título - manejar negrita de forma segura
        self.set_xy(0, 10)
        try:
            self.set_font(self.default_font, 'B', 16)
        except:
            # Si falla la negrita, usar normal
            self.set_font(self.default_font, '', 16)
        
        self.cell(0, 10, self.safe_text(f"{player_data['jugador']} - FIRMAR - MEJORA PLANTILLA"), 0, 1, 'C')
        
        # Línea decorativa
        self.set_draw_color(0, 100, 0)
        self.line(20, 30, self.w - 20, 30)
        
        self.set_y(45)  # Espacio después del header
    
    def add_personal_info(self, player_data):
        """Añade la sección de información personal"""
        x = 20
        y = 60
        
        # Foto del jugador (si existe)
        if 'imagen_path' in player_data and player_data['imagen_path'] and os.path.exists(player_data['imagen_path']):
            try:
                from PIL import Image
                # Redimensionar imagen manteniendo la relación de aspecto
                img = Image.open(player_data['imagen_path'])
                img.thumbnail((60, 80))  # Tamaño máximo 60x80 píxeles
                img_path = f"temp_{os.path.basename(player_data['imagen_path'])}"
                img.save(img_path)  # Guardar temporalmente la imagen redimensionada
                
                self.image(img_path, x, y, 50)  # Ancho fijo de 50mm
                y += 60  # Ajustar posición Y después de la imagen
                
                # Eliminar archivo temporal
                os.remove(img_path)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
        
        # Información personal
        self.set_font(self.default_font, '', 10)
        info_items = [
            ("📅", f"Edad: {player_data['edad']} años"),
            ("🌍", f"Nacionalidad: {player_data['nacionalidad']}"),
            ("⚽", f"Pie hábil: {player_data['pie']}"),
            ("📏", f"Talla: {player_data['talla']} cm")
        ]
        
        for emoji, text in info_items:
            self.set_xy(x, y)
            self.cell(10, 8, self.safe_text(emoji), 0, 0, 'L')
            self.cell(0, 8, self.safe_text(text), 0, 1, 'L')
            y += 7  # Espacio entre líneas
    
    def add_club_info(self, player_data):
        """Añade la sección de información del club"""
        x = 80  # Ajustar según el diseño
        y = 60  # Misma altura que la columna 1
        
        self.set_font(self.default_font, 'B', 12)
        self.set_xy(x, y - 15)
        self.cell(0, 10, self.safe_text("Club y Contrato"), 0, 1, 'L')
        
        # Información del club
        self.set_font(self.default_font, '', 10)
        info_items = [
            ("👕", f"Club actual: {player_data['club_actual']}"),
            ("🏆", f"Liga: {player_data['liga']}"),
            ("📅", f"Fin de contrato: {player_data['fin_contrato']}"),
            ("👤", f"Agente: {player_data['agente']}"),
            ("📞", f"Teléfono: {player_data['telefono_agente']}")
        ]
        
        for emoji, text in info_items:
            self.set_xy(x, y)
            self.cell(10, 8, self.safe_text(emoji), 0, 0, 'L')
            self.multi_cell(0, 8, self.safe_text(text), 0, 'L')
            y += 7  # Espacio entre líneas
    
    def add_positions(self, player_data):
        """Añade la sección de posiciones"""
        x = 140  # Ajustar según el diseño
        y = 60  # Misma altura que las otras columnas
        
        self.set_font(self.default_font, 'B', 12)
        self.set_xy(x, y - 15)
        self.cell(0, 10, self.safe_text("Posiciones"), 0, 1, 'L')
        
        self.set_font(self.default_font, '', 10)
        positions = [
            ("⭐", f"Principal: {player_data['posicion_principal']}"),
            ("🔷", f"Secundaria: {player_data.get('posicion_secundaria', 'No especificada')}")
        ]
        
        for icon, text in positions:
            self.set_xy(x, y)
            self.cell(10, 8, self.safe_text(icon), 0, 0)
            self.multi_cell(0, 8, self.safe_text(text), 0, 'L')
            y += 10
    
    def generate_pdf(self, player_data, output_path):
        """Genera el PDF completo"""
        self.add_page()
        
        # Añadir secciones
        self.add_header_section(player_data)
        self.add_personal_info(player_data)
        self.add_club_info(player_data)
        self.add_positions(player_data)
        
        # Guardar el PDF
        self.output(output_path)

# Función de conveniencia para generar el PDF
def generate_player_pdf(player_data, output_path):
    """Función de conveniencia para generar el PDF del jugador"""
    try:
        pdf = PDFGenerator()
        pdf.generate_pdf(player_data, output_path)
        return True, ""
    except Exception as e:
        return False, str(e)
