import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import base64
import tempfile
import os
from pdf_generator_enhanced import generate_player_pdf

# ====================================
# CONFIGURACIÓN DE PÁGINA
# ====================================
st.set_page_config(
    page_title="Sistema de Scouting",
    page_icon="AudaxEscudo.png",
    layout="wide"
)

# ====================================
# CONSTANTES
# ====================================
DATABASE_FILE = "scouting_database.csv"

# ====================================
# FUNCIONES DE BASE DE DATOS
# ====================================

def create_initial_database():
    """Crea la base de datos inicial si no existe"""
    # Crear directorio para imágenes si no existe
    os.makedirs("jugadores_img", exist_ok=True)
    
    if not os.path.exists("scouting_database.csv"):
        columns = [
            "fecha_creacion", "jugador", "edad", "talla", "fecha_nacimiento", 
            "nacionalidad", "pie", "club_actual", "fin_contrato", 
            "agente", "telefono_agente", "posicion_principal", "posicion_secundaria",
            "descripcion_general", "rendimiento", "potencial", "adaptabilidad",
            "evaluacion_tecnica", "evaluacion_tactica", "evaluacion_fisica", 
            "evaluacion_mental", "observaciones_tecnica", "observaciones_tactica",
            "observaciones_fisica", "observaciones_mental", "referencias", 
            "historial_lesiones", "estado_lesiones", "veredicto", "imagen_path"
        ]
        df_empty = pd.DataFrame(columns=columns)
        df_empty.to_csv("scouting_database.csv", index=False)

def save_uploaded_file(uploaded_file, player_name):
    """Guarda el archivo subido y devuelve la ruta relativa"""
    try:
        # Crear un nombre de archivo seguro a partir del nombre del jugador
        safe_name = "".join(c if c.isalnum() else "_" for c in player_name).strip("_")
        file_ext = os.path.splitext(uploaded_file.name)[1]
        filename = f"{safe_name}_{int(datetime.now().timestamp())}{file_ext}"
        filepath = os.path.join("jugadores_img", filename)
        
        # Guardar el archivo
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filepath
    except Exception as e:
        st.error(f"Error al guardar la imagen: {str(e)}")
        return None

def save_player(player_data, uploaded_file=None):
    """Guarda los datos de un jugador en la base de datos"""
    try:
        if not os.path.exists("scouting_database.csv"):
            create_initial_database()
        
        # Guardar la imagen si se proporcionó una
        if uploaded_file is not None:
            filepath = save_uploaded_file(uploaded_file, player_data.get('jugador', 'jugador'))
            if filepath:
                player_data['imagen_path'] = filepath
        
        df = pd.read_csv("scouting_database.csv")
        df = pd.concat([df, pd.DataFrame([player_data])], ignore_index=True)
        df.to_csv("scouting_database.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Error al guardar el jugador: {str(e)}")
        return False

def load_players():
    """Carga todos los jugadores de la base de datos"""
    if not os.path.exists("scouting_database.csv"):
        return pd.DataFrame()
    try:
        return pd.read_csv("scouting_database.csv")
    except Exception as e:
        st.error(f"Error al cargar los jugadores: {str(e)}")
        return pd.DataFrame()

# ====================================
# FUNCIÓN PARA CARGAR POSICIONES
# ====================================

def load_positions():
    """Carga las posiciones desde el archivo Excel o usa valores por defecto"""
    try:
        if os.path.exists("ItemsPosiciones.xlsx"):
            df = pd.read_excel("ItemsPosiciones.xlsx")
            if 'Posición' in df.columns:
                return df['Posición'].dropna().unique().tolist()
    except Exception as e:
        st.warning(f"No se pudo cargar el archivo de posiciones: {str(e)}")
    
    # Posiciones por defecto
    return [
        'Portero', 'Lateral Izquierdo', 'Lateral Derecho', 'Defensa Central',
        'Pivote', 'Mediocentro', 'Mediocentro Defensivo', 'Mediocentro Ofensivo',
        'Interior Izquierdo', 'Interior Derecho', 'Extremo Izquierdo', 'Extremo Derecho',
        'Mediapunta', 'Delantero Centro', 'Segundo Delantero'
    ]

# ====================================
# PÁGINA: NUEVO INFORME
# ====================================

def show_new_report_page():
    """Muestra el formulario para crear un nuevo informe"""
    st.title("Nuevo Informe de Jugador")
    
    # Cargar posiciones
    posiciones = load_positions()
    
    with st.form("nuevo_informe_form"):
        # 1. INFORMACIÓN GENERAL
        st.header("1. INFORMACIÓN GENERAL")
        
        # Primera fila (3 columnas)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            jugador = st.text_input("Nombre del jugador*")
            edad = st.number_input("Edad*", min_value=16, max_value=45, step=1, value=16)
            talla = st.number_input("Talla (cm)*", min_value=150, max_value=220, step=1, value=180)
            posicion_principal = st.selectbox("Posición principal*", [""] + posiciones)
            
        with col2:
            club_actual = st.text_input("Club actual*")
            liga = st.text_input("Liga*")
            pie = st.selectbox("Pie hábil*", ["", "Derecho", "Izquierdo", "Ambidiestro"])
            posicion_secundaria = st.selectbox("Posición secundaria", ["No especificada"] + posiciones)
            
        with col3:
            nacionalidad = st.text_input("Nacionalidad*")
            agente = st.text_input("Agente")
            telefono_agente = st.text_input("Teléfono de agente")
        
        # Segunda fila (3 columnas)
        col4, col5, col6 = st.columns([1, 1, 2])
        
        with col4:
            fecha_nacimiento = st.number_input("Año nacimiento", min_value=1950, max_value=2010, step=1, value=1990)
        
        with col5:
            fin_contrato = st.number_input("Año fin contrato", min_value=2024, max_value=2035, step=1, value=2025)
        
        with col6:
            # Widget para subir imagen
            uploaded_file = st.file_uploader("Foto del jugador", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                # Mostrar vista previa de la imagen
                st.image(uploaded_file, caption='Vista previa', width=150)
        
        # Descripción general
        descripcion_general = st.text_area("Descripción general", height=100)
        
        # 2. EVALUACIÓN ESPECÍFICA
        st.markdown("---")
        st.header("2. EVALUACIÓN ESPECÍFICA")
        
        # Primera fila de evaluaciones (3 columnas)
        col6, col7, col8 = st.columns(3)
        
        with col6:
            rendimiento = st.slider("Rendimiento actual", 1, 6, 1)
        
        with col7:
            potencial = st.slider("Potencial de crecimiento", 1, 6, 1)
        
        with col8:
            adaptabilidad = st.slider("Adaptabilidad al equipo", 1, 6, 1)
        
        # Segunda fila (4 columnas para evaluaciones detalladas)
        st.markdown("### Evaluaciones detalladas (1-6)")
        
        col9, col10, col11, col12 = st.columns(4)
        
        with col9:
            evaluacion_tecnica = st.slider("Técnica", 1, 6, 1, key="tecnica")
            obs_tecnica = st.text_area("Obs. técnicas", height=60, key="obs_tecnica")
        
        with col10:
            evaluacion_tactica = st.slider("Táctica", 1, 6, 1, key="tactica")
            obs_tactica = st.text_area("Obs. tácticas", height=60, key="obs_tactica")
        
        with col11:
            evaluacion_fisica = st.slider("Físico", 1, 6, 1, key="fisica")
            obs_fisica = st.text_area("Obs. físicas", height=60, key="obs_fisica")
        
        with col12:
            evaluacion_mental = st.slider("Mental", 1, 6, 1, key="mental")
            obs_mental = st.text_area("Obs. mentales", height=60, key="obs_mental")
        
        # 3. REFERENCIAS
        st.markdown("---")
        st.header("3. REFERENCIAS")
        referencias = st.text_area("Referencias adicionales", height=100)
        
        # 4. HISTORIAL Y ESTADO DE LESIONES
        st.markdown("---")
        st.header("4. HISTORIAL Y ESTADO DE LESIONES")
        
        # Historial de lesiones
        historial_lesiones = st.text_area("Detalle el historial de lesiones", height=100)
        
        # Estado de lesiones
        estado_lesiones = st.selectbox(
            "Estado de lesiones",
            ["NO", "REVISAR", "ÚLTIMOS 3 AÑOS LESIONES RELEVANTES"]
        )
        
        # 5. VEREDICTO FINAL
        st.markdown("---")
        st.header("5. VEREDICTO FINAL")
        
        # Veredicto final
        veredicto = st.radio(
            "Veredicto final:",
            [
                "FIRMAR – Mejora plantilla", 
                "SEGUIR DE CERCA – Nivel de plantilla", 
                "SEGUIR – Complemento de plantilla", 
                "NO INTERESA – No cumple con los requisitos"
            ]
        )
        
        # Botón de envío
        submitted = st.form_submit_button("💾 Guardar Jugador", use_container_width=True)
        
        if submitted:
            # Validar campos obligatorios
            campos_obligatorios = {
                "Nombre del jugador": jugador,
                "Edad": edad,
                "Talla": talla,
                "Posición principal": posicion_principal,
                "Club actual": club_actual,
                "Pie hábil": pie,
                "Nacionalidad": nacionalidad
            }
            
            campos_faltantes = [campo for campo, valor in campos_obligatorios.items() if not valor]
            
            if campos_faltantes:
                st.error(f"Por favor complete los siguientes campos obligatorios: {', '.join(campos_faltantes)}")
            else:
                # Crear diccionario con los datos del jugador
                jugador_data = {
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "jugador": jugador,
                    "edad": edad,
                    "liga": liga,
                    "talla": talla,
                    "fecha_nacimiento": fecha_nacimiento,
                    "nacionalidad": nacionalidad,
                    "pie": pie,
                    "club_actual": club_actual,
                    "fin_contrato": fin_contrato,
                    "agente": agente if agente else "",
                    "telefono_agente": telefono_agente if telefono_agente else "",
                    "posicion_principal": posicion_principal,
                    "posicion_secundaria": posicion_secundaria if posicion_secundaria != "No especificada" else "",
                    "descripcion_general": descripcion_general,
                    "rendimiento": rendimiento,
                    "potencial": potencial,
                    "adaptabilidad": adaptabilidad,
                    "evaluacion_tecnica": evaluacion_tecnica,
                    "evaluacion_tactica": evaluacion_tactica,
                    "evaluacion_fisica": evaluacion_fisica,
                    "evaluacion_mental": evaluacion_mental,
                    "observaciones_tecnica": obs_tecnica,
                    "observaciones_tactica": obs_tactica,
                    "observaciones_fisica": obs_fisica,
                    "observaciones_mental": obs_mental,
                    "referencias": referencias,
                    "historial_lesiones": historial_lesiones,
                    "estado_lesiones": estado_lesiones,
                    "veredicto": veredicto
                }
                
                # Guardar los datos del jugador
                if save_player(jugador_data, uploaded_file):
                    st.success("¡Jugador guardado correctamente!")
                    st.balloons()
                else:
                    st.error("Ocurrió un error al guardar el jugador. Por favor, intente nuevamente.")

# PÁGINA: BASE DE DATOS JUGADORES
# ====================================

def generate_pdf_report(jugador_data):
    """Genera un PDF con la información del jugador usando el generador mejorado"""
    try:
        # Crear archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            output_path = tmp_file.name
        
        # Generar el PDF usando el generador mejorado
        success, error_message = generate_player_pdf(jugador_data, output_path)
        
        if not success:
            raise Exception(error_message)
            
        return output_path
        
    except Exception as e:
        st.error(f"Error al generar el PDF: {str(e)}")
        return None

def create_download_button(pdf_file):
    """Crea un botón de descarga para el PDF"""
    if not pdf_file or not os.path.exists(pdf_file):
        st.error("No se pudo generar el archivo PDF")
        return
        
    try:
        with open(pdf_file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # Crear un nombre de archivo más amigable
        player_name = pdf_file.split('_')[-1].replace('.pdf', '')
        download_filename = f"Informe_{player_name}.pdf"
        
        # Botón de descarga con estilo mejorado
        st.markdown(
            f'''
            <a href="data:application/octet-stream;base64,{base64_pdf}" 
               download="{download_filename}"
               style="
                   display: inline-block;
                   padding: 0.5em 1em;
                   background-color: #0d6efd;
                   color: white;
                   text-decoration: none;
                   border-radius: 5px;
                   font-weight: bold;
                   text-align: center;
                   margin: 10px 0;
               ">
                📥 Descargar Informe PDF
            </a>
            ''',
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Error al preparar la descarga: {str(e)}")
    finally:
        # Limpiar archivo temporal
        try:
            os.remove(pdf_file)
        except Exception as e:
            print(f"Error al eliminar archivo temporal: {e}")

def show_database_page():
    st.title("📊 BASE DE DATOS JUGADORES")
    
    # Cargar datos
    if not os.path.exists(DATABASE_FILE):
        st.warning("No se encontró la base de datos de jugadores. Por favor, cree al menos un informe.")
        return
        
    df = pd.read_csv(DATABASE_FILE)
    
    # Verificar si el DataFrame está vacío
    if df.empty:
        st.info("No hay jugadores registrados en la base de datos.")
        return
    
    # Filtros de búsqueda
    st.subheader("Filtros de Búsqueda")
    
    # Crear columnas para los filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filtro por liga (asumiendo que hay una columna 'liga' en el DataFrame)
        ligas = ["Todas"] + sorted(df['liga'].dropna().unique().tolist()) if 'liga' in df.columns else ["Todas"]
        liga_seleccionada = st.selectbox("Liga:", ligas, key="filtro_liga")
        
    with col2:
        # Filtro por equipo
        equipos = ["Todos"] + sorted(df['club_actual'].dropna().unique().tolist())
        equipo_seleccionado = st.selectbox("Equipo:", equipos, key="filtro_equipo")
        
    with col3:
        # Filtro por posición
        posiciones = ["Todas"] + sorted(df['posicion_principal'].dropna().unique().tolist())
        posicion_seleccionada = st.selectbox("Posición:", posiciones, key="filtro_posicion")
        
    with col4:
        # Filtro por nacionalidad
        nacionalidades = ["Todas"] + sorted(df['nacionalidad'].dropna().unique().tolist())
        nacionalidad_seleccionada = st.selectbox("Nacionalidad:", nacionalidades, key="filtro_nacionalidad")
    
    # Filtro por nombre (búsqueda)
    busqueda_nombre = st.text_input("Buscar por nombre:", "", key="busqueda_nombre")
    
    # Aplicar filtros al DataFrame
    df_filtrado = df.copy()
    
    if liga_seleccionada != "Todas" and 'liga' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['liga'] == liga_seleccionada]
        
    if equipo_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['club_actual'] == equipo_seleccionado]
        
    if posicion_seleccionada != "Todas":
        df_filtrado = df_filtrado[
            (df_filtrado['posicion_principal'] == posicion_seleccionada) |
            (df_filtrado['posicion_secundaria'] == posicion_seleccionada)
        ]
        
    if nacionalidad_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['nacionalidad'] == nacionalidad_seleccionada]
        
    if busqueda_nombre:
        df_filtrado = df_filtrado[
            df_filtrado['jugador'].str.contains(busqueda_nombre, case=False, na=False)
        ]
    
    # Mostrar selector de jugador con la lista filtrada
    jugadores = [""] + sorted(df_filtrado['jugador'].dropna().unique().tolist())
    jugador_seleccionado = st.selectbox("Seleccionar jugador:", jugadores, key="jugador_selector")
    
    if jugador_seleccionado:
        jugador = df[df['jugador'] == jugador_seleccionado].iloc[0].to_dict()
        
        # Botón para generar PDF
        if st.button("🖨️ IMPRIMIR INFORME EN PDF", key="generar_pdf_btn"):
            with st.spinner('Generando informe PDF...'):
                pdf_file = generate_pdf_report(jugador)
                if pdf_file:
                    create_download_button(pdf_file)
        
        # Mostrar la información del jugadores según el veredicto
        veredicto = jugador.get('veredicto', '').upper()
        if "FIRMAR" in veredicto:
            st.success(f"## {jugador['jugador']} - {veredicto}")
        elif "SEGUIR DE CERCA" in veredicto:
            st.info(f"## {jugador['jugador']} - {veredicto}")
        elif "SEGUIR" in veredicto and "CERCA" not in veredicto:
            st.warning(f"## {jugador['jugador']} - {veredicto}")
        elif "NO INTERESA" in veredicto:
            st.error(f"## {jugador['jugador']} - {veredicto}")
        else:
            st.write(f"## {jugador['jugador']} - {veredicto}")
        
        # Crear layout de 4 columnas: Imagen + 3 columnas de información
        col_img, col_info, col_club, col_pos = st.columns([1, 2, 2, 2])
        
        # Columna 1: Imagen del jugador
        with col_img:
            # Obtener la ruta de la imagen del CSV
            img_path = str(jugador.get('imagen_path', '')).strip()
            
            # Si la ruta está vacía, usar None
            if not img_path or pd.isna(img_path):
                valid_path = None
                img_url = None
            else:
                # Obtener el directorio base de la aplicación
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Construir la ruta completa
                full_path = os.path.join(base_dir, img_path)
                
                # Verificar si la ruta existe
                valid_path = full_path if os.path.exists(full_path) else None
                img_url = img_path  # Usar la ruta relativa para la URL
            
            # Debug: Mostrar información de la ruta (oculto)
            if False:  # Cambiar a True para depuración
                debug_info = f"""
                <div style='display: none;'>
                    Ruta del CSV: {img_path}<br>
                    Ruta completa: {full_path if 'full_path' in locals() else 'N/A'}<br>
                    ¿Existe?: {'Sí' if valid_path else 'No'}<br>
                    Directorio actual: {os.getcwd()}
                </div>
                """
                st.markdown(debug_info, unsafe_allow_html=True)
            
            # Usar la ruta válida si se encontró alguna
            if valid_path:
                # Usar st.image con formato circular
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    # Crear un contenedor circular con CSS
                    st.markdown(
                        """
                        <style>
                        .circular-image {
                            width: 150px;
                            height: 150px;
                            border-radius: 50%;
                            overflow: hidden;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                            margin: 0 auto 10px auto;
                            background: #f0f0f0;
                        }
                        .circular-image img {
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Mostrar la imagen usando st.image con base64
                    try:
                        import base64
                        
                        def get_image_base64(path):
                            with open(path, 'rb') as img_file:
                                return base64.b64encode(img_file.read()).decode('utf-8')
                        
                        # Convertir la imagen a base64
                        img_base64 = get_image_base64(img_path)
                        
                        # Mostrar la imagen con HTML
                        st.markdown(
                            f"""
                            <div style='width: 150px; height: 150px; border-radius: 50%; overflow: hidden; 
                                         margin: 0 auto 10px auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                                <img src='data:image/png;base64,{img_base64}' 
                                     style='width: 100%; height: 100%; object-fit: cover;' 
                                     alt='{jugador['jugador']}'>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    except Exception as e:
                        st.error(f"Error al cargar la imagen: {str(e)}")
                        # Mostrar placeholder en caso de error
                        st.markdown(
                            f"""
                            <div style='width: 150px; height: 150px; border-radius: 50%; overflow: hidden; 
                                         margin: 0 auto 10px auto; background: #f0f0f0; display: flex; 
                                         align-items: center; justify-content: center;'>
                                <div style='font-size: 40px; color: #999;'>👤</div>
                            </div>
                            <h4 style='text-align: center; margin: 5px 0;'>{jugador['jugador']}</h4>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                # Mostrar placeholder si no hay imagen
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;'>
                        <div style='width: 150px; height: 150px; border-radius: 50%; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
                                     margin-bottom: 10px; background: #f0f0f0; display: flex; align-items: center; justify-content: center;'>
                            <div style='font-size: 40px; color: #999;'>👤</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Columna 2: Información Personal
        with col_info:
            with st.container():
                st.markdown("### 📋 Información Personal")
                st.markdown(
                    f"<div style='background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 15px; height: 100%;'>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>📅</span> <strong>Edad:</strong> {jugador.get('edad', 'No especificada')} años</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>{'🇦🇷' if 'argen' in str(jugador.get('nacionalidad', '')).lower() else '🌐'}</span> <strong>Nacionalidad:</strong> {jugador.get('nacionalidad', 'No especificada')}</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>⚽</span> <strong>Pie hábil:</strong> {jugador.get('pie', 'No especificado')}</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>📏</span> <strong>Talla:</strong> {jugador.get('talla', 'No especificada')} cm</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        
        # Columna 3: Club y Contrato
        with col_club:
            with st.container():
                st.markdown("### ⚽ Club y Contrato")
                st.markdown(
                    f"<div style='background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 15px; height: 100%;'>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>👕</span> <strong>Club actual:</strong> {jugador.get('club_actual', 'Sin club')}</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>🏆</span> <strong>Liga:</strong> {jugador.get('liga', 'No especificada')}</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>📅</span> <strong>Fin de contrato:</strong> {jugador.get('fin_contrato', 'No especificado')}</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>👤</span> <strong>Agente:</strong> {jugador.get('agente', 'No especificado')}</div>"
                    f"<div style='margin: 8px 0;'><span style='font-size: 20px;'>📞</span> <strong>Teléfono:</strong> {jugador.get('telefono_agente', 'No especificado')}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        
        # Columna 4: Posiciones
        with col_pos:
            with st.container():
                st.markdown("### 🏷️ Posiciones")
                st.markdown(
                    f"<div style='background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 15px; height: 100%;'>"
                    f"<div style='margin: 15px 0;'><span style='font-size: 20px;'>⭐</span> <strong>Principal:</strong><br>{jugador.get('posicion_principal', 'No especificada')}</div>"
                    f"<div style='margin: 15px 0;'><span style='font-size: 20px;'>🔹</span> <strong>Secundaria:</strong><br>{jugador.get('posicion_secundaria', 'No especificada')}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        
        st.divider()
        
        st.divider()
        
        # ====================================
        # SECCIÓN: ANÁLISIS DETALLADO
        # ====================================
        st.header("Análisis Detallado")
        
        # Calcular evaluación AUDAX
        
        # Sección 4 - Evaluación AUDAX
        st.divider()
        
        # Calcular evaluación AUDAX: ((Rendimiento + Potencial + Adaptabilidad) / 18) * 10
        rendimiento = float(jugador.get('rendimiento', 0)) if jugador.get('rendimiento') else 0
        potencial = float(jugador.get('potencial', 0)) if jugador.get('potencial') else 0
        adaptabilidad = float(jugador.get('adaptabilidad', 0)) if jugador.get('adaptabilidad') else 0
        
        # Asegurarse de que los valores estén en el rango correcto (0-10)
        rendimiento = max(0, min(10, rendimiento))
        potencial = max(0, min(10, potencial))
        adaptabilidad = max(0, min(10, adaptabilidad))
        
        # Calcular puntuación AUDAX según la fórmula ((R + P + A) / 18) * 10
        suma_valores = rendimiento + potencial + adaptabilidad
        puntuacion_audax = (suma_valores / 18) * 10
        puntuacion_audax = max(0, min(10, puntuacion_audax))  # Asegurar que esté entre 0 y 10
        
        # Crear layout horizontal para la evaluación AUDAX y métricas
        col_audax, col_metrics = st.columns([2, 3])
        
        with col_audax:
            # Mostrar evaluación AUDAX
            st.markdown("### 📊 Evaluación AUDAX")
            st.markdown(f"**Puntuación: {puntuacion_audax:.1f}/10**")
            st.markdown(
                f"<div style='height: 24px; width: 100%; background: #f0f2f6; border-radius: 12px; margin: 5px 0;'>"
                f"<div style='height: 100%; width: {puntuacion_audax * 10}%; background: #1f77b4; border-radius: 12px; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: bold;'>{puntuacion_audax:.1f}</div>"
                f"</div>"
                f"<div style='font-size: 0.9em; color: #666; margin-bottom: 10px;'>"
                f"(({rendimiento} + {potencial} + {adaptabilidad}) / 18) × 10 = {puntuacion_audax:.1f}"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with col_metrics:
            # Función para obtener la descripción según el valor
            def get_metric_description(tipo, valor):
                valor = int(round(valor))
                if tipo == 'rendimiento':
                    descripciones = [
                        "Muy por debajo del nivel de 1ª división de Chile.",
                        "Jugador de rol en equipos débiles de 1ª división o válido para 2ª división.",
                        "Cumple en equipos de media tabla baja en 1ª división de Chile o ligas equivalentes.",
                        "Buen rendimiento en 1ª división de Chile / titular fiable en Sudamérica competitiva.",
                        "Jugador diferencial en Sudamérica o titular en ligas europeas secundarias.",
                        "Rendimiento top nivel europeo, listo para competir en ligas Big 5 y torneos internacionales."
                    ]
                    return descripciones[valor-1] if 1 <= valor <= 6 else 'N/A'
                elif tipo == 'potencial':
                    descripciones = [
                        "No da nivel para 1ª división de Chile.",
                        "Jugador válido solo para ligas menores sudamericanas o 2ª división.",
                        "Jugador de nivel bajo/medio en 1ª división de Chile o ligas similares.",
                        "Jugador sólido en 1ª división de Chile / competitivo en ligas top sudamericanas.",
                        "Jugador con nivel para destacar en Sudamérica y con proyección de salto a ligas europeas secundarias.",
                        "Jugador con potencial claro para ligas top de Europa y competiciones internacionales."
                    ]
                    return descripciones[valor-1] if 1 <= valor <= 6 else 'N/A'
                else:  # adaptabilidad
                    descripciones = [
                        "Adaptación muy complicada: limitaciones de mentalidad, idioma o carácter.",
                        "Adaptación lenta, con riesgo de bajo rendimiento fuera de Sudamérica.",
                        "Adaptación posible con acompañamiento y tiempo de aclimatación.",
                        "Adaptación rápida en ligas sudamericanas y progresiva en Europa.",
                        "Adaptación sólida a corto plazo incluso en contextos europeos exigentes.",
                        "Adaptación inmediata: mentalidad profesional, sin barreras de idioma/cultura."
                    ]
                    return descripciones[valor-1] if 1 <= valor <= 6 else 'N/A'
            
            # Crear 3 columnas para las métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                valor = int(round(rendimiento))
                st.metric("RENDIMIENTO", f"{valor}")
                st.caption(get_metric_description('rendimiento', rendimiento))
                
            with col2:
                valor = int(round(potencial))
                st.metric("POTENCIAL", f"{valor}")
                st.caption(get_metric_description('potencial', potencial))
                
            with col3:
                valor = int(round(adaptabilidad))
                st.metric("ADAPTABILIDAD", f"{valor}")
                st.caption(get_metric_description('adaptabilidad', adaptabilidad))
        
        
        # Sección 5 - Evaluaciones Técnicas
        st.divider()
        st.markdown("### ⚙️ Evaluaciones Técnicas")
        
        # Crear 4 columnas para las evaluaciones
        col1, col2, col3, col4 = st.columns(4)
        
        # Función para crear una tarjeta de evaluación
        def crear_tarjeta_evaluacion(col, titulo, valor, observaciones):
            with col:
                st.markdown(f"**{titulo}**")
                # Barra de progreso personalizada
                st.markdown(
                    f"<div style='height: 20px; width: 100%; background: #f0f2f6; border-radius: 10px; margin: 5px 0;'>"
                    f"<div style='height: 100%; width: {(valor/6)*100}%; background: #1f77b4; border-radius: 10px;'></div>"
                    f"</div>"
                    f"<div style='text-align: center; font-weight: bold;'>{valor}/6</div>",
                    unsafe_allow_html=True
                )
                if observaciones and str(observaciones).lower() != 'nan':
                    st.caption(f"*{observaciones}*")
        
        # Mostrar cada evaluación en su columna correspondiente
        crear_tarjeta_evaluacion(
            col1, 
            "Técnica", 
            int(jugador.get('evaluacion_tecnica', 0)), 
            jugador.get('observaciones_tecnica', '')
        )
        
        crear_tarjeta_evaluacion(
            col2, 
            "Táctica", 
            int(jugador.get('evaluacion_tactica', 0)), 
            jugador.get('observaciones_tactica', '')
        )
        
        crear_tarjeta_evaluacion(
            col3, 
            "Física", 
            int(jugador.get('evaluacion_fisica', 0)), 
            jugador.get('observaciones_fisica', '')
        )
        
        crear_tarjeta_evaluacion(
            col4, 
            "Mental", 
            int(jugador.get('evaluacion_mental', 0)), 
            jugador.get('observaciones_mental', '')
        )
        
        # ====================================
        # SECCIÓN: CONCLUSIONES
        # ====================================
        st.divider()
        st.subheader("📝 CONCLUSIONES")
        
        # Obtener datos del jugador
        descripcion = jugador.get('descripcion_general', 'Sin información disponible')
        historial = jugador.get('historial_medico', 'Sin información disponible')
        referencias = jugador.get('referencias_adicionales', 'Sin información disponible')
        
        # Crear 3 columnas
        col1, col2, col3 = st.columns(3)
        
        # Columna 1: Descripción General
        with col1:
            st.markdown("**Descripción General**")
            st.info(
                f"{descripcion if pd.notna(descripcion) and str(descripcion).lower() != 'nan' else 'Sin información disponible'}",
                icon="ℹ️"
            )
        
        # Columna 2: Historial Médico
        with col2:
            st.markdown("**Historial Médico**")
            st.warning(
                f"{historial if pd.notna(historial) and str(historial).lower() != 'nan' else 'Sin información disponible'}",
                icon="⚠️"
            )
        
        # Columna 3: Referencias Adicionales
        with col3:
            st.markdown("**Referencias Adicionales**")
            st.info(
                f"{referencias if pd.notna(referencias) and str(referencias).lower() != 'nan' else 'Sin información disponible'}",
                icon="📌"
            )
        
        st.divider()

# ====================================
# FUNCIÓN PRINCIPAL
# ====================================

def get_image_base64(image_path):
    import base64
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def main():
    # Sidebar para navegación
    try:
        audax_logo = get_image_base64("AudaxEscudo.png")
        liga_logo = get_image_base64("ligachile1.png")
        st.sidebar.markdown(f'<img src="data:image/png;base64,{audax_logo}" width="80">', unsafe_allow_html=True)
    except Exception as e:
        st.sidebar.error("Error cargando logos")
        
    st.sidebar.title("Navegación")
    page = st.sidebar.selectbox(
        "Seleccione una página:",
        ["NUEVO INFORME", "BASE DE DATOS JUGADORES"]
    )
    
    # Header principal
    try:
        st.markdown(f"""
            <div style='background-color: #0d6efd; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div style='width: 80px;'>
                        <img src='data:image/png;base64,{audax_logo}' style='height: 80px; width: auto;'/>
                    </div>
                    <div style='text-align: center;'>
                        <h1 style='margin: 0; padding: 0; font-size: 1.8rem;'>SISTEMA DE SCOUTING PROFESIONAL</h1>
                        <h2 style='margin: 5px 0 0 0; padding: 0; font-size: 1.4rem;'>AUDAX ITALIANO</h2>
                        <h3 style='margin: 5px 0 0 0; padding: 0; font-size: 1.1rem;'>DIRECCIÓN DEPORTIVA</h3>
                    </div>
                    <div style='width: 80px;'>
                        <img src='data:image/png;base64,{liga_logo}' style='height: 80px; width: auto;'/>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Error al cargar las imágenes del encabezado")
    
    # Mostrar la página correspondiente
    if page == "NUEVO INFORME":
        show_new_report_page()
    elif page == "BASE DE DATOS JUGADORES":
        show_database_page()

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
