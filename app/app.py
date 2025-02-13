import uvicorn
from fastapi import FastAPI
from routes import whatsapp_router

app = FastAPI(title="Loris, the AI Personal Finance Assistant API")

app.include_router(whatsapp_router.router, tags=["Loris Whatsapp Inteface"])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8002)
