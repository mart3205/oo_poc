# app.py file modifications

import invoke_agent as agenthelper
import streamlit as st
import json
import pandas as pd

# Streamlit page configuration
st.set_page_config(page_title="Asistente Alfred", page_icon=":test:", layout="wide")

# Sample user credentials (store these securely in production)
valid_users = {
    "martin.hernandez@rackspace.com": "admin08#",
    "luz.infante@rackspace.com": "ajiaco",
    "user1": "DKQH11873111",
    "user2": "YWPC16421416",
    "user3": "JQIF19744380",
    "user4": "ADNB14892661",
    "user5": "KQGD16269006",
    "user6": "TYDP12080327",
    "user7": "TSIN10018184",
    "user8": "MWMH17824485",
    "user9": "BYHG16497889",
    "user10": "NSAB19748205",
    "user11": "LPZY11812450",
    "user12": "CRET12080142",
    "user13": "AWUE14072889",
    "user14": "KXZL12038976",
    "user15": "FRRC10475043"
}

# Function to authenticate users
def authenticate(username, password):
    return valid_users.get(username) == password

# Session state for login status
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Initialize username and password in session state if not already set
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'password' not in st.session_state:
    st.session_state['password'] = ""

# Display the login form only if the user is not logged in
if not st.session_state['logged_in']:
    with st.sidebar:
        st.title("Iniciar Sesión")
        st.session_state['username'] = st.text_input("Usuario", value=st.session_state['username'], key="username_input")
        st.session_state['password'] = st.text_input("Contraseña", type="password", value=st.session_state['password'], key="password_input")
        login_button = st.button("Iniciar Sesión")

        # Handle login
        if login_button:
            if authenticate(st.session_state['username'], st.session_state['password']):
                st.session_state['logged_in'] = True
                # Clear username and password fields after successful login
                st.session_state['username'] = ""
                st.session_state['password'] = ""
                st.success("Inicio de sesión exitoso.")
                st.rerun()  # Refresh the app to reflect changes
            else:
                st.error("Usuario o contraseña incorrectos.")

# Only show the main interface if the user is logged in
if st.session_state['logged_in']:
    # Initialize the session state for history if it doesn't exist
    if 'history' not in st.session_state:
        st.session_state['history'] = []  # Initialize as an empty list

    # Sidebar for user input
    st.sidebar.title("Historia")

    # Create a layout for the page with the sidebar
    if st.session_state['history']:
        image_width = 700
        col_width = 28  # Reduced width when sidebar is open
    else:
        image_width = 1110  # Full width when sidebar is hidden
        col_width = 34  # Full width when sidebar is hidden

    # Crear un layout en columnas
    col1, = st.columns([col_width])

    # Colocar la imagen y el título en columnas separadas
    with col1:
        st.image("cinta.png", width=image_width)  # Dynamically adjust the image size

    st.write("")

    # Input prompt for the question
    prompt = st.text_input("Escribe una pregunta y presiona el botón Enviar", max_chars=500, key='input', 
                           placeholder='Haz tu pregunta aquí', help='Crea preguntas específicas para tener las mejores respuestas')
    prompt = prompt.strip()

    # Display a primary button for submission
    submit_button = st.button("Enviar", type="primary")

    # Display a button to end the session
    end_session_button = st.button("Terminar sesión")

    # Function to parse and format response
    def format_response(response_body):
        try:
            data = json.loads(response_body)
            if isinstance(data, list):
                return pd.DataFrame(data)
            else:
                return response_body
        except json.JSONDecodeError:
            return response_body

    # Handling user input and responses
    if submit_button and prompt:
        event = {
            "sessionId": "MYSESSION",
            "question": prompt
        }

        response = agenthelper.lambda_handler(event, None)
        try:
            if response and 'body' in response and response['body']:
                response_data = json.loads(response['body'])
            else:
                st.warning("Respuesta no válida o vacía.")
                response_data = None
        except json.JSONDecodeError as e:
            st.error(f"Error al decodificar JSON: {e}")
            response_data = None

        if response_data and 'response' in response_data:
            try:
                formatted_response = format_response(response_data['response'])
                the_response = response_data['response']
            except Exception as e:
                st.error(f"Error al formatear respuesta: {e}")
                formatted_response = "Error al formatear respuesta"
                the_response = "Lo siento, ocurrió un error. Ejecuta nuevamente por favor."

            st.session_state['history'].append({"question": prompt, "answer": the_response})

            st.sidebar.write("Historial de Preguntas y Respuestas:")
            for interaction in st.session_state['history']:
                st.sidebar.write(f"**Pregunta:** {interaction['question']}")
                st.sidebar.write(f"**Respuesta:** {interaction['answer']}")
                st.sidebar.write("---")  # Separator between each interaction

            st.text_area("Respuesta", value=formatted_response, height=300)
        else:
            st.error("No se obtuvo una respuesta válida.")

    # If the "Terminar sesión" button is clicked
    if end_session_button:
        # Clear the session state and log out
        st.session_state.clear()
        st.write("La sesión ha terminado. Gracias por usar el asistente Alfred.")
        st.session_state['session_active'] = False
        st.rerun()
        st.stop()
        
else:
    st.write("Por favor, inicie sesión para acceder al asistente Alfred.")

