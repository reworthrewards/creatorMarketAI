import streamlit as st
import openai
import os
import json
import requests
from PIL import Image
import io
import base64

#🎨 Favicon + title
st.set_page_config(
    page_title="Creativos | Majo",  
    page_icon="🎨",
)

# 🚨 Código de acceso predefinido
ACCESO_PERMITIDO = "prueba"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("Acceso Restringido")
    clave = st.text_input("Ingresa el código de acceso:", type="password")

    if clave == ACCESO_PERMITIDO:
        st.session_state["autenticado"] = True
        st.rerun() 
    elif clave:
        st.error("Código incorrecto. Inténtalo de nuevo.")
    st.stop()


#estilos
st.markdown("""
    <style>
        div.stButton > button {
            border: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        div.stButton > button:hover {
            background-color: #021666;
            color: white !important;
        }

        body {
            background-color: #121212;
        }

        h1 {
            font-size: 1.8rem !important; 
            font-weight: bold;
        }
        
        hr{
            height: 4px;
            background: linear-gradient(90deg, #2E58FF 30%, #D5DAE5 70%);
            border: none;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Configurar manualmente la clave API (solo para pruebas locales)
#os.environ["OPENAI_API_KEY"] = ""
#os.environ["STABILITY_API_KEY"] = ""
#os.environ["FREEPIK_API_KEY"] = ""

# Cargar claves desde variables de entorno
openai_api_key = os.getenv("OPENAI_API_KEY")
stability_api_key = os.getenv("STABILITY_API_KEY")
freepik_api_key = os.getenv("FREEPIK_API_KEY")

if not openai_api_key:
    raise ValueError("⚠️ ERROR: No se encontró OPENAI_API_KEY en las variables de entorno.")

if not stability_api_key:
    raise ValueError("⚠️ ERROR: No se encontró STABILITY_API_KEY en las variables de entorno.")

if not freepik_api_key:
    raise ValueError("⚠️ ERROR: No se encontró FREEPIK_API_KEY en las variables de entorno.")

print("API Key de OpenAI cargada:", openai_api_key)
print("API Key de Stability AI cargada:", stability_api_key)

# Cliente de OpenAI
client_openai = openai.OpenAI(api_key=openai_api_key)


# 👩🏽‍💻 prompt solicitado para los copys
def generar_copy(comercio, recompensa_bienvenida, recompensa_recurrente, categoria, banco, ejemplo_copy, limite_caracteres):
    prompt = f"""
    Genera exactamente 3 copys publicitarios atractivos para una promoción de un comercio de la categoría {categoria}. 
    Asegúrate de que el tono del mensaje sea apropiado para un negocio en esta categoría.
    
    - Cada copy debe tener un máximo de {limite_caracteres} caracteres.
    - No los numeres ni los separes con guiones, deben estar separados por saltos de línea.
    - Deben ser breves, persuasivos y adecuados para redes sociales en México.
    
    Información del comercio:
    - Comercio: {comercio}
    - Recompensa de Bienvenida: {recompensa_bienvenida}
    - Recompensa Recurrente: {recompensa_recurrente}
    - Categoría: {categoria}
    - Banco asociado: {banco}
    
    Ejemplo de copy deseado:
    {ejemplo_copy}

    Por favor, respeta estrictamente el límite de caracteres en cada copy y no devuelvas otro contenido que no sean los 3 copys.
    """

    # Aproximación para convertir caracteres a tokens
    max_tokens = (limite_caracteres // 4) * 3  

    response = client_openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens  
    )

    # Separar los copys generados asegurando que sean 3 y respetando el límite de caracteres
    copies = response.choices[0].message.content.strip().split("\n")
    return [copy.strip()[:limite_caracteres] for copy in copies if copy.strip()][:3]

# 👩🏽‍💻 prompt solicitado para Stability
# def generar_imagen_stability(texto_prompt, imagenes_referencia, imagenes_subidas):
    api_key = os.getenv("STABILITY_API_KEY")
    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

    if not texto_prompt or texto_prompt.strip() == "":
        return "❌ Error: El prompt no puede estar vacío. Por favor, ingresa una descripción."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }

    files = {}

    if imagenes_referencia:
        ref_image_path = imagenes_referencia[0] 
        with open(ref_image_path, "rb") as img_file:
            files["image"] = ("image.png", img_file.read(), "image/png")

    if imagenes_subidas:
        uploaded_img = imagenes_subidas[0]  
        files["image"] = (uploaded_img.name, uploaded_img.getvalue(), uploaded_img.type)

    data = {
        "prompt": texto_prompt,
        "mode": "image-to-image" if files else "text-to-image",
        "strength": "0.2" if files else "", 
        "output_format": "png",
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    print("\n🔍 Código de respuesta:", response.status_code)

    if response.status_code == 200:
        try:
            image = Image.open(io.BytesIO(response.content))
            return image
        except Exception as e:
            return f"❌ Error al procesar la imagen: {str(e)}"
    else:
        return f"❌ Error en la generación de imágenes: {response.text}"#


def generar_imagen_stability(texto_prompt, imagenes_referencia=None, imagenes_subidas=None):
    api_key = os.getenv("STABILITY_API_KEY")
    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

    if not texto_prompt or texto_prompt.strip() == "":
        return "❌ Error: El prompt no puede estar vacío. Por favor, ingresa una descripción."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }

    files = {}
    modo = "text-to-image"  # Por defecto, usar solo texto

    # Verificar si hay imágenes (referencia o subidas)
    tiene_imagenes = (imagenes_referencia and len(imagenes_referencia) > 0) or (imagenes_subidas and len(imagenes_subidas) > 0)

    if tiene_imagenes:
        modo = "image-to-image"

        if imagenes_referencia:
            ref_image_path = imagenes_referencia[0]
            with open(ref_image_path, "rb") as img_file:
                files["image"] = ("image.png", img_file.read(), "image/png")

        if imagenes_subidas:
            uploaded_img = imagenes_subidas[0]
            files["image"] = (uploaded_img.name, uploaded_img.getvalue(), uploaded_img.type)

    data = {
    "prompt": texto_prompt,
    "mode": modo,
    "output_format": "png"
    }

    # Solo agregar "strength" si el modo es "image-to-image"
    if modo == "image-to-image":
        data["strength"] = "0.8"

    response = requests.post(url, headers=headers, files=files if modo == "image-to-image" else {"none": ""}, data=data)

    print("\n🔍 Código de respuesta:", response.status_code)

    if response.status_code == 200:
        try:
            image = Image.open(io.BytesIO(response.content))
            return image
        except Exception as e:
            return f"❌ Error al procesar la imagen: {str(e)}"
    else:
        return f"❌ Error en la generación de imágenes: {response.text}"

# 👩🏽‍💻 prompt solicitado para Dalle
def generar_imagen_dalle(texto_prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/images/generations"

    if not texto_prompt or texto_prompt.strip() == "":
        return "❌ Error: El prompt no puede estar vacío. Por favor, ingresa una descripción."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "dall-e-3",  # O puedes probar "dall-e-3"
        "prompt": texto_prompt,
        "n": 1,
        "size": "1024x1024"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            image_url = response.json()["data"][0]["url"]
            return image_url
        except Exception as e:
            return f"❌ Error al procesar la imagen: {str(e)}"
    else:
        return f"❌ Error en la generación de imágenes: {response.text}"

# 👩🏽‍💻 prompt solicitado para Freepik
def generar_imagen_freepik(texto_prompt):
    api_key = os.getenv("FREEPIK_API_KEY")
    url = "https://api.freepik.com/v1/ai/mystic"

    if not texto_prompt or texto_prompt.strip() == "":
        return "❌ Error: El prompt no puede estar vacío."

    headers = {
        "x-freepik-api-key": api_key, 
        "Content-Type": "application/json",
    }

    data = {
        "prompt": texto_prompt,
        "n": 1,
        "size": "1024x1024"
    }

    response = requests.post(url, headers=headers, json=data)
    print("🔍 Código de respuesta:", response.status_code)
    
    if response.status_code == 200:
        try:
            respuesta_json = response.json()
            print("📩 Respuesta JSON:", respuesta_json)  # Debugging
            image_url = respuesta_json["data"][0]["url"]
            return image_url
        except KeyError:
            return f"❌ Error al procesar la imagen: {respuesta_json}"
    else:
        return f"❌ Error en la generación de imágenes: {response.text}"

# Cargar lista de comercios con logos desde el JSON
try:
    with open("comercios.json", "r") as f:
        data = json.load(f)
        comercios = data.get("comercios", [])
except FileNotFoundError:
    comercios = []


#
#
#
# 🟢 Si el código es correcto, muestra la app normalmente
#
#
#
st.title("Generador de Creativos para Promociones")
# Botón para cerrar sesión
if st.button("🔒 Cerrar sesión", type="secondary"):
    st.session_state["autenticado"] = False
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["Copys", "Stability", "Open IA", "Freepik"])

with tab1:
    # Extraer solo los nombres de los comercios
    comercio_nombres = [c["nombre"] for c in comercios]
    col1, col2 = st.columns([1, 4])

    # Obtener categorías únicas desde el JSON
    categorias_unicas = list(set(c["categoria"] for c in comercios if "categoria" in c))

    with col2:
        comercio_seleccionado = st.selectbox(
        "Nombre del comercio", comercio_nombres, key="comercio_copys")
        recompensa_bienvenida = st.text_input("Recompensa de Bienvenida", "10%")
        recompensa_recurrente = st.text_input("Recompensa Recurrente (opcional)", "5%")
        # Buscar información del comercio seleccionado
        comercio_info = next((c for c in comercios if c["nombre"] == comercio_seleccionado), None)
        # Si el comercio tiene una categoría definida, la seleccionamos automáticamente
        if comercio_info:
            categoria_predeterminada = comercio_info["categoria"]
        else:
            categoria_predeterminada = ""
        categoria = st.selectbox("Categoría del negocio", categorias_unicas, index=categorias_unicas.index(categoria_predeterminada) if categoria_predeterminada in categorias_unicas else 0)
        banco = st.text_input("Banco asociado", "albo")
        ejemplo_copy = st.text_input("Ejemplo de copy deseado", "¡Aprovecha nuestra oferta!")
        evento = st.text_input("Fiesta o evente a tener en cuenta", "Fiestas patrias")
        limite_caracteres = st.number_input("Límite de caracteres en la respuesta", min_value=50, max_value=500, value=200, step=10)
        if st.button("Generar Copys", type="primary", icon="🎉"):
            st.session_state["copies_generados"] = generar_copy(comercio_seleccionado, recompensa_bienvenida, recompensa_recurrente, categoria, banco, ejemplo_copy, limite_caracteres)
       # Buscar información del comercio seleccionado

    with col1:
        comercio_info = next((c for c in comercios if c["nombre"] == comercio_seleccionado), None)
        if comercio_info:
            st.image(comercio_info["logo"], width=80, use_container_width=True)

    # Resultado del prompt   
    if "copies_generados" in st.session_state:
        copies_generados = st.session_state["copies_generados"]
        st.write("### Copys Generados:")
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
        for copy in copies_generados:
            st.code(copy)

with tab2:
    col1, col2 = st.columns([1, 4])  

    with col1:
        comercio_seleccionado_img = st.selectbox(
            "Nombre del comercio", comercio_nombres, key="comercio_imagenes"
        )
        comercio_info_img = next((c for c in comercios if c["nombre"] == comercio_seleccionado_img), None)
        if comercio_info_img:
            st.image(comercio_info_img["logo"], width=100, use_container_width=True)

    with col2:
        st.write("📸 **Imágenes de referencia:**")

        imagenes_referencia = comercio_info_img.get("imagenes_referencia", []) if comercio_info_img else []
        if imagenes_referencia:
            for img in imagenes_referencia:
                st.image(img,  use_container_width=True)
        else:
            st.info("📢 Aún no se han creado comunicaciones para esta marca")

        # Subida de imágenes adicionales
        imagenes_subidas = st.file_uploader("Sube imágenes adicionales", accept_multiple_files=True, type=["png", "jpg", "jpeg"])
        
        # Campo de texto para descripción
        descripcion = st.text_area("📝 Añadir texto descriptivo para la generación de imágenes")

       # Botón para generar imágenes
        if st.button("🎨 Generar Imagen", type="primary"):
            with st.spinner("Generando imagen..."):

                # Verificar si hay imágenes de referencia y subidas
                tiene_referencia = imagenes_referencia and len(imagenes_referencia) > 0
                tiene_subidas = imagenes_subidas and len(imagenes_subidas) > 0

                # Si no hay imágenes, solo enviamos el prompt (text-to-image)
                if not tiene_referencia and not tiene_subidas:
                    imagen_generada = generar_imagen_stability(descripcion)
                else:
                    imagen_generada = generar_imagen_stability(descripcion, imagenes_referencia, imagenes_subidas)

            # Manejo de la imagen generada
            if isinstance(imagen_generada, str) and "❌ Error" in imagen_generada:
                st.error(imagen_generada)  # Mostrar mensaje de error
            elif isinstance(imagen_generada, Image.Image):  # Si se generó correctamente
                st.image(imagen_generada, use_container_width=True)

                # Guardar la imagen en un buffer para descarga
                buffered = io.BytesIO()
                imagen_generada.save(buffered, format="PNG")
                image_bytes = buffered.getvalue()

                st.download_button(
                    label="📥 Descargar Imagen",
                    data=image_bytes,
                    file_name="imagen_generada.png",
                    mime="image/png"
                )
            else:
                st.warning("⚠️ No se generó ninguna imagen. Revisa el prompt.")

with tab3:

    # Campo de texto para descripción
    descripcion_dalle = st.text_area("📝 Añadir prompt para generar la imagen con Open IA")

    # Botón para generar imágenes
    if st.button("🎨 Generar Imagen con Open IA", type="primary"):
        with st.spinner("Generando imagen con Open IA..."):
            imagen_generada_url = generar_imagen_dalle(descripcion_dalle)

        if isinstance(imagen_generada_url, str) and "❌ Error" in imagen_generada_url:
            st.error(imagen_generada_url)  # Mostrar mensaje de error
        else:  # Si se generó correctamente
            st.image(imagen_generada_url, use_container_width=True)

            # Descargar imagen
            st.download_button(
                label="📥 Descargar Imagen",
                data=requests.get(imagen_generada_url).content,
                file_name="imagen_generada_dalle.png",
                mime="image/png"
            )

with tab4:
    with st.container():
        # Campo de texto para ingresar la descripción de la imagen
        descripcion_freepik = st.text_area("📝 Añadir prompt para generar la imagen con Freepik")

        # Botón para generar imágenes
        if st.button("🎨 Generar Imagen con Freepik", type="primary"):
            with st.spinner("Generando imagen con Freepik..."):
                imagen_generada_url = generar_imagen_freepik(descripcion_freepik)

            if isinstance(imagen_generada_url, str) and "❌ Error" in imagen_generada_url:
                st.error(imagen_generada_url)  # Mostrar mensaje de error
            else:  # Si se generó correctamente
                st.image(imagen_generada_url, use_column_width=True)

                # Descargar imagen
                st.download_button(
                    label="📥 Descargar Imagen",
                    data=requests.get(imagen_generada_url).content,
                    file_name="imagen_generada_freepik.png",
                    mime="image/png"
                )