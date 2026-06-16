def generar_respuesta_con_ia(pregunta, resultados_supabase):
    """Usa Groq para generar una respuesta técnica basada EXCLUSIVAMENTE en los manuales"""
    
    contexto = ""
    if resultados_supabase:
        # Para resúmenes, usamos más fragmentos
        es_resumen = any(palabra in pregunta.lower() for palabra in ["resumen", "descripción general", "visión general", "puntos principales"])
        num_fragmentos = 8 if es_resumen else 3  # Más fragmentos para resúmenes
        
        for doc in resultados_supabase[:num_fragmentos]:
            texto = doc.get('texto', '')[:2500]  # Más texto para mejor contexto
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
    
    # ============================================================
    # PROMPT MEJORADO PARA RESUMENES MÁS DETALLADOS
    # ============================================================
    if es_resumen:
        prompt = f"""Eres un asistente técnico experto en máquinas de inyección ENGEL.

La siguiente información ha sido EXTRAÍDA DIRECTAMENTE de los manuales de ENGEL.
Debes responder EXCLUSIVAMENTE usando esta información.

INFORMACIÓN DE LOS MANUALES (NO inventes nada fuera de esto):
{contexto}

Pregunta del técnico: {pregunta}

**INSTRUCCIONES OBLIGATORIAS PARA EL RESUMEN:**

1. **IDIOMA:** Responde SIEMPRE en ESPAÑOL, incluso si el texto fuente está en alemán, inglés u otro idioma.

2. **ESTRUCTURA DEL RESUMEN:** Organiza la respuesta con estas secciones:

   ## 📋 RESUMEN DEL MANUAL [nombre de la máquina]

   ### 🎯 PROPÓSITO DEL MANUAL
   [Explica para qué sirve este manual, qué tipo de información contiene y a quién va dirigido]

   ### 📑 CONTENIDO PRINCIPAL
   [Lista los temas principales que cubre el manual, organizados por categorías lógicas]

   ### 🔧 PROCEDIMIENTOS DE MANTENIMIENTO
   [Describe los procedimientos de mantenimiento más importantes que se mencionan]

   ### 🛡️ DISPOSITIVOS DE SEGURIDAD
   [Menciona los dispositivos de seguridad que se describen y cómo se verifican]

   ### ⚙️ PARÁMETROS Y CONFIGURACIONES CRÍTICAS
   [Valores, ajustes o configuraciones importantes que se mencionan]

   ### ⚠️ ADVERTENCIAS IMPORTANTES
   [Precauciones o advertencias de seguridad destacadas en el manual]

3. **DETALLE:** Sé completo y detallado. Si el manual tiene información extensa, organízala en subsecciones. No te limites a frases cortas.

4. **CITAS:** Al final del resumen, lista todas las fuentes consultadas con el formato:
   - (Máquina, Tipo, Página)

5. **SI FALTA INFORMACIÓN:** Si alguna sección no tiene información en los fragmentos disponibles, indícalo claramente: "No se encontró información específica sobre [tema] en los fragmentos disponibles".

**Resumen basado en el manual:**"""
    else:
        # Prompt para preguntas específicas
        prompt = f"""Eres un asistente técnico experto en máquinas de inyección ENGEL.

La siguiente información ha sido EXTRAÍDA DIRECTAMENTE de los manuales de ENGEL.
Debes responder EXCLUSIVAMENTE usando esta información.

INFORMACIÓN DE LOS MANUALES (NO inventes nada fuera de esto):
{contexto}

Pregunta del técnico: {pregunta}

**INSTRUCCIONES OBLIGATORIAS:**

1. **IDIOMA:** Responde SIEMPRE en ESPAÑOL, incluso si el texto fuente está en alemán, inglés u otro idioma.

2. **RESPUESTA CLARA:** Organiza la información de forma lógica y fácil de entender.

3. **CITAS:** Cita las fuentes usando el formato: (Máquina, Tipo, Página)

4. **SI NO ENCUENTRAS INFORMACIÓN:** Di claramente: "No encontré esta información específica en el manual"

5. **NO USES CONOCIMIENTO GENERAL:** Solo lo que dice el manual.

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
- SIEMPRE respondes en ESPAÑOL, sin importar el idioma del texto fuente.
- Traduces correctamente los términos técnicos del alemán o inglés al español.

**INSTRUCCIONES ESPECIALES PARA RESUMENES:**
Cuando el usuario pide un "resumen", "descripción general" o "visión general":
- Organiza la información en secciones claras con títulos y subtítulos
- Sé detallado y completo, no uses frases cortas
- Sintetiza los puntos más importantes de TODOS los fragmentos disponibles
- Mantén un tono técnico pero accesible para técnicos de mantenimiento
- Cita todas las fuentes principales al final

**FORMATO PARA RESUMEN:**
---
## 📋 RESUMEN DEL MANUAL [nombre_maquina]

### 🎯 PROPÓSITO DEL MANUAL
[Descripción detallada del propósito]

### 📑 CONTENIDO PRINCIPAL
[Temas clave organizados lógicamente]

### 🔧 PROCEDIMIENTOS DE MANTENIMIENTO
[Procedimientos importantes]

### 🛡️ DISPOSITIVOS DE SEGURIDAD
[Dispositivos y verificaciones]

### ⚙️ PARÁMETROS CRÍTICOS
[Valores y configuraciones importantes]

### ⚠️ ADVERTENCIAS
[Precauciones destacadas]

---
"""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000 if es_resumen else 1000,  # Más tokens para resúmenes
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al conectar con el asistente IA: {str(e)[:150]}\n\n📁 Por favor, consulta los manuales en Google Drive."