# Microservices Demo with UV

This is a simple microservices architecture demonstration using FastAPI and UV package manager. The project consists of multiple services that work together to create a complete application.

## Services

1. **API Gateway** - Entry point for all client requests
2. **Auth Service** - Handles user authentication and authorization
3. **Product Service** - Manages product catalog and inventory
4. **Order Service** - Handles order processing and management

## Technology Stack

- Python 3.11+
- FastAPI
- UV (Package Manager)
- Docker
- Redis (for service communication)
- PostgreSQL (for data storage)

## Project Structure

```
microservices-demo/
├── api-gateway/
├── auth-service/
├── product-service/
├── order-service/
└── shared/
```

## Setup Instructions

1. Install UV package manager:
   ```bash
   pip install uv
   ```

2. Install dependencies for each service:
   ```bash
   cd [service-directory]
   uv venv
   uv pip install -r requirements.txt
   ```

3. Start the services:
   ```bash
   docker-compose up
   ```

## Development

Each service is independently deployable and follows these principles:
- Loose coupling
- High cohesion
- Independent data storage
- RESTful communication

## API Documentation

Once the services are running, you can access the API documentation at:
- API Gateway: http://localhost:8000/docs
- Auth Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs
- Order Service: http://localhost:8003/docs
