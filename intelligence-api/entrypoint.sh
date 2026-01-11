#!/bin/bash
set -e

echo "Starting Intelligence API Service..."

# Set Python path to include the project root
export PYTHONPATH="/app:$PYTHONPATH"

# Stay in the root directory since volumes are mounted there
cd /app

# Fix imports dynamically for Docker environment
echo "Fixing imports for Docker environment..."

# Create __init__.py files if they don't exist in intelligence-api directory
touch intelligence-api/__init__.py
touch intelligence-api/api/__init__.py
touch intelligence-api/models/__init__.py
touch intelligence-api/services/__init__.py
touch intelligence-api/repositories/__init__.py
touch intelligence-api/utils/__init__.py

# Fix main.py imports in intelligence-api directory
sed -i 's/from api import/from intelligence_api.api import/g' intelligence-api/main.py
sed -i 's/from utils import/from intelligence_api.utils import/g' intelligence-api/main.py
sed -i 's/from services import/from intelligence_api.services import/g' intelligence-api/main.py
sed -i 's/from repositories import/from intelligence_api.repositories import/g' intelligence-api/main.py
sed -i 's/from models import/from intelligence_api.models import/g' intelligence-api/main.py

# Fix API module imports
find intelligence-api/api -name "*.py" -exec sed -i 's/from models import/from intelligence_api.models import/g' {} \;
find intelligence-api/api -name "*.py" -exec sed -i 's/from services import/from intelligence_api.services import/g' {} \;
find intelligence-api/api -name "*.py" -exec sed -i 's/from repositories import/from intelligence_api.repositories import/g' {} \;
find intelligence-api/api -name "*.py" -exec sed -i 's/from utils import/from intelligence_api.utils import/g' {} \;

# Fix services module imports
find intelligence-api/services -name "*.py" -exec sed -i 's/from models import/from intelligence_api.models import/g' {} \;
find intelligence-api/services -name "*.py" -exec sed -i 's/from utils import/from intelligence_api.utils import/g' {} \;
find intelligence-api/services -name "*.py" -exec sed -i 's/from repositories import/from intelligence_api.repositories import/g' {} \;

# Fix repositories module imports
find intelligence-api/repositories -name "*.py" -exec sed -i 's/from models import/from intelligence_api.models import/g' {} \;
find intelligence-api/repositories -name "*.py" -exec sed -i 's/from utils import/from intelligence_api.utils import/g' {} \;

# Fix utils module imports
find intelligence-api/utils -name "*.py" -exec sed -i 's/from models import/from intelligence_api.models import/g' {} \;

# Fix __init__.py files
echo "from .endpoints import router" > intelligence-api/api/__init__.py
echo "from .llm_service import LLMService" > intelligence-api/services/__init__.py
echo "from .message_broker import MessageBrokerService" >> intelligence-api/services/__init__.py
echo "from .mongodb_repository import MongoDBRepository" > intelligence-api/repositories/__init__.py
echo "from .config import Config" > intelligence-api/utils/__init__.py
echo "from .logging import configure_logging, get_logger" >> intelligence-api/utils/__init__.py

# Create intelligence_api symlink for import compatibility
ln -sf intelligence-api intelligence_api

echo "Starting FastAPI application..."
exec uvicorn intelligence_api.main:app --host 0.0.0.0 --port 8001 --reload
