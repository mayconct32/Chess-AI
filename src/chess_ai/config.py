"""Configuration module for ChessAI application.

Contains all constants, paths, and configuration parameters used throughout the application.
"""

# File and directory paths
CHESS_PDF_FILENAME = "chess.pdf"
DATABASE_DIR = "database"

# Text splitting configuration
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 100

# RAG configuration
SIMILARITY_SEARCH_K = 5
SIMILARITY_SCORE_THRESHOLD = 0.60

# Engine configuration
ENGINE = "stockfish"
ENGINE_ANALYSIS_TIME = 3.0

# AI Model configuration
GEMINI_MODEL = "gemini-3.1-flash-lite"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_LEVEL_DEFAULT = "ERROR"

# Regex pattern for FEN validation
# Format: board_position active_color castling_rights en_passant_target halfmove fullmove
FEN_REGEX_PATTERN = r"(?<=FEN: )([prnbqkPRNBQK1-8/]+ [wb] [KQkq-]+ [a-h1-8-]+ \d+ \d+)"
