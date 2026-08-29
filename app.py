import streamlit as st
from rag_pipeline import create_vector_db, load_llm, get_answer

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="RAG_Project",
    layout="centered"
)

# -------------------------------
# CSS
# -------------------------------
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background-color: black;
    color: white;
}

/* Center layout */
.block-container {
    max-width: 700px;
    margin: auto;
}

/* Title */
h1 {
    text-align: center;
    color: #4f8bf9;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

/* Upload box */
[data-testid="stFileUploader"] {
    background-color: red;
    padding: 12px;
    border-radius: 10px;
}

/* Input box */
[data-testid="stTextInput"] input {
    background-color: black;
    color: white;
    border-radius: 8px;
    padding: 10px;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg, #4f8bf9, #6c63ff);
    color: white;
    border-radius: 8px;
    font-weight: bold;
    width: 100%;
}

/* Answer box */
.answer-box {
    background-color: #1a1f2e;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #4f8bf9;
    margin-top: 15px;
}

/* Source chunks */
.chunk-box {
    background-color: #161b22;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 8px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1> IntelliDocs </h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Upload document · Ask questions · Get answers instantly</p>", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "db" not in st.session_state:
    st.session_state.db = None

if "llm" not in st.session_state:
    st.session_state.llm = None

# -------------------------------
# FILE UPLOAD
# -------------------------------
st.subheader("📄 Upload Your Document")

uploaded_file = st.file_uploader("", type=["txt"])

if uploaded_file is not None:

    text = uploaded_file.read().decode("utf-8")

    with st.spinner("Processing document..."):
        db, num_chunks = create_vector_db(text)
        llm = load_llm()

        st.session_state.db = db
        st.session_state.llm = llm

    st.success(f"Document processed Successfully and ({num_chunks} no.of chunks)")

# -------------------------------
# QUESTION INPUT
# -------------------------------
st.subheader("Ask Your Question from the Document")

query = st.text_input("")

# -------------------------------
# BUTTON ACTION
# -------------------------------
if st.button("Get Answer"):

    if st.session_state.db is None:
        st.warning("Sorry,there is no document uploaded")

    elif query.strip() == "":
        st.warning("Can u pls Enter a question")

    else:
        with st.spinner("Generating answer for you..."):

            answer, sources = get_answer(
                st.session_state.db,
                st.session_state.llm,
                query
            )

        # -------------------------------
        # ANSWER DISPLAY 
        # -------------------------------
        st.markdown("### Answer")
        st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)

        # -------------------------------
        # SOURCE DISPLAY
        # -------------------------------
        with st.expander("Source Chunks"):
            for i, chunk in enumerate(sources, 1):
                st.markdown(f"<div class='chunk-box'><b>Chunk {i}:</b><br>{chunk}</div>", unsafe_allow_html=True)