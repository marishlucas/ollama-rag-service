from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the RAG prompt template
RAG_PROMPT_TEMPLATE = """
You are a helpful AI assistant that answers questions based on provided documents.
Use only the following context to answer the question. If you don't know the answer or can't find it in the context, say "I don't have enough information to answer this question" - don't try to make up an answer.

Context:
{context}

Question: {query}

Answer:
"""

def create_rag_chain(
    vectorstore,
    model_name,
    temperature,
    ollama_host,
    retrieval_k=5,
):
    """
    Create a Retrieval-Augmented Generation chain for question answering.
    
    Args:
        vectorstore: The vector database for retrieval
        model_name: The name of the Ollama model to use
        temperature: Temperature parameter for the model
        ollama_host: URL of the Ollama API
        retrieval_k: Number of documents to retrieve
        
    Returns:
        RetrievalQA: A RAG chain for question answering
    """
    
    logger.info(f"Creating RAG chain with model: {model_name}, temperature: {temperature}")
    
    # Initialize the LLM
    llm = Ollama(
        model=model_name,
        temperature=temperature,
        base_url=ollama_host,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )
    
    # Create the prompt template
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "query"],
    )
    
    # Create the retriever
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": retrieval_k},
    )
    
    # Create and return the RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    
    return qa_chain

def load_vectorstore(
    persist_directory,
    ollama_host,
    embedding_model,
):
    """
    Load a persistent vector store.
    
    Args:
        persist_directory: Directory where the vector store is persisted
        ollama_host: URL of the Ollama API
        embedding_model: Name of the embedding model to use
        
    Returns:
        Chroma: The loaded vector store
    """
    
    logger.info(f"Loading vector store from: {persist_directory}")
    
    embeddings = OllamaEmbeddings(
        model=embedding_model,
        base_url=ollama_host,
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    
    return vectorstore