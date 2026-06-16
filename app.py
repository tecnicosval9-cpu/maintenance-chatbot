import streamlit as st
import requests
import json
import re
from sentence_transformers import SentenceTransformer
from groq import Groq

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA (PRIMERO)
# ============================================================
st.set_page_config(
    page_title="Maintenance Technical Assistant",
    page_icon="🔧",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a Bug': None,
        'About': None
    }
)

# ============================================================
# OCULTAR ELEMENTOS DE STREAMLIT (CSS + JS)
# ============================================================
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden; display: none;}
        footer {visibility: hidden; display: none;}
        header {visibility: hidden; display: none;}
        .stAppDeployButton {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stStatusWidget {display: none !important;}
        .stDecoration {display: none !important;}
        button[aria-label="Manage app"] {display: none !important;}
        button[kind="icon"] {display: none !important;}
        .viewerBadge_link__qRIov {display: none !important;}
        .viewerBadgeContainer__1w5xh {display: none !important;}
        .css-1n76uvr {display: none !important;}
        .css-1dp5vir {display: none !important;}
        .css-1v0mbdj {display: none !important;}
        .css-zq5wmm {display: none !important;}
        .egzxvld0 {display: none !important;}
        .st-emotion-cache-1v0mbdj {display: none !important;}
        .st-emotion-cache-zq5wmm {display: none !important;}
        .st-emotion-cache-16txtl3 {display: none !important;}
        footer * {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

hide_js = """
<script>
    function removeStreamlitBranding() {
        const selectors = [
            'footer', '.stAppDeployButton', '[data-testid="stToolbar"]',
            '.viewerBadgeContainer__1w5xh', '.viewerBadge_link__qRIov',
            '.css-1n76uvr', '.css-1dp5vir', '.css-1v0mbdj', '.css-zq5wmm',
            '.egzxvld0', '.st-emotion-cache-1v0mbdj', '.st-emotion-cache-zq5wmm',
            '.st-emotion-cache-16txtl3', '[class*="viewerBadge"]', '[class*="stAppDeploy"]'
        ];
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => el.remove());
        });
        
        document.querySelectorAll('*').forEach(el => {
            if (el.innerText && el.innerText.includes("Made with Streamlit")) {
                el.style.display = 'none';
            }
        });
    }
    document.addEventListener('DOMContentLoaded', removeStreamlitBranding);
    setTimeout(removeStreamlitBranding, 1000);
    setTimeout(removeStreamlitBranding, 3000);
</script>
"""
st.markdown(hide_js, unsafe_allow_html=True)

# ============================================================
# CONFIGURACIÓN
# ============================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

GOOGLE_DRIVE_MAIN = "https://drive.google.com/drive/folders/1h5X-ma9-dt2_HszTlxpcJNKdA9KILFeY"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# ============================================================
# ENLACES DIRECTOS A CARPETAS DE MÁQUINAS
# ============================================================

CARPETAS_MAQUINAS = {
    "IMM_28_174797": "https://drive.google.com/drive/folders/17AARDP7zNXwo8Ya0KkneP4o5xvlXWbSf?usp=drive_link",
    "IMM_35_179349": "https://drive.google.com/drive/folders/1OxXpwL2Kl8sis88rRv3QnJi4uoWvM36H?usp=drive_link",
    "IMM_40_179843": "https://drive.google.com/drive/folders/1Uye_LZsSvAQBxx4XIgkG0TfX5qTtFVP3?usp=drive_link",
    "IMM_43_183868": "https://drive.google.com/drive/folders/16QFrpDALtCC9A75u9UFOsR7r_12N3gl8?usp=drive_link",
    "IMM_47_187368": "https://drive.google.com/drive/folders/1bm7T8iulPI2yEAL2Rk4wM70j6b7jj3Vh?usp=drive_link",
    "IMM_53_201450": "https://drive.google.com/drive/folders/1lMcQSfK9mlPsLXIpITmPxcqPomUTmWRi?usp=drive_link",
    "IMM_54_201448": "https://drive.google.com/drive/folders/1h1BU6AfMn5uGoe80oj2KBBth_tUx363f?usp=drive_link",
    "IMM_67_218187": "https://drive.google.com/drive/folders/1qECnF7MLRxobLVHCsFOTcs-3oU17CCOM?usp=drive_link",
    "IMM_68_217893": "https://drive.google.com/drive/folders/1SxR2bSC7SkW_jC1BRa_v3cl1GvwOHly1?usp=drive_link",
    "IMM_72_219827": "https://drive.google.com/drive/folders/1L731Mt6prgpXrxAAM6F9kG3RPYwHr8ts?usp=drive_link",
    "IMM_76_235283": "https://drive.google.com/drive/folders/15i7LttkO9Y6H7JuDDRpJQVJ3vIddVM0k?usp=drive_link",
    "IMM_80_255210": "https://drive.google.com/drive/folders/1FCJsMbIgM0tDVLx4YzAeNMQ5CyB67XHG?usp=drive_link",
    "IMM_82_261098": "https://drive.google.com/drive/folders/1PBbnEWic_wNG6cP7blXDmTG8xvc924Ei?usp=drive_link",
    "ROBOT_IMM_39_179848": "https://drive.google.com/drive/folders/1csTol73E-hGdE6xDHO-g5XsUam-Uyexb?usp=drive_link",
    "ROBOT_IMM_40 179849": "https://drive.google.com/drive/folders/1j7OXGSNmJiklo6BBHTNDRS0Qled86w75?usp=drive_link",
    "ROBOT_IMM_47_187382": "https://drive.google.com/drive/folders/17Q7gXk2lpH09KXiLBkeLbCEQmlWchcsm?usp=drive_link",
    "ROBOT_IMM_53_201614": "https://drive.google.com/drive/folders/10NR_2FSI-e28pB7PJyPaHN7ojuA53AbG?usp=drive_link",
    "ROBOT_IMM_54_201615": "https://drive.google.com/drive/folders/1u-BCIJrr85xhoscXLkUvmC21NuejUDlf?usp=drive_link",
    "ROBOT_IMM_72_219830": "https://drive.google.com/drive/folders/1fwX2b1WmcjFTkrLnl9rDwis7tSosHNL6?usp=drive_link",
    "ROBOT_IMM_76": "https://drive.google.com/drive/folders/1nUSmKmeHdxhPAsXgZImWbaCmppF2EN1B?usp=drive_link",
    "ROBOT_IMM_79_197063": "https://drive.google.com/drive/folders/1xP4leLMIN-uj-PEUGFz_Q2UCU3FMlVWz?usp=drive_link",
    "ROBOT_IMM_82_261257": "https://drive.google.com/drive/folders/1aG6iUhIWz6UiROVzxq9fNqrS5235m2jy?usp=drive_link",
}

# ============================================================
# MAPEO DE NÚMEROS A MÁQUINAS
# ============================================================

MAQUINAS_IMM = {
    "28": "IMM_28_174797",
    "35": "IMM_35_179349",
    "40": "IMM_40_179843",
    "43": "IMM_43_183868",
    "47": "IMM_47_187368",
    "53": "IMM_53_201450",
    "54": "IMM_54_201448",
    "67": "IMM_67_218187",
    "68": "IMM_68_217893",
    "72": "IMM_72_219827",
    "76": "IMM_76_235283",
    "80": "IMM_80_255210",
    "82": "IMM_82_261098",
}

MAQUINAS_ROBOT = {
    "39": "ROBOT_IMM_39_179848",
    "40": "ROBOT_IMM_40 179849",
    "47": "ROBOT_IMM_47_187382",
    "53": "ROBOT_IMM_53_201614",
    "54": "ROBOT_IMM_54_201615",
    "72": "ROBOT_IMM_72_219830",
    "76": "ROBOT_IMM_76",
    "79": "ROBOT_IMM_79_197063",
    "82": "ROBOT_IMM_82_261257",
}

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

@st.cache_resource
def load_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def expandir_pregunta(pregunta):
    """Expande la pregunta con sinónimos en diferentes idiomas"""
    sinónimos = {
        "vacuum": ["vakuum", "vacío", "aspiración", "succión", "vacio"],
        "pressure": ["druck", "presión", "presion", "press", "pression"],
        "temperature": ["temperatur", "temperatura", "temp"],
        "error": ["fehler", "fallo", "código", "code", "fout", "errore"],
        "speed": ["geschwindigkeit", "velocidad", "velocity", "vitesse"],
        "velocity": ["geschwindigkeit", "velocidad", "speed", "vitesse"],
        "ajustar": ["adjust", "einstellen", "ajuste", "configurar", "set", "modificar", "ändern", "anpassen"],
        "perfil": ["profile", "profil", "perfil de velocidad", "velocity profile", "geschwindigkeitsprofil"],
        "carrera": ["stroke", "hub", "carrera", "posicion", "position"],
        "valve": ["ventil", "válvula", "valvula", "valve"],
        "pump": ["pumpe", "bomba", "pump"],
        "axis": ["achse", "eje", "axis", "asse"],
        "calibrate": ["kalibrieren", "calibrar", "calibration", "kalibrierung", "calibración"],
        "aprender": ["learn", "lernen", "estudiar", "study", "capacitación", "training", "formación", "education"],
        "operar": ["operate", "bedienen", "funcionamiento", "operation", "betrieb", "manejar", "usar", "utilizar", "manejo", "operación"],
        "manual": ["handbuch", "guide", "guía", "instrucciones", "instructions", "anleitung"],
        "seguro": ["safety", "sicherheit", "seguridad", "protección", "guard", "schutz"],
        "cierre": ["closing", "schließen", "cierre", "lock", "verriegelung", "schloss"],
        "hidraulico": ["hydraulic", "hydraulik", "hidráulico", "oil", "aceite", "hydraulisch"],
        "cartridge": ["cartucho", "valvula", "valve", "ventil", "asiento", "kartusche"],
        "defectuoso": ["defective", "defekt", "falla", "error", "fehler", "störung"],
        "manguera": ["hose", "schlauch", "tubo", "conducción", "leitung"],
        "presión": ["pressure", "druck", "presion", "pression"],
        "válvula": ["valve", "ventil", "valvula", "valve"],
        "bloqueo": ["lock", "verriegelung", "bloqueo", "sperre", "block"],
    }
    
    pregunta_lower = pregunta.lower()
    palabras = pregunta_lower.split()
    
    for palabra, sinonimos_lista in sinónimos.items():
        if palabra in pregunta_lower:
            for sin in sinonimos_lista:
                palabras.append(sin)
    
    if "ajustar perfil de velocidad" in pregunta_lower:
        palabras.extend(["geschwindigkeitsprofil", "velocity profile", "ajuste de velocidad", "speed profile"])
    
    if "ajustar carrera" in pregunta_lower or "carrera" in pregunta_lower:
        palabras.extend(["stroke adjustment", "hub einstellen", "ajuste de carrera", "position", "posicion"])
    
    if "aprender" in pregunta_lower or "learn" in pregunta_lower:
        palabras.extend(["training", "capacitación", "curso", "manual", "guía", "tutorial", "handbuch", "anleitung"])
    
    if "operar" in pregunta_lower or "operate" in pregunta_lower:
        palabras.extend(["bedienung", "funcionamiento", "operation", "manejo", "usar", "utilizar"])
    
    if "seguro de cierre" in pregunta_lower:
        palabras.extend(["closing safety", "schließsicherheit", "cierre seguro", "lock safety", "verriegelungssicherheit"])
    
    if "cartridge" in pregunta_lower:
        palabras.extend(["kartusche", "cartucho", "valve cartridge", "ventil-kartusche"])
    
    return ' '.join(palabras)

def detectar_idioma_pregunta(pregunta):
    pregunta_lower = pregunta.lower()
    palabras_ingles = ['vacuum', 'pressure', 'temperature', 'valve', 'pump', 'error', 'how', 'what', 'is', 'the', 'speed', 'velocity', 'adjust', 'learn', 'operate', 'manual', 'safety', 'hydraulic', 'cartridge']
    palabras_aleman = ['vakuum', 'druck', 'temperatur', 'ventil', 'pumpe', 'fehler', 'wie', 'was', 'ist', 'der', 'geschwindigkeit', 'einstellen', 'lernen', 'bedienen', 'handbuch', 'sicherheit', 'hydraulik', 'kartusche']
    palabras_espanol = ['vacío', 'presión', 'temperatura', 'válvula', 'bomba', 'fallo', 'cómo', 'qué', 'es', 'el', 'velocidad', 'ajustar', 'carrera', 'aprender', 'operar', 'manual', 'seguro', 'hidraulico', 'cartucho']
    
    es_ingles = any(p in pregunta_lower for p in palabras_ingles)
    es_aleman = any(p in pregunta_lower for p in palabras_aleman)
    es_espanol = any(p in pregunta_lower for p in palabras_espanol)
    
    if es_ingles:
        return "ingles"
    elif es_aleman:
        return "aleman"
    elif es_espanol:
        return "espanol"
    return None

def extraer_numero_maquina(pregunta):
    """Extrae el número de máquina y detecta si es robot o IMM"""
    pregunta_limpia = ' '.join(pregunta.lower().split())
    
    es_robot = 'robot' in pregunta_limpia
    
    if es_robot:
        match = re.search(r'robot\s*(?:de\s*la\s*)?imm[^\d]*(\d+)', pregunta_limpia)
    else:
        match = re.search(r'imm[^\d]*(\d+)', pregunta_limpia)
    
    if match:
        return {"numero": match.group(1), "es_robot": es_robot}
    return None

def es_peticion_de_plano(pregunta):
    """Detecta si el usuario pide un plano o diagrama (incluye plurales)"""
    pregunta_limpia = ' '.join(pregunta.lower().split())
    palabras_clave = [
        'plano', 'diagrama', 'esquema', 'schematic', 'schema', 'eléctrico', 'electric',
        'pleno', 'planos', 'dibujo', 'circuito', 'electrical', 'wiring', 'layout',
        'diagramas', 'esquemas'
    ]
    return any(p in pregunta_limpia for p in palabras_clave)

def detectar_tipo_manual(pregunta):
    """Detecta qué tipo de manual está pidiendo el usuario (incluye plurales)"""
    pregunta_limpia = ' '.join(pregunta.lower().split())
    
    if 'manuales' in pregunta_limpia:
        if 'operacion' not in pregunta_limpia and 'operación' not in pregunta_limpia and \
           'tecnico' not in pregunta_limpia and 'técnico' not in pregunta_limpia and \
           'servicio' not in pregunta_limpia and 'mantenimiento' not in pregunta_limpia and \
           'operador' not in pregunta_limpia:
            return 'operador'
    
    tipos = {
        'operador': [
            'manual de operacion', 'manual de operación', 
            'operation manual', 'operating manual', 
            'manual del operador', 'operator manual',
            'manual de operador', 'operador manual',
            'manual del operario', 'operario manual',
            'manuales de operacion', 'manuales de operación',
            'manuales del operador', 'manuales de operador'
        ],
        'tecnico': [
            'manual tecnico', 'manual técnico', 'technical manual', 
            'manual de tecnico', 'tecnic manual',
            'manuales tecnicos', 'manuales técnicos'
        ],
        'servicio': [
            'manual de servicio', 'service manual', 'servicio manual', 
            'maintenance manual', 'reparacion', 'repair manual',
            'manual de mantenimiento',
            'manuales de servicio', 'manuales de mantenimiento'
        ]
    }
    
    for tipo, palabras in tipos.items():
        if any(p in pregunta_limpia for p in palabras):
            return tipo
    return None

def obtener_nombre_maquina(numero, es_robot):
    if es_robot:
        return MAQUINAS_ROBOT.get(numero)
    return MAQUINAS_IMM.get(numero)

def buscar_planos_por_nombre_exacto(nombre_maquina):
    nombre_codificado = nombre_maquina.replace(' ', '%20')
    url = f"{SUPABASE_URL}/rest/v1/documentos_engel?metadatos->>numero_serie=eq.{nombre_codificado}&metadatos->>tipo_documento=eq.diagrama_electrico&limit=10"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return []

def buscar_manual_por_tipo(numero_maquina, tipo_manual, es_robot):
    """Busca un manual específico por tipo, usando el nombre completo de la máquina"""
    
    if es_robot:
        nombre_completo = MAQUINAS_ROBOT.get(numero_maquina)
    else:
        nombre_completo = MAQUINAS_IMM.get(numero_maquina)
    
    if not nombre_completo:
        return []
    
    nombre_codificado = nombre_completo.replace(' ', '%20')
    
    url = f"{SUPABASE_URL}/rest/v1/documentos_engel?metadatos->>numero_serie=eq.{nombre_codificado}&metadatos->>tipo_documento=eq.{tipo_manual}&limit=10"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        resultados = response.json()
        resultados_filtrados = []
        for doc in resultados:
            metadatos = doc.get('metadatos', {})
            if isinstance(metadatos, str):
                try:
                    metadatos = json.loads(metadatos)
                except:
                    metadatos = {}
            if metadatos.get('numero_serie') == nombre_completo:
                resultados_filtrados.append(doc)
        return resultados_filtrados
    
    return []

def test_groq_directo():
    """Prueba directa de Groq"""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Responde SOLO con la palabra: OK"}],
            max_tokens=5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {str(e)[:100]}"

def generar_respuesta_con_ia(pregunta, resultados_supabase):
    """Usa Groq para generar una respuesta técnica basada EXCLUSIVAMENTE en los manuales"""
    
    contexto = ""
    if resultados_supabase:
        # Detectar si es resumen específico de un tema
        es_resumen_especifico = any(palabra in pregunta.lower() for palabra in [
            "resumen de", "resumen sobre", "resumen del", "resumen de los",
            "procedimientos de", "dispositivos de", "parámetros de", "seguridad de",
            "mantenimiento de", "configuración de"
        ])
        
        # Usar más fragmentos para temas específicos
        if es_resumen_especifico:
            num_fragmentos = 15
        else:
            es_resumen = any(palabra in pregunta.lower() for palabra in ["resumen", "descripción general", "visión general", "puntos principales"])
            num_fragmentos = 8 if es_resumen else 3
        
        for doc in resultados_supabase[:num_fragmentos]:
            texto = doc.get('texto', '')[:3000] if es_resumen_especifico else doc.get('texto', '')[:2000]
            if texto:
                metadatos = doc.get('metadatos', {})
                if isinstance(metadatos, str):
                    try:
                        metadatos = json.loads(metadatos)
                    except:
                        metadatos = {}
                num_serie = metadatos.get('numero_serie', 'N/A')
                tipo = metadatos.get('tipo_documento', 'N/A')
                pagina = metadatos.get('pagina', 'N/A')
                idioma = metadatos.get('idioma', 'desconocido')
                contexto += f"\n=== INICIO DE INFORMACIÓN DEL MANUAL ===\n"
                contexto += f"Fuente: {num_serie} - {tipo}, Página {pagina} (Idioma: {idioma})\n"
                contexto += f"Contenido:\n{texto}\n"
                contexto += f"=== FIN DE LA INFORMACIÓN DEL MANUAL ===\n"
    else:
        contexto = "No se encontró información en los manuales para esta consulta."
    
    # ============================================================
    # DEPURACIÓN - Mostrar contexto en logs
    # ============================================================
    print("\n" + "=" * 60)
    print("🔍 CONTEXTO ENVIADO A GROQ:")
    print("=" * 60)
    print(f"Pregunta: {pregunta}")
    print(f"Longitud del contexto: {len(contexto)} caracteres")
    print(f"Primeros 500 caracteres del contexto:\n{contexto[:500]}")
    if len(contexto) > 500:
        print(f"... (y {len(contexto)-500} caracteres más)")
    print("=" * 60 + "\n")
    
    # Detectar si es un resumen
    es_resumen = any(palabra in pregunta.lower() for palabra in ["resumen", "descripción general", "visión general", "puntos principales"])
    es_resumen_especifico = any(palabra in pregunta.lower() for palabra in [
        "resumen de", "resumen sobre", "resumen del", "resumen de los",
        "procedimientos de", "dispositivos de", "parámetros de", "seguridad de",
        "mantenimiento de", "configuración de"
    ])
    
    # ============================================================
    # PROMPT MEJORADO PARA RESUMENES ESPECÍFICOS
    # ============================================================
    if es_resumen_especifico:
        # Detectar el tema específico
        tema = "contenido del manual"
        if "mantenimiento" in pregunta.lower():
            tema = "procedimientos de mantenimiento"
        elif "seguridad" in pregunta.lower() or "dispositivos de seguridad" in pregunta.lower():
            tema = "dispositivos de seguridad"
        elif "parámetros" in pregunta.lower() or "configuraciones" in pregunta.lower():
            tema = "parámetros y configuraciones"
        elif "procedimientos" in pregunta.lower():
            tema = "procedimientos"
        elif "operación" in pregunta.lower() or "funcionamiento" in pregunta.lower():
            tema = "operación y funcionamiento"
        
        prompt = f"""Eres un asistente técnico experto en máquinas de inyección ENGEL.

La siguiente información ha sido EXTRAÍDA DIRECTAMENTE de los manuales de ENGEL.
Debes responder EXCLUSIVAMENTE usando esta información.

**TEMA ESPECÍFICO DEL RESUMEN:** {tema}

INFORMACIÓN DE LOS MANUALES (NO inventes nada fuera de esto):
{contexto}

Pregunta del técnico: {pregunta}

**INSTRUCCIONES PARA EL RESUMEN ESPECÍFICO:**

1. **IDIOMA:** Responde SIEMPRE en ESPAÑOL

2. **ENFOQUE:** Concéntrate EXCLUSIVAMENTE en {tema}. Ignora información no relacionada.

3. **ESTRUCTURA DEL RESUMEN ESPECÍFICO:**
   ## 📋 RESUMEN DE {tema.upper()} - IMM [número de máquina]

   ### 🔍 INFORMACIÓN ENCONTRADA
   [Lista toda la información relevante sobre el tema, organizada de forma lógica]

   ### 📍 UBICACIÓN EN EL MANUAL
   [Secciones o capítulos donde se encuentra esta información]

   ### ⚙️ DETALLES IMPORTANTES
   [Especificaciones, valores, procedimientos paso a paso]

   ### ⚠️ ADVERTENCIAS Y PRECAUCIONES
   [Precauciones de seguridad relacionadas con el tema]

4. **DETALLE:** Sé completo y exhaustivo. Si hay múltiples procedimientos o elementos, enuméralos.

5. **CITAS:** Al final, lista todas las fuentes consultadas con el formato:
   - (Máquina, Tipo, Página)

**Resumen específico basado en el manual:**"""
        
    elif es_resumen:
        prompt = f"""Eres un asistente técnico experto en máquinas de inyección ENGEL.

La siguiente información ha sido EXTRAÍDA DIRECTAMENTE de los manuales de ENGEL.
Debes responder EXCLUSIVAMENTE usando esta información.

INFORMACIÓN DE LOS MANUALES (NO inventes nada fuera de esto):
{contexto}

Pregunta del técnico: {pregunta}

**INSTRUCCIONES OBLIGATORIAS PARA EL RESUMEN:**

1. **IDIOMA:** Responde SIEMPRE en ESPAÑOL

2. **ESTRUCTURA DEL RESUMEN:**
   ## 📋 RESUMEN DEL MANUAL [nombre de la máquina]
   ### 🎯 PROPÓSITO DEL MANUAL
   ### 📑 CONTENIDO PRINCIPAL
   ### 🔧 PROCEDIMIENTOS DE MANTENIMIENTO
   ### 🛡️ DISPOSITIVOS DE SEGURIDAD
   ### ⚙️ PARÁMETROS CRÍTICOS
   ### ⚠️ ADVERTENCIAS IMPORTANTES

3. **DETALLE:** Sé completo y detallado

4. **CITAS:** Lista todas las fuentes consultadas

**Resumen basado en el manual:**"""
        
    else:
        prompt = f"""Eres un asistente técnico experto en máquinas de inyección ENGEL.

La siguiente información ha sido EXTRAÍDA DIRECTAMENTE de los manuales de ENGEL.
Debes responder EXCLUSIVAMENTE usando esta información.

INFORMACIÓN DE LOS MANUALES (NO inventes nada fuera de esto):
{contexto}

Pregunta del técnico: {pregunta}

**INSTRUCCIONES OBLIGATORIAS:**

1. **IDIOMA:** Responde SIEMPRE en ESPAÑOL
2. **RESPUESTA CLARA:** Organiza la información de forma lógica
3. **CITAS:** Usa el formato: (Máquina, Tipo, Página)
4. **SI NO ENCUENTRAS INFORMACIÓN:** Dilo claramente

Respuesta basada en el manual:"""
    
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """Eres un asistente experto en máquinas de inyección ENGEL.

**INSTRUCCIONES PRINCIPALES:**
1. Respondes EXCLUSIVAMENTE con información extraída de los manuales.
2. Si no está en el manual, lo dices claramente.
3. No inventas información.

**IDIOMA:**
- SIEMPRE respondes en ESPAÑOL
- Traduces correctamente los términos técnicos del alemán o inglés al español

**PARA RESUMENES ESPECÍFICOS:**
- Concéntrate en el tema solicitado
- Sé exhaustivo con la información disponible
- Organiza la información de forma lógica
- Cita todas las fuentes

**FORMATO PARA RESUMEN ESPECÍFICO:**
---
## 📋 RESUMEN DE [TEMA] - IMM [número]

### 🔍 INFORMACIÓN ENCONTRADA
[Contenido detallado]

### 📍 UBICACIÓN EN EL MANUAL
[Secciones o capítulos]

### ⚙️ DETALLES IMPORTANTES
[Especificaciones y procedimientos]

### ⚠️ ADVERTENCIAS
[Precauciones]

---
"""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500 if es_resumen_especifico else (2000 if es_resumen else 1000),
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al conectar con el asistente IA: {str(e)[:150]}\n\n📁 Por favor, consulta los manuales en Google Drive."

def buscar_en_supabase(pregunta, model, limit=5):
    info = extraer_numero_maquina(pregunta)
    
    # Detectar si es un resumen específico de un tema
    es_resumen_especifico = any(palabra in pregunta.lower() for palabra in [
        "resumen de", "resumen sobre", "resumen del", "resumen de los",
        "procedimientos de", "dispositivos de", "parámetros de", "seguridad de",
        "mantenimiento de", "configuración de"
    ])
    
    # Si es resumen específico, usar más fragmentos
    if es_resumen_especifico:
        limite_busqueda = 15
    else:
        es_resumen = any(palabra in pregunta.lower() for palabra in ["resumen", "descripción general", "visión general", "puntos principales"])
        limite_busqueda = 8 if es_resumen else limit
    
    if info:
        numero = info["numero"]
        es_robot = info["es_robot"]
        nombre_completo = obtener_nombre_maquina(numero, es_robot)
        
        if es_peticion_de_plano(pregunta):
            if nombre_completo:
                resultados = buscar_planos_por_nombre_exacto(nombre_completo)
                if resultados:
                    return resultados
            return None
        
        tipo_manual = detectar_tipo_manual(pregunta)
        if tipo_manual and nombre_completo:
            resultados = buscar_manual_por_tipo(numero, tipo_manual, es_robot)
            if resultados:
                # Si es resumen específico o general, devolvemos TODOS los resultados
                if es_resumen_especifico or any(palabra in pregunta.lower() for palabra in ["resumen", "descripción general"]):
                    return resultados
                return resultados
            return None
    
    # Búsqueda semántica
    pregunta_expandida = expandir_pregunta(pregunta)
    embedding = model.encode([pregunta_expandida], convert_to_numpy=True)[0].tolist()
    
    payload = {
        "query_embedding": embedding,
        "similitud_minima": 0.35,
        "limite": limite_busqueda * 2
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/buscar_documentos",
            headers=HEADERS,
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            resultados = response.json()
            idioma_pregunta = detectar_idioma_pregunta(pregunta)
            if idioma_pregunta:
                resultados_mismo = [r for r in resultados if r.get('metadatos', {}).get('idioma') == idioma_pregunta]
                resultados_otros = [r for r in resultados if r.get('metadatos', {}).get('idioma') != idioma_pregunta]
                resultados = resultados_mismo + resultados_otros
            return resultados[:limite_busqueda]
        return []
    except Exception as e:
        return []

def formatear_respuesta(resultados, pregunta):
    # ============================================================
    # DETECTAR SI EL USUARIO PIDE UN RESUMEN
    # ============================================================
    es_resumen = any(palabra in pregunta.lower() for palabra in ["resumen", "descripción general", "visión general", "puntos principales", "puntos clave"])
    
    # ============================================================
    # CASO 1: PETICIÓN DE PLANO ELÉCTRICO
    # ============================================================
    if es_peticion_de_plano(pregunta):
        info = extraer_numero_maquina(pregunta)
        if not info:
            return f"❌ No entendí tu pregunta. Por favor, incluye el número de máquina (ej: 'plano IMM 40' o 'plano robot IMM 40')."
        
        numero = info["numero"]
        es_robot = info["es_robot"]
        nombre_completo = obtener_nombre_maquina(numero, es_robot)
        tipo_texto = "robot" if es_robot else "IMM"
        
        if not nombre_completo:
            return f"❌ La máquina **{tipo_texto} {numero}** no existe en la base de datos.\n\n📁 **Ver todos los planos en Google Drive:** [Haz clic aquí]({GOOGLE_DRIVE_MAIN})"
        
        if not resultados or (isinstance(resultados, list) and len(resultados) == 0):
            return f"❌ No encontré planos eléctricos para **{tipo_texto} {numero}**.\n\n📁 **Ver todos los planos en Google Drive:** [Haz clic aquí]({GOOGLE_DRIVE_MAIN})"
        
        respuesta = ""
        for doc in resultados:
            metadatos = doc.get('metadatos', {})
            if isinstance(metadatos, str):
                try:
                    metadatos = json.loads(metadatos)
                except:
                    metadatos = {}
            
            archivo = metadatos.get('archivo_original', 'N/A')
            num_serie = metadatos.get('numero_serie', 'N/A')
            enlace_carpeta = CARPETAS_MAQUINAS.get(num_serie, GOOGLE_DRIVE_MAIN)
            
            respuesta += f"\n---\n"
            respuesta += f"📐 **PLANO ELÉCTRICO ENCONTRADO**\n\n"
            respuesta += f"**📁 Máquina:** {num_serie}\n"
            respuesta += f"**📄 Archivo:** `{archivo}`\n\n"
            respuesta += f"🔗 **Abrir carpeta de la máquina:** [Haz clic aquí]({enlace_carpeta})\n"
            respuesta += f"📁 **Busca el archivo:** `{archivo}` dentro de la carpeta\n"
        return respuesta
    
    # ============================================================
    # CASO 2: PETICIÓN DE MANUAL (con o sin resumen)
    # ============================================================
    tipo_manual = detectar_tipo_manual(pregunta)
    if tipo_manual:
        if resultados:
            # SI EL USUARIO PIDE UN RESUMEN, USA LA IA
            if es_resumen:
                respuesta_ia = generar_respuesta_con_ia(pregunta, resultados)
                return f"🤖 **Asistente técnico:**\n\n{respuesta_ia}\n\n---\n📁 **Manual relacionado:** [Ver en Google Drive]({GOOGLE_DRIVE_MAIN})"
            
            # SI NO PIDE RESUMEN, DEVUELVE EL ENLACE DEL MANUAL
            respuesta = ""
            vistos = set()
            for doc in resultados[:3]:
                metadatos = doc.get('metadatos', {})
                if isinstance(metadatos, str):
                    try:
                        metadatos = json.loads(metadatos)
                    except:
                        metadatos = {}
                
                archivo = metadatos.get('archivo_original', 'N/A')
                if archivo in vistos:
                    continue
                vistos.add(archivo)
                
                num_serie = metadatos.get('numero_serie', 'N/A')
                enlace_carpeta = CARPETAS_MAQUINAS.get(num_serie, GOOGLE_DRIVE_MAIN)
                
                respuesta += f"\n---\n"
                respuesta += f"📚 **MANUAL ENCONTRADO**\n\n"
                respuesta += f"**📁 Máquina:** {num_serie}\n"
                respuesta += f"**📄 Archivo:** `{archivo}`\n\n"
                respuesta += f"🔗 **Abrir carpeta en Google Drive:** [Haz clic aquí]({enlace_carpeta})\n"
                respuesta += f"📁 **Busca el archivo:** `{archivo}` dentro de la carpeta\n"
            return respuesta if respuesta else "❌ No encontré el manual solicitado.\n\n📁 **Ver todos los manuales en Google Drive:** [Haz clic aquí]({GOOGLE_DRIVE_MAIN})"
        else:
            return f"❌ No encontré el manual solicitado.\n\n📁 **Ver todos los manuales en Google Drive:** [Haz clic aquí]({GOOGLE_DRIVE_MAIN})"
    
    # ============================================================
    # CASO 3: PREGUNTA TÉCNICA GENERAL (SIEMPRE USA IA)
    # ============================================================
    respuesta_ia = generar_respuesta_con_ia(pregunta, resultados)
    
    if resultados:
        return f"🤖 **Asistente técnico:**\n\n{respuesta_ia}\n\n---\n📁 **Manuales relacionados:** [Ver en Google Drive]({GOOGLE_DRIVE_MAIN})"
    else:
        return f"🤖 **Asistente técnico:**\n\n{respuesta_ia}\n\n---\n📁 **Recursos generales:** [Abrir carpeta de manuales]({GOOGLE_DRIVE_MAIN})"

# ============================================================
# INTERFAZ
# ============================================================

st.title("🔧 Maintenance Technical Assistant")
st.markdown("Asistente virtual para máquinas de inyección")

with st.sidebar:
    st.header("📚 Documentos disponibles")
    st.markdown("""
    - Manuales de operación
    - Manuales técnicos
    - Manuales de servicio
    - Planos eléctricos
    """)
    st.markdown("---")
    st.markdown(f"### 📁 Planos en Google Drive")
    st.markdown(f"[Abrir carpeta principal]({GOOGLE_DRIVE_MAIN})")
    st.markdown("---")
    st.markdown("### 🔢 Máquinas disponibles")
    st.markdown("""
    **IMM:** 28, 35, 40, 43, 47, 53, 54, 67, 68, 72, 76, 80, 82
    **ROBOT IMM:** 39, 40, 47, 53, 54, 72, 76, 79, 82
    """)
    st.markdown("---")
    if st.button("🔧 Probar Groq"):
        resultado = test_groq_directo()
        if resultado == "OK":
            st.success("✅ Groq funciona correctamente")
        else:
            st.error(f"❌ Error: {resultado}")

with st.spinner("Cargando modelo de búsqueda..."):
    model = load_model()
    st.success("✅ Modelo listo")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente técnico de máquinas ENGEL.\n\n**Puedo ayudarte con:**\n- 🔌 Planos eléctricos (ej: *'plano IMM 40'*)\n- 📚 Manuales (ej: *'manual de operacion imm 82'* o *'manual tecnico del robot imm 72'*)\n- ⚙️ Parámetros técnicos (ej: *'¿cómo ajustar la velocidad?'*)\n\n**¿En qué te ayudo hoy?**"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu pregunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando en manuales..."):
            resultados = buscar_en_supabase(prompt, model)
            respuesta = formatear_respuesta(resultados, prompt)
            st.markdown(respuesta)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})