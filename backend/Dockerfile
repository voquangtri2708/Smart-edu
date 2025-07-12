# Sử dụng image Python slim
FROM python:3.9-slim

# Cài đặt các công cụ build cần thiết (nếu cần)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libc-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục ứng dụng
WORKDIR /app

# Copy các file vào container
COPY . .

# Cài đặt pip và các thư viện trong requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Mở port 5000
EXPOSE 5000

# Chạy ứng dụng Flask trên port 5000
CMD ["python", "run.py"]