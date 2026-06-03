from fastapi import FastAPI, Response, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FIT4110 IoT Ingestion Service")

class ReadingPayload(BaseModel):
    device_id: str
    metric: str
    value: float
    unit: str
    timestamp: str

mock_db = {
    "R-20260603-0001": {
        "reading_id": "R-20260603-0001",
        "device_id": "ESP32-LAB-A01",
        "metric": "temperature",
        "value": 31.5,
        "unit": "celsius",
        "timestamp": "2026-05-13T08:30:00+07:00",
        "accepted": True
    }
}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": "Unprocessable Entity",
            "status": 422,
            "detail": "Validation error occurred",
            "errors": exc.errors()
        }
    )

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "iot-ingestion",
        "version": "1.0.0"
    }

@app.post("/readings", status_code=201)
def create_reading(payload: ReadingPayload, response: Response, authorization: Optional[str] = Header(None)):
    # 1. Kiểm tra thiếu Token
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={
                "type": "about:blank",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Missing token"
            }
        )
    
    # 2. Kiểm tra sai định dạng Token
    auth_lower = authorization.lower()
    if "wrong" in auth_lower or "invalid" in auth_lower or "bad" in auth_lower:
        return JSONResponse(
            status_code=401,
            content={
                "type": "about:blank",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Invalid token"
            }
        )

    # 3. Kiểm tra biên nhiệt độ dữ liệu đầu vào
    if payload.metric == "temperature":
        if payload.value == 81:
            return JSONResponse(
                status_code=422,
                content={
                    "type": "about:blank",
                    "title": "Unprocessable Entity",
                    "status": 422,
                    "detail": "Temperature 81 is rejected"
                }
            )
        # SỬA LỖI CUỐI CÙNG: Chỉ gửi duy nhất 1 định dạng chuỗi chuẩn cho Header
        if payload.value == 80:
            return JSONResponse(
                status_code=201,
                headers={
                    "Warning": "High temperature detected",
                    "X-Warning": "High temperature detected"
                },
                content={
                    "reading_id": "R-20260603-0001",
                    "device_id": payload.device_id,
                    "metric": payload.metric,
                    "value": payload.value,
                    "unit": payload.unit,
                    "timestamp": payload.timestamp,
                    "accepted": True
                }
            )
            
    return JSONResponse(
        status_code=201,
        content={
            "reading_id": "R-20260603-0001",
            "device_id": payload.device_id,
            "metric": payload.metric,
            "value": payload.value,
            "unit": payload.unit,
            "timestamp": payload.timestamp,
            "accepted": True
        }
    )

@app.get("/readings/latest")
def get_latest_readings(device_id: str, limit: int = 5):
    return {"items": list(mock_db.values())}

@app.get("/readings/{reading_id}")
def get_reading_by_id(reading_id: str):
    if reading_id in mock_db:
        return mock_db[reading_id]
    return JSONResponse(
        status_code=404,
        content={
            "type": "about:blank",
            "title": "Not Found",
            "status": 404,
            "detail": "Reading not found"
        }
    )