FROM python:3.11-slim

# Thiết lập thư mục làm việc mặc định trong container
WORKDIR /app

# Copy file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép TOÀN BỘ mã nguồn ở máy ngoài vào thư mục /app trong container
COPY . .

# Khai báo port hệ thống
EXPOSE 8000

# LỆNH CHẠY CHUẨN: Gọi uvicorn, định tuyến app-dir vào thư mục src 
CMD ["uvicorn", "iot_app.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]