#!/bin/bash
set -e

echo "Starting Predictor Service..."

# Set Python path to include the project root
export PYTHONPATH="/app:$PYTHONPATH"

# Stay in the root directory since volumes are mounted there
cd /app

# Fix imports dynamically for Docker environment
echo "Fixing imports for Docker environment..."

# Create __init__.py files if they don't exist in predictor directory
touch predictor/__init__.py
touch predictor/api/__init__.py
touch predictor/models/__init__.py
touch predictor/services/__init__.py
touch predictor/repositories/__init__.py
touch predictor/utils/__init__.py

# Fix main.py imports in predictor directory
sed -i 's/from api import/from predictor.api import/g' predictor/main.py
sed -i 's/from utils import/from predictor.utils import/g' predictor/main.py
sed -i 's/from services import/from predictor.services import/g' predictor/main.py
sed -i 's/from repositories import/from predictor.repositories import/g' predictor/main.py
sed -i 's/from models import/from predictor.models import/g' predictor/main.py

# Fix API module imports
find predictor/api -name "*.py" -exec sed -i 's/from models import/from predictor.models import/g' {} \;
find predictor/api -name "*.py" -exec sed -i 's/from services import/from predictor.services import/g' {} \;
find predictor/api -name "*.py" -exec sed -i 's/from repositories import/from predictor.repositories import/g' {} \;
find predictor/api -name "*.py" -exec sed -i 's/from utils import/from predictor.utils import/g' {} \;

# Fix services module imports
find predictor/services -name "*.py" -exec sed -i 's/from models import/from predictor.models import/g' {} \;
find predictor/services -name "*.py" -exec sed -i 's/from utils import/from predictor.utils import/g' {} \;
find predictor/services -name "*.py" -exec sed -i 's/from repositories import/from predictor.repositories import/g' {} \;

# Fix repositories module imports
find predictor/repositories -name "*.py" -exec sed -i 's/from models import/from predictor.models import/g' {} \;
find predictor/repositories -name "*.py" -exec sed -i 's/from utils import/from predictor.utils import/g' {} \;

# Fix utils module imports
find predictor/utils -name "*.py" -exec sed -i 's/from models import/from predictor.models import/g' {} \;

# Fix __init__.py files
echo "from .endpoints import router" > predictor/api/__init__.py
echo "from .risk_service import RiskService" > predictor/services/__init__.py
echo "from .message_broker import MessageBrokerService" >> predictor/services/__init__.py
echo "from .prediction_service import PredictionService" >> predictor/services/__init__.py
echo "from .mongodb_repository import MongoDBRepository" > predictor/repositories/__init__.py
echo "from .config import Config" > predictor/utils/__init__.py
echo "from .logger import configure_logging, get_logger" >> predictor/utils/__init__.py

echo "Starting FastAPI application..."
exec uvicorn predictor.main:app --host 0.0.0.0 --port 8002 --reload
