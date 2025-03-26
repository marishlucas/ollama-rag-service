import os
import tempfile
import streamlit as st
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_documents(
    uploaded_files,
    ollama_host,
    embedding_model,
    chunk_size,
    chunk_overlap,
    persist_directory,
):
    """
    Process uploaded documents, split them into chunks, and store them in a vector database.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit
        ollama_host: URL of the Ollama API
        embedding_model: Name of the embedding model to use
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        persist_directory: Directory to persist the vector database
        
    Returns:
        Chroma: Vector store with the processed documents
    """
    
    # Initialize document list
    documents = []
    
    # Load and process each document
    for uploaded_file in uploaded_files:
        # Create a temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            file_path = temp_file.name
        
        try:
            # Choose the appropriate loader based on file extension
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                logger.info(f"Processing PDF: {uploaded_file.name}")
            elif file_path.endswith('.txt'):
                loader = TextLoader(file_path)
                logger.info(f"Processing TXT: {uploaded_file.name}")
            elif file_path.endswith('.csv'):
                loader = CSVLoader(file_path)
                logger.info(f"Processing CSV: {uploaded_file.name}")
            elif file_path.endswith('.md'):
                loader = UnstructuredMarkdownLoader(file_path)
                logger.info(f"Processing Markdown: {uploaded_file.name}")
            elif file_path.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
                logger.info(f"Processing DOCX: {uploaded_file.name}")
            else:
                logger.warning(f"Unsupported file type: {uploaded_file.name}")
                continue
                
            # Load the document and add it to our documents list
            file_docs = loader.load()
            
            # Add metadata for source tracking
            for doc in file_docs:
                doc.metadata["source"] = uploaded_file.name
                
            documents.extend(file_docs)
            
        except Exception as e:
            logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        finally:
            # Remove the temporary file
            os.unlink(file_path)
    
    if not documents:
        logger.warning("No documents were successfully processed")
        return None
    
    # Split documents into chunks
    logger.info(f"Splitting {len(documents)} documents into chunks of size {chunk_size} with overlap {chunk_overlap}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    
    # Create or update the vector store
    logger.info(f"Using Ollama embeddings model: {embedding_model}")
    embeddings = OllamaEmbeddings(
        model=embedding_model,
        base_url=ollama_host,
    )
    
    # Create or load the persistent vector store
    logger.info(f"Storing vectors in: {persist_directory}")
    
    # Check if the vector store already exists
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        logger.info("Loading existing vector store")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        
        # Add the new documents to the existing vector store
        vectorstore.add_documents(chunks)
    else:
        # Create a new vector store
        logger.info("Creating new vector store")
        vectorstore = Chroma.from_documents(
            chunks,
            embeddings,
            persist_directory=persist_directory,
        )
    
    # Persist the vector store to disk
    vectorstore.persist()
    logger.info("Vector store persisted successfully")
    
    return vectorstore