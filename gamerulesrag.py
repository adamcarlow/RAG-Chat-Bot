import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Board Game Rules Assistant", layout="wide")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Set in .env file
MODEL_NAME = "llama-3.3-70b-versatile"  # Free models: "llama-3.3-70b-versatile", "mixtral-8x7b-32768"

# RAG Configuration
CHUNK_SIZE = 2000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
TOP_K_CHUNKS = 4  # Number of relevant chunks to retrieve

PROMPT_TEMPLATE = """\
You are an expert board game rules specialist. Your job is to help players understand game rules, clarify confusing situations, and explain how to play.

When answering:
- Be clear and precise about game mechanics
- Use examples when helpful to illustrate rules
- If a rule interaction is ambiguous, explain the most common interpretation
- Reference specific sections or page numbers from the rulebook when possible

Use **only** the information from the provided rulebook context below.

Relevant Rulebook Sections:
{context}

Player's Question: {question}

Answer:"""

# ─── Functions ────────────────────────────────────────────────────────────
def get_llm():
    return ChatGroq(model=MODEL_NAME, temperature=0.2, api_key=GROQ_API_KEY)

@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Load the embedding model (cached to avoid reloading)."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def load_and_chunk_pdf(pdf_path: str | Path):
    """Load PDF and split into chunks."""
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    return chunks

def create_vector_store(chunks, embeddings):
    """Create FAISS vector store from chunks."""
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

def retrieve_relevant_chunks(vector_store, question: str, k: int = TOP_K_CHUNKS):
    """Retrieve the most relevant chunks for a question."""
    docs = vector_store.similarity_search(question, k=k)
    return docs

# ─── UI ────────────────────────────────────────────────────────────────────

# Header with board game theme
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <span style="font-size: 4rem;">🎲 🎯 🃏</span>
        <h1 style="margin-top: 0;">Board Game Rules Assistant</h1>
        <p style="color: gray;">Upload a rulebook, ask questions, get answers instantly</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar with tips
with st.sidebar:
    st.markdown("### 🎮 How to Use")
    st.markdown("""
    1. **Upload** your game's rulebook PDF
    2. **Wait** for processing (chunking & embedding)
    3. **Ask** any rules question
    4. **Get** instant answers
    """)

    st.markdown("---")
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    - *"How do I set up the game?"*
    - *"What happens when I roll doubles?"*
    - *"Can I trade on my first turn?"*
    - *"How do I win?"*
    """)

    st.markdown("---")
    st.markdown("### 🎲 Supported Games")
    st.markdown("Any board game with a PDF rulebook!")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a game rulebook (PDF)",
    type=["pdf"],
    help="Upload the PDF rulebook for any board game"
)

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_dir = Path("temp_pdfs")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / uploaded_file.name

    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Create a unique key for this file to cache the vector store
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"

    # Check if we already processed this file
    if "vector_store" not in st.session_state or st.session_state.get("file_key") != file_key:

        # Step 1: Load and chunk the PDF
        with st.spinner("📄 Loading and chunking PDF..."):
            chunks = load_and_chunk_pdf(temp_path)

        # Step 2: Load embedding model
        with st.spinner("🧠 Loading embedding model..."):
            embeddings = get_embeddings()

        # Step 3: Create vector store
        with st.spinner("🔢 Creating embeddings and vector store..."):
            vector_store = create_vector_store(chunks, embeddings)

        # Store in session state
        st.session_state.vector_store = vector_store
        st.session_state.file_key = file_key
        st.session_state.num_chunks = len(chunks)

    st.success("📖 Rulebook processed")

    # Show chunk info
    with st.expander("📊 Processing Details"):
        st.markdown(f"""
        - **Chunks created:** {st.session_state.num_chunks}
        - **Chunk size:** {CHUNK_SIZE} characters
        - **Overlap:** {CHUNK_OVERLAP} characters
        - **Embedding model:** all-MiniLM-L6-v2
        - **Vector store:** FAISS
        """)

    # Question input
    st.markdown("### ❓ Ask a Rules Question")
    question = st.text_input("Your question:",
                            placeholder="How do I set up the game?",
                            key="question_input",
                            label_visibility="collapsed")

    if question and question.strip():
        if st.button("🎯 Get Answer", type="primary"):

            # Step 1: Retrieve relevant chunks
            with st.spinner("🔍 Finding relevant sections..."):
                relevant_docs = retrieve_relevant_chunks(
                    st.session_state.vector_store,
                    question
                )
                context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])

            # Step 2: Generate answer
            with st.spinner("🎲 Generating answer..."):
                llm = get_llm()

                prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
                chain_input = {"context": context, "question": question}
                formatted_prompt = prompt.format(**chain_input)

                try:
                    response = llm.invoke(formatted_prompt)
                    answer = response.content

                    st.markdown("### 📜 Answer")
                    st.info(answer)

                except Exception as e:
                    st.error(f"Error while running model:\n{e}")

# Cleanup hint
st.markdown("---")
if st.button("🗑️ Clear uploaded rulebooks", help="Removes uploaded PDFs and clears cache"):
    try:
        for file in Path("temp_pdfs").glob("*.pdf"):
            file.unlink()
        if "vector_store" in st.session_state:
            del st.session_state.vector_store
        if "file_key" in st.session_state:
            del st.session_state.file_key
        st.success("Rulebooks and cache cleared!")
        st.rerun()
    except Exception as e:
        st.warning(f"Could not delete some files: {e}")

st.markdown("---")
st.caption("Powered by Llama 3.3 • Groq | Embeddings: all-MiniLM-L6-v2 | Vector Store: FAISS")
