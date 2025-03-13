from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API Gateway",
    description="Main entry point for the microservices application",
    redirect_slashes=False
)

# Service URLs from environment variables
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")

@app.get("/health")
async def health_check():
    try:
        # Check all service connections
        async with httpx.AsyncClient() as client:
            services = {
                "auth": AUTH_SERVICE_URL,
                "product": PRODUCT_SERVICE_URL,
                "order": ORDER_SERVICE_URL
            }
            
            for name, url in services.items():
                response = await client.get(f"{url}/health")
                if response.status_code != 200:
                    raise HTTPException(status_code=503, detail=f"{name} service unhealthy")
        
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/ready")
async def readiness_check():
    try:
        # Check all service connections
        async with httpx.AsyncClient() as client:
            services = {
                "auth": AUTH_SERVICE_URL,
                "product": PRODUCT_SERVICE_URL,
                "order": ORDER_SERVICE_URL
            }
            
            for name, url in services.items():
                response = await client.get(f"{url}/ready")
                if response.status_code != 200:
                    raise HTTPException(status_code=503, detail=f"{name} service not ready")
        
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the API Gateway"}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(service: str, path: str, request: Request):
    service_urls = {
        "auth": AUTH_SERVICE_URL,
        "products": PRODUCT_SERVICE_URL,
        "orders": ORDER_SERVICE_URL
    }
    
    if service not in service_urls:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Forward the request to the appropriate service
    target_url = f"{service_urls[service]}/{path}"
    
    # Get the request body if any
    body = await request.body()
    headers = dict(request.headers)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers
            )
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
