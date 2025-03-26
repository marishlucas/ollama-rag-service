import os
import streamlit as st
from utils.document_processor_patched import process_documents
from utils.rag_chain import create_rag_chain
import tempfile

# App configuration
st.set_page_config(
    page_title="Ollama RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Environment variables
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "http://chroma:8000")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "llama3")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")
PERSIST_DIRECTORY = os.environ.get("PERSIST_DIRECTORY", "/app/data/chroma_db")
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 200))
RETRIEVAL_K = int(os.environ.get("RETRIEVAL_K", 5))

# Initialize session state
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "files_processed" not in st.session_state:
    st.session_state.files_processed = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# CSS for styling
st.markdown(
    """
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
    }
    .feedback-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #f0f2f6;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        margin: 0 0.25rem;
        cursor: pointer;
    }
    .feedback-btn:hover {
        background-color: #e6f3ff;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1fae5;
        border: 1px solid #34d399;
        margin-bottom: 1rem;
    }
    .file-list {
        margin: 1rem 0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
    }
</style>
""",
    unsafe_allow_html=True,
)

# App header
st.title("🤖 Ollama RAG System")
st.markdown(
    "Upload documents and ask questions based on their content using Ollama and RAG."
)

# Create tabs
tab1, tab2, tab3 = st.tabs(
    ["📚 Document Processing", "❓ Question Answering", "⚙️ Settings"]
)

with tab1:
    st.header("Document Processing")
    st.markdown(
        "Upload PDF documents to be processed and indexed for question answering."
    )

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf", "txt", "csv", "md", "docx"],
        accept_multiple_files=True,
        help="Supported formats: PDF, TXT, CSV, Markdown, DOCX",
    )

    # Process button
    if uploaded_files:
        files_to_process = [
            f for f in uploaded_files if f.name not in st.session_state.files_processed
        ]
        if files_to_process:
            if st.button("Process Documents"):
                with st.spinner("Processing documents..."):
                    vectorstore = process_documents(
                        files_to_process,
                        OLLAMA_HOST,
                        EMBEDDING_MODEL,
                        CHUNK_SIZE,
                        CHUNK_OVERLAP,
                        PERSIST_DIRECTORY,
                    )
                    st.session_state.vectorstore = vectorstore
                    st.session_state.files_processed.extend(
                        [f.name for f in files_to_process]
                    )
                    st.session_state.processing_complete = True

                st.markdown(
                    f"""
                <div class="success-box">
                    ✅ Processed {len(files_to_process)} new document(s) successfully!
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Display processed files
        if st.session_state.files_processed:
            st.markdown("### Processed Documents")
            st.markdown('<div class="file-list">', unsafe_allow_html=True)
            for i, filename in enumerate(st.session_state.files_processed):
                st.markdown(f"{i+1}. {filename}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Please upload PDF documents to enable the RAG system.")

with tab2:
    st.header("Question Answering")

    # Model selection
    model_name = st.selectbox(
        "Select Ollama Model",
        [
            "llama3",
            "llama3:8b",
            "llama3:70b",
            "mistral",
            "mixtral",
            "gemma:7b",
            "phi3:mini",
        ],
        index=0,
        help="Choose the LLM to use for answering questions",
    )

    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic",
    )

    # Question input
    query = st.text_area("Enter your question:", height=100)

    # Show sources checkbox
    show_sources = st.checkbox("Show sources", value=True)

    # Answer button
    if query and (
        st.session_state.vectorstore is not None or st.session_state.processing_complete
    ):
        if st.button("Get Answer"):
            with st.spinner("Searching for information and generating answer..."):
                qa_chain = create_rag_chain(
                    st.session_state.vectorstore,
                    model_name,
                    temperature,
                    OLLAMA_HOST,
                    RETRIEVAL_K,
                )

                # Run the query
                result = qa_chain.invoke({"query": query})

                # Display results
                st.markdown("### Answer")
                st.markdown(result["result"])

                # Display sources if requested
                if show_sources and "source_documents" in result:
                    st.markdown("### Sources")
                    for i, doc in enumerate(result["source_documents"]):
                        st.markdown(f"**Source {i+1}**")
                        st.markdown(f"*From: {doc.metadata.get('source', 'Unknown')}*")
                        st.markdown(f"```\n{doc.page_content[:500]}...\n```")
    elif not st.session_state.processing_complete:
        st.warning(
            "Please process some documents first in the Document Processing tab."
        )

with tab3:
    st.header("Settings")

    st.markdown("### Environment Configuration")
    st.code(f"""
    OLLAMA_HOST = {OLLAMA_HOST}
    CHROMA_HOST = {CHROMA_HOST}
    DEFAULT_MODEL = {DEFAULT_MODEL}
    EMBEDDING_MODEL = {EMBEDDING_MODEL}
    PERSIST_DIRECTORY = {PERSIST_DIRECTORY}
    """)

    st.markdown("### Advanced Settings")
    st.markdown("These settings can be modified in the `.env` file:")

    st.markdown("#### Document Processing")
    st.markdown(f"- **Chunk Size**: {CHUNK_SIZE} characters")
    st.markdown(f"- **Chunk Overlap**: {CHUNK_OVERLAP} characters")

    st.markdown("#### Retrieval")
    st.markdown(f"- **Number of chunks retrieved**: {RETRIEVAL_K}")

    st.markdown("### Available Models")
    with st.spinner("Fetching available models..."):
        try:
            # Placeholder for model fetching - in a real implementation, you'd fetch from Ollama API
            st.markdown("- llama3 (default)")
            st.markdown("- llama3:8b")
            st.markdown("- llama3:70b")
            st.markdown("- mistral")
            st.markdown("- mixtral")
            st.markdown("- gemma:7b")
            st.markdown("- phi3:mini")

            st.info(
                "To pull additional models, use `make pull-models` or add your model to the scripts/pull_models.sh file."
            )
        except Exception as e:
            st.error(f"Error fetching models: {e}")

# Footer
st.markdown("---")
st.markdown("Ollama RAG System | Made with Streamlit + Ollama + ChromaDB")