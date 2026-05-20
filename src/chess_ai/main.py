import os
import re
import logging
import sys
from typing import List, Dict, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import chess.engine as chess_engine
import chess

from prompts import prompt


ASCII_ART = """
 ██████╗██╗  ██╗███████╗███████╗███████╗     █████╗ ██╗
██╔════╝██║  ██║██╔════╝██╔════╝██╔════╝    ██╔══██╗██║
██║     ███████║█████╗  ███████╗███████╗    ███████║██║
██║     ██╔══██║██╔══╝  ╚════██║╚════██║    ██╔══██║██║
╚██████╗██║  ██║███████╗███████║███████║    ██║  ██║██║
 ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝
"""

ANSI_COLORS = {
    "red": "\033[91m",     
    "orange": "\033[38;5;208m", 
    "yellow": "\033[93m",  
    "green": "\033[92m",   
    "blue": "\033[94m",     
    "anil": "\033[34m",     
    "purple": "\033[95m",
    "white": "\033[97m"
}

RESET_COLORS = "\033[0m"

# Configuration constants
CHESS_PDF_FILENAME = "chess.pdf"
DATABASE_DIR = "database"
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 100
SIMILARITY_SEARCH_K = 5
ENGINE = "stockfish"
ENGINE_ANALYSIS_TIME = 3.0
GEMINI_MODEL = "gemini-3.1-flash-lite"

# Logger setup
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global prompt template for LLM context formatting
PROMPT_TEMPLATE: ChatPromptTemplate = ChatPromptTemplate.from_template(prompt)

# Regex for FEN validation
# Format: board_position active_color castling_rights en_passant_target halfmove fullmove
FEN_REGEX = re.compile(r"(?<=FEN: )([prnbqkPRNBQK1-8/]+ [wb] [KQkq-]+ [a-h1-8-]+ \d+ \d+)")


def request_model(prompt: str) -> None:
    """
    Stream AI response from Google Gemini to stdout.
    output is streamed in real-time for interactive use.
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError(f"API_KEY not found")
    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=api_key
    )
    for chunk in model.stream(prompt):
        if chunk.content:
            print(chunk.content[0]["text"], end="", flush=True)
    print() 


def load_pdf_document() -> List:
    """Load PDF document from the default chess.pdf file."""
    pdf_path = get_path(CHESS_PDF_FILENAME)
    logger.info(f"Loading PDF from: {pdf_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    pdf_loader = PyPDFLoader(pdf_path)
    document = pdf_loader.load()
    logger.info(f"Successfully loaded PDF: {len(document)} pages")
    return document


def split_pdf_document_into_chunks(documents: List) -> List:
    """Split documents into chunks for embedding and retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} document chunks")
    return chunks


def vectorize_pdf_document_chunks(chunks: List) -> None:
    """Create a vector database (Chroma) from document chunks using embeddings."""
    logger.info("Initializing embeddings...")
    embedding = FastEmbedEmbeddings()
    db_path = get_path(DATABASE_DIR)
    logger.info(f"Creating vector database at: {db_path}")
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=db_path
    )
    logger.info("Vector database created successfully!")


def create_db() -> None:
    """Orchestrate the complete database creation pipeline."""
    logger.info("\n=== Starting database creation pipeline ===")
    try:
        document = load_pdf_document()
        chunks = split_pdf_document_into_chunks(document)
        vectorize_pdf_document_chunks(chunks)
        logger.info("=== Database pipeline completed successfully ===")
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        sys.exit(1)


def initialize_database() -> Chroma:
    """Initialize or load the vector database."""
    db_path = get_path(DATABASE_DIR)
    if not os.path.exists(db_path):
        create_db()
    db = Chroma(
        persist_directory=db_path,
        embedding_function=FastEmbedEmbeddings(),
    )
    return db


def get_similarity_chunk(message: str, db: Chroma) -> str:
    """
    Retrieve relevant document chunks from the vector 
    database using similarity search."""
    results = db.similarity_search_with_relevance_scores(message, k=SIMILARITY_SEARCH_K)
    # result_content = [
    #     doc[0].page_content if doc[-1] >= 0.60 else None for doc in results
    #     ]
    result_content = []
    for doc in results:
        #if score >= 0.60
        if doc[-1] >= 0.60:
            result_content.append(doc[0].page_content)
    information = "\n\n----\n\n".join(result_content)
    return information


def get_fen(message: str) -> Optional[str]:
    """Extract FEN notation from user message using regex."""
    fen = FEN_REGEX.search(message)
    return fen.group() if fen else None


def validation_fen(message: str) -> Tuple[Optional[chess.Board], Optional[str]]:
    """Validate FEN extracted from message and return board or error message."""
    fen = get_fen(message)
    if not fen: 
        return None, "FEN not found in message"
    try: 
        board = chess.Board(fen)
    except ValueError: 
        return None, "Invalid FEN notation"
    if not board.is_valid(): 
        return None, "FEN contains illegal positions"
    return board, None


def analyse_position(message: str, engine: chess_engine.SimpleEngine) -> Dict:
    """Analyze chess position using engine chess if FEN is provided."""
    board, error_fen = validation_fen(message)
    if error_fen: 
        return {
            "error_fen": error_fen, 
            "board": None, 
            "engine_analysis": None
        }
    limit = chess_engine.Limit(time=ENGINE_ANALYSIS_TIME)
    return {
        "error_fen": None,
        "board": board,
        "stockfish_analysis": engine.analyse(board, limit)
    }


def get_path(file_name: str) -> str:
    """Build absolute path relative to the module directory."""
    return os.path.join(
        os.path.dirname(__file__),
        file_name
    )


def initialize_engine() -> chess_engine.SimpleEngine:
    """Initialize chess engine."""
    try:
        engine = chess_engine.SimpleEngine.popen_uci(ENGINE)
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        raise


def interactive_loop(db: Chroma, engine: chess_engine.SimpleEngine) -> None:
    """Run the main interactive conversation loop."""
    while True:
        try:
            message = input(f"{ANSI_COLORS['orange']}\nAsk something: {RESET_COLORS}").strip()
            if not message:
                print("Please enter a valid question!")
                continue
            # Analyze position if FEN is provided
            analyse = analyse_position(message, engine)
            # Retrieve relevant context from database
            information = get_similarity_chunk(message, db)
            # Format prompt with context
            formatted_prompt = PROMPT_TEMPLATE.invoke(
                {
                    "context": information,
                    "input": message,
                    "engine_analysis": analyse
                }
            )
            # Stream response from AI model
            request_model(formatted_prompt)
        except KeyboardInterrupt:
            print(f"\n{ANSI_COLORS['green']}👋 Goodbye! {RESET_COLORS}")
            break
        except Exception as e:
            logger.error(f"{ANSI_COLORS['red']}Error: {e}{RESET_COLORS}")
        

def main() -> None:
    """Main entry point for the Chess AI assistant application."""
    print(ANSI_COLORS["green"], ASCII_ART, RESET_COLORS)
    print("* AI assistant specialized in chess")
    print("* CTRL + C to quit\n")
    # Load environment variables
    load_dotenv()
    # Initialize components
    try:
        db = initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    try:
        with initialize_engine() as engine:
            interactive_loop(db, engine)
    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")


if __name__ == "__main__":
    main()