import streamlit as st
import pyperclip
import openai
import os
import json

import streamlit as st

# Código de acceso predefinido
ACCESO_PERMITIDO = "prueba"

# Si la autenticación aún no se ha realizado
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Si el usuario aún no está autenticado, mostrar solo el input del código
if not st.session_state["autenticado"]:
    st.title("Acceso Restringido")
    clave = st.text_input("Ingresa el código de acceso:", type="password")

    if clave == ACCESO_PERMITIDO:
        st.session_state["autenticado"] = True
        st.rerun()  # 🔄 Recarga la app después de autenticarse correctamente
    elif clave:
        st.error("Código incorrecto. Inténtalo de nuevo.")

    # 🔴 Detiene la ejecución aquí y NO muestra el resto de la app
    st.stop()

# 🟢 Si el código es correcto, muestra la app normalmente
st.title("Generador de Creativos para Promociones")

st.markdown("""
    <style>
        /* Cambia el color del botón */
        div.stButton > button {
            background-color: #2E58FF;
            color: white;
            font-weight: bold;
            border-radius: 4px;
            padding: 10px 20px;
            border: none;
            transition: background-color 0.3s;
        }
        div.stButton > button:hover {
            background-color: #021666;
        }

        /* Cambia el fondo de la app */
        body {
            background-color: #121212;
        }

        /* Cambia el tamaño del título */
        h1 {
            font-size: 1.8rem !important; 
            font-weight: bold;
        }

        /* Cambia el color de los select y text inputs */
        div[data-baseweb="select"] > div {
            background-color: #222;
            color: white;
        }

        input {
            background-color: #333;
            color: white;
        }
        
        hr{
            height: 4px;
            background: linear-gradient(90deg, #2E58FF 30%, #D5DAE5 70%);
            border: none;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))


def generar_copy(comercio, recompensa_bienvenida, recompensa_recurrente, categoria, banco, ejemplo_copy, limite_caracteres):
    max_tokens = limite_caracteres // 4
    prompt = f"""
    Genera 3 copys publicitarios atractivos para una promoción de un comercio.
    Comercio: {comercio}
    Recompensa de Bienvenida: {recompensa_bienvenida}
    Recompensa Recurrente: {recompensa_recurrente}
    Categoría: {categoria}
    Banco asociado: {banco}
    Ejemplo de copy deseado: {ejemplo_copy}

    Los copys deben ser breves, persuasivos y adecuados para redes sociales en México.
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    
    copies = response.choices[0].message.content.split("\n")
    return [copy for copy in copies if copy.strip()][:3]



# Cargar lista de comercios con logos desde el JSON
try:
    with open("comercios.json", "r") as f:
        data = json.load(f)
        comercios = data.get("comercios", [])
except FileNotFoundError:
    comercios = []

st.divider()

# Extraer solo los nombres de los comercios
comercio_nombres = [c["nombre"] for c in comercios]
col1, col2 = st.columns([1, 4])  # La primera columna más ancha

with col2:
    comercio_seleccionado = st.selectbox("Nombre del comercio", comercio_nombres)
    recompensa_bienvenida = st.text_input("Recompensa de Bienvenida", "10%")
    recompensa_recurrente = st.text_input("Recompensa Recurrente (opcional)", "5%")
    categoria = st.text_input("Categoría del negocio", "Restaurantes")
    banco = st.text_input("Banco asociado", "albo")
    ejemplo_copy = st.text_input("Ejemplo de copy deseado", "¡Aprovecha nuestra oferta!")
    limite_caracteres = st.number_input("Límite de caracteres en la respuesta", min_value=50, max_value=500, value=200, step=10)
    if st.button("Generar Creativo", type="primary", icon="🎉"):
        st.session_state["copies_generados"] = generar_copy(comercio_seleccionado, recompensa_bienvenida, recompensa_recurrente, categoria, banco, ejemplo_copy, limite_caracteres)

with col1:
    comercio_info = next((c for c in comercios if c["nombre"] == comercio_seleccionado), None)
    if comercio_info:
        st.image(comercio_info["logo"], width=80, use_container_width=True)


if "copies_generados" in st.session_state:
    copies_generados = st.session_state["copies_generados"]
    st.write("### Copys Generados:")
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    for copy in copies_generados:
        st.code(copy)
        if st.button("Copiar", key=copy):
            pyperclip.copy(copy)
            st.success("Texto copiado al portapapeles!")
