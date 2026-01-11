# Nextier Nigeria Violent Conflicts Database

A modern, microservices-based Python backend using FastAPI for real-time signal processing and analysis. The system processes news articles to generate conflict risk signals using AI/ML analysis.

## Architecture Overview

The system has been completely refactored with modern architecture patterns:

- **Message Broker Communication**: RabbitMQ for asynchronous service communication
- **Document Storage**: MongoDB for scalable data persistence
- **Modular Design**: Clean architecture with dependency injection
- **Resilience Patterns**: Circuit breakers, retry mechanisms, and connection pooling
- **Observability**: Structured logging and comprehensive health checks
- **Security**: Enhanced input validation and CORS configuration

## Services

This project consists of three microservices:

1. **Scraper Service** (Port 8000) - News article collection and preprocessing
2. **Intelligence API Service** (Port 8001) - AI-powered event extraction using LLM
3. **Predictor Service** (Port 8002) - Risk scoring and economic data analysis

## Infrastructure Services

- **MongoDB** (Port 27017) - Document storage for articles, events, and risk signals
- **RabbitMQ** (Port 5672/15672) - Message broker for service communication

## Project Structure

```
nextier-nigeria-violent-conflicts-database/
├── docker-compose.yml
├── pytest.ini
├── requirements-test.txt
├── scraper/
│   ├── api/                 # FastAPI routes
│   ├── models/             # Pydantic models
│   ├── services/            # Business logic
│   ├── repositories/       # Data access layer
│   ├── utils/               # Configuration and utilities
│   ├── tests/               # Unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── intelligence-api/
│   ├── api/                 # FastAPI routes
│   ├── models/             # Pydantic models
│   ├── services/            # Business logic (LLM processing)
│   ├── repositories/       # Data access layer
│   ├── utils/               # Configuration and utilities
│   ├── tests/               # Unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── predictor/
│   ├── api/                 # FastAPI routes
│   ├── models/             # Pydantic models
│   ├── services/            # Business logic (risk calculation)
│   ├── repositories/       # Data access layer
│   ├── utils/               # Configuration and utilities
│   ├── tests/               # Unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── tests/
│   └── integration/         # Integration tests
└── data/                    # Sample data files
```

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Ejyke90/nextier-nigeria-violent-conflicts-database.git
cd nextier-nigeria-violent-conflicts-database
```

### 2. Build and Run All Services

```bash
docker-compose up --build
```

This command will:
- Build Docker images for all three services
- Start all services in containers
- Set up networking between services

### 3. Run Services in Detached Mode

```bash
docker-compose up -d
```

### 4. Stop All Services

```bash
docker-compose down
```

## API Endpoints

### Scraper Service (http://localhost:8000)

#### Core Endpoints
- `GET /` - Welcome message
- `GET /health` - Enhanced health check with MongoDB and RabbitMQ status
- `GET /api/v1/scrape` - Trigger news scraping (async)
- `POST /api/v1/scrape` - Trigger news scraping (sync)
- `GET /api/v1/articles` - Retrieve scraped articles

#### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Intelligence API Service (http://localhost:8001)

#### Core Endpoints
- `GET /` - Welcome message
- `GET /health` - Enhanced health check with MongoDB and RabbitMQ status
- `GET /api/v1/analyze` - Trigger article analysis (async)
- `POST /api/v1/analyze` - Trigger article analysis (sync)
- `GET /api/v1/events` - Retrieve parsed events
- `GET /api/v1/status` - Processing status and statistics
- `POST /api/v1/start-processor` - Start background event processor
- `POST /api/v1/stop-processor` - Stop background event processor

#### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Predictor Service (http://localhost:8002)

#### Core Endpoints
- `GET /` - Welcome message
- `GET /health` - Enhanced health check with MongoDB, RabbitMQ, and economic data status
- `GET /api/v1/predict` - Trigger risk prediction (async)
- `POST /api/v1/predict` - Trigger risk prediction (sync)
- `GET /api/v1/signals` - Retrieve risk signals
- `GET /api/v1/status` - Prediction status and statistics
- `POST /api/v1/start-processor` - Start background prediction processor
- `POST /api/v1/stop-processor` - Stop background prediction processor
- `POST /api/v1/initialize-economic-data` - Initialize economic data from CSV

#### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Infrastructure Services

#### RabbitMQ Management UI
- `http://localhost:15672` - RabbitMQ management interface
  - Username: `admin`
  - Password: `password`

#### MongoDB
- `mongodb://localhost:27017` - Direct MongoDB connection
  - Username: `admin`
  - Password: `password`
  - Database: `nextier_signal`

## Development

### Running Individual Services

To run a specific service:

```bash
docker-compose up scraper
# or
docker-compose up intelligence-api
# or
docker-compose up predictor
# or
docker-compose up mongodb rabbitmq  # Infrastructure only
```

### Environment Variables

The services support extensive configuration through environment variables:

#### Common Configuration
- `MONGODB_URL` - MongoDB connection string
- `RABBITMQ_URL` - RabbitMQ connection string
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

#### Service-Specific Configuration
- `OLLAMA_URL` - LLM service URL (Intelligence API)
- `PREMIUM_TIMES_URL` - News source URL (Scraper)
- `POLL_INTERVAL` - Background processing interval
- `MAX_CONNECTIONS` - HTTP connection pool size

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f scraper

# Infrastructure services
docker-compose logs -f mongodb rabbitmq
```

### Accessing Service Containers

```bash
docker exec -it scraper-service bash
docker exec -it intelligence-api-service bash
docker exec -it predictor-service bash
docker exec -it mongodb bash
docker exec -it rabbitmq bash
```

## Testing

### Running Tests

The project includes comprehensive unit and integration tests:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific service tests
pytest scraper/tests/
pytest intelligence-api/tests/
pytest predictor/tests/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=scraper --cov=intelligence-api --cov=predictor

# Run performance tests
pytest -m slow
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test service interactions and data flows
- **Performance Tests**: Test system behavior with large datasets

## Data Flow

1. **Scraper Service** collects news articles and publishes them to RabbitMQ
2. **Intelligence API Service** consumes articles, processes them with LLM, and extracts events
3. **Predictor Service** consumes events, calculates risk scores using economic data
4. **MongoDB** stores all data (articles, events, risk signals)
5. **RabbitMQ** facilitates asynchronous communication between services

## Monitoring & Observability

### Health Checks

All services provide comprehensive health checks:

```bash
# Service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Infrastructure health
curl http://localhost:15672/api/healthchecks  # RabbitMQ
```

### Structured Logging

All services use structured JSON logging with correlation IDs for request tracing.

### Performance Metrics

- Connection pooling metrics
- Message queue depth
- Database query performance
- LLM response times

## Architecture Features

### Resilience Patterns
- **Circuit Breakers**: Prevent cascading failures for external LLM calls
- **Retry Mechanisms**: Exponential backoff for transient failures
- **Connection Pooling**: Efficient HTTP connection management
- **Graceful Degradation**: Services continue operating with reduced functionality

### Security Enhancements
- **Input Validation**: Comprehensive Pydantic model validation
- **CORS Configuration**: Restricted to specific origins
- **Error Sanitization**: Prevent information leakage in error responses

### Performance Optimizations
- **Async Processing**: Non-blocking I/O throughout the stack
- **Caching**: LRU cache for expensive operations
- **Batch Processing**: Efficient handling of multiple items
- **Resource Management**: Proper cleanup and resource pooling

### Observability
- **Structured Logging**: JSON-formatted logs with context
- **Health Checks**: Detailed service dependency monitoring
- **Request Tracing**: Correlation IDs for request flow tracking
- **Performance Metrics**: Built-in performance monitoring

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker logs
docker-compose logs

# Check port conflicts
netstat -tulpn | grep :8000
netstat -tulpn | grep :27017
netstat -tulpn | grep :5672
```

#### MongoDB Connection Issues
```bash
# Check MongoDB container
docker exec -it mongodb mongo -u admin -p password

# Verify database exists
use nextier_signal
show collections
```

#### RabbitMQ Connection Issues
```bash
# Check RabbitMQ status
docker exec -it rabbitmq rabbitmqctl status

# Check queues
docker exec -it rabbitmq rabbitmqctl list_queues
```

#### LLM Service Issues
```bash
# Check Ollama service (if running locally)
curl http://host.docker.internal:11434/api/tags

# Test LLM endpoint
curl -X POST http://host.docker.internal:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:latest", "prompt": "Test", "stream": false}'
```

## Production Deployment

### Environment Configuration
```bash
# Production environment variables
export MONGODB_URL="mongodb://user:pass@prod-mongo:27017/"
export RABBITMQ_URL="amqp://user:pass@prod-rabbitmq:5672/"
export ALLOWED_ORIGINS="https://nextier.example.com"
export LOG_LEVEL="WARNING"
```

### Scaling Services
```bash
# Scale specific services
docker-compose up --scale scraper=3 --scale intelligence-api=2

# Use Docker Swarm or Kubernetes for production scaling
```

### Monitoring Setup
- Set up log aggregation (ELK stack, Grafana, etc.)
- Configure alerting for health check failures
- Monitor queue depths and processing times
- Track database performance metrics

## Contributing

### Development Workflow
1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass (`pytest`)
4. Update documentation
5. Submit pull request

### Code Quality Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage > 80%

## License

[Add your license here]