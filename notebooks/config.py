import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Assumes the .env file is in the parent directory of 'notebooks'
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Centralized environment variables
KG_VERSION = os.getenv("KG_VERSION")
KG_GIT = os.getenv("KG_GIT")
NEO4J_INSTALL_PATH = os.getenv("NEO4J_INSTALL_PATH")
BIOPORTAL_API_KEY = os.getenv("BIOPORTAL_API_KEY")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATA = os.getenv("NEO4J_DATA")
NEO4J_METADATA = os.getenv("NEO4J_METADATA")

# Centralized path constants
# All paths are relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output_csvs"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def print_config_summary():
    print(f"Project root: {PROJECT_ROOT}")
    print(f"KG version: {KG_VERSION}")
    print(f"Neo4j database: {NEO4J_DATABASE}")
