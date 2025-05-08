# Sử dụng image Python chính thức
FROM python:3.9.13

# Tạo thư mục ứng dụng
WORKDIR /app

# Copy các file vào container
COPY . .

# Cài đặt thư viện
RUN pip install --upgrade pip && pip install -r requirements.txt

# Chạy ứng dụng
CMD ["python", "run.py"]