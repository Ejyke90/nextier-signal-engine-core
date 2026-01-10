# nextier-signal-engine-core

A Dockerized Python backend project using FastAPI with three microservices for signal processing and analysis.

## Services

This project consists of three microservices:

1. **Scraper Service** (Port 8000) - Data scraping and collection
2. **Intelligence API Service** (Port 8001) - Data analysis and intelligence processing
3. **Predictor Service** (Port 8002) - Prediction and forecasting

## Project Structure

```
nextier-signal-engine-core/
├── docker-compose.yml
├── scraper/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── intelligence-api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
└── predictor/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Ejyke90/nextier-signal-engine-core.git
cd nextier-signal-engine-core
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

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /scrape` - Scraping endpoint (to be implemented)
- `GET /docs` - Interactive API documentation (Swagger UI)

### Intelligence API Service (http://localhost:8001)

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /analyze` - Analysis endpoint (to be implemented)
- `GET /docs` - Interactive API documentation (Swagger UI)

### Predictor Service (http://localhost:8002)

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /predict` - Prediction endpoint (to be implemented)
- `GET /docs` - Interactive API documentation (Swagger UI)

## Development

### Running Individual Services

To run a specific service:

```bash
docker-compose up scraper
# or
docker-compose up intelligence-api
# or
docker-compose up predictor
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f scraper
```

### Accessing Service Containers

```bash
docker exec -it scraper-service bash
docker exec -it intelligence-api-service bash
docker exec -it predictor-service bash
```

## Testing

Each service provides an interactive API documentation at `/docs` endpoint:
- Scraper: http://localhost:8000/docs
- Intelligence API: http://localhost:8001/docs
- Predictor: http://localhost:8002/docs

## Next Steps

1. Implement scraping logic in the Scraper service
2. Add data analysis capabilities to the Intelligence API service
3. Develop prediction models in the Predictor service
4. Add database integration (PostgreSQL, MongoDB, etc.)
5. Implement authentication and authorization
6. Add comprehensive unit and integration tests
7. Set up CI/CD pipelines

## License

[Add your license here]