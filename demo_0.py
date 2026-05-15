import streamlit as st

st.set_page_config(
    page_title="AI Video Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>

/* общий фон */
html, body, [class*="css"] {
    background-color: #05070d;
    color: white;
}

/* главный контейнер */
.stApp {
    background-color: #05070d;
}

/* убираем огромные отступы streamlit */
.block-container {
    padding-top: 0.5rem;
    padding-bottom: 0rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    max-width: 100%;
}

/* заголовок */
h1 {
    color: white !important;
    margin-top: 12px;
    margin-bottom: 0.8rem;
    padding-left: 8px;
}

/* плитка камеры */
.camera-tile {
    background: black;
    border-radius: 16px;
    border: 1px solid #1f1f1f;
    height: 42vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

/* fullscreen */
.fullscreen-tile {
    background: black;
    border-radius: 16px;
    border: 1px solid #1f1f1f;
    height: 82vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

/* текст */
.camera-title {
    color: white;
    font-size: 34px;
    font-weight: 700;
}

.camera-status {
    color: #9a9a9a;
    font-size: 18px;
    margin-top: 10px;
}

/* кнопки */
div.stButton > button {
    background-color: #171717;
    color: white;
    border-radius: 12px;
    border: 1px solid #2e2e2e;
    height: 42px;
    width: 100%;
}

/* hover */
div.stButton > button:hover {
    border: 1px solid #666;
    color: white;
}

/* уменьшаем расстояние между колонками */
[data-testid="column"] {
    padding: 0.2rem;
}

</style>
""", unsafe_allow_html=True)

if "selected_camera" not in st.session_state:
    st.session_state.selected_camera = None


def open_camera(cam_id):
    st.session_state.selected_camera = cam_id


def close_camera():
    st.session_state.selected_camera = None


cameras = [
    {"id": 1, "name": "Camera 1", "status": "NO SIGNAL"},
    {"id": 2, "name": "Camera 2", "status": "NO CAMERA"},
    {"id": 3, "name": "Camera 3", "status": "NO CAMERA"},
    {"id": 4, "name": "Camera 4", "status": "NO CAMERA"},
]


# fullscreen mode
if st.session_state.selected_camera is not None:
    cam = cameras[st.session_state.selected_camera - 1]

    top_left, top_right = st.columns([10, 1])
    with top_left:
        st.title(cam["name"])
    with top_right:
        st.markdown("<div style='margin-top: 18px'></div>", unsafe_allow_html=True)

    st.button(
        "Закрыть",
        use_container_width=True,
        on_click=close_camera
    )

    st.markdown(
        f"""
        <div class="fullscreen-tile">
            <div class="camera-title">{cam["name"]}</div>
            <div class="camera-status">{cam["status"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# grid mode
else:
    st.title("AI Video Analytics Demo")

    row1 = st.columns(2)
    row2 = st.columns(2)
    cols = row1 + row2

    for i, cam in enumerate(cameras):
        with cols[i]:
            st.markdown(
                f"""
                <div class="camera-tile">
                    <div class="camera-title">{cam["name"]}</div>
                    <div class="camera-status">{cam["status"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.button(
                f"Открыть {cam['name']}",
                key=f"open_{cam['id']}",
                use_container_width=True,
                on_click=open_camera,
                args=(cam["id"],)
            )