from fastapi import FastAPI
from api.v1.router.company_router import router as company_router
from api.v1.router.schedule_router import router as schedule_router
from api.v1.router.evaluate_router import router as evaluate_router
import uvicorn
app = FastAPI(title="Campaign Management API")
def start_app():
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True)

# Подключение роутеров
app.include_router(company_router, prefix="")
app.include_router(schedule_router, prefix="/api/v1")
app.include_router(evaluate_router, prefix="/api/v1")
if __name__ == "__main__":
    start_app()



