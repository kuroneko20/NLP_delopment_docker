# Banking AI-Agent Microservice

## Video demo: https://drive.google.com/file/d/19xXnEonvF9thZNYr2hs-eiu2aaH55acJ/view?usp=sharing

### Thông tin sinh viên

- Họ và tên: `<Nguyễn Trịnh Quang>`
- MSSV: `<23120345>`

---

## 1. Tổng quan project

Project triển khai **Banking AI-Agent** theo kiến trúc microservice, sử dụng:

- FastAPI cho API Gateway.
- gRPC cho Intent Service.
- Streamlit cho frontend.
- Ollama cho AI response generation.
- Docker Compose để chạy toàn bộ hệ thống.

Hệ thống vẫn demo được khi Ollama không khả dụng nhờ fallback rule-based intent classifier và fallback draft response.

---

## 2. Thành phần hệ thống

| Service | Công nghệ | Vai trò | Port |
|---|---|---|---|
| `backend` | FastAPI + Uvicorn | API Gateway, điều phối workflow | `8000` |
| `intent-service` | Python gRPC | Nhận diện intent | `50051` |
| `frontend` | Streamlit | Giao diện người dùng | `8501` |
| Ollama | HTTP API | Sinh phản hồi AI | `11434` nếu chạy local |

Endpoint backend:

```txt
GET  /health
GET  /config
POST /run-agent
```

---

## 3. Luồng xử lý

```txt
User Message
    ↓
Frontend Streamlit
    ↓ HTTP
FastAPI Backend /run-agent
    ↓ gRPC
Intent Service
    ↓
Priority Node
    ↓
Policy Node
    ↓
Validation Node
    ↓
Router Node
    ↓
Draft Node
    ↓ HTTP
Ollama /api/chat hoặc /api/generate
    ↓
Structured JSON Response
```

Response chính:

```json
{
  "message": "...",
  "intent": "...",
  "confidence": 0.0,
  "reason": "...",
  "priority": "...",
  "policy": "...",
  "validation": "...",
  "draft_reply": "...",
  "missing_information": [],
  "next_recommended_action": "..."
}
```

---

## 4. Cấu trúc thư mục

```txt
banking-service/
├── backend/
│   ├── app/
│   │   ├── agent/orchestrator.py
│   │   ├── clients/
│   │   ├── core/
│   │   ├── data/
│   │   ├── nodes/
│   │   └── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── Dockerfile
│   ├── interface.py
│   └── requirements.txt
│
├── intent_service/
│   ├── client.py
│   ├── server.py
│   ├── intent_service.proto
│   ├── intent_service_pb2.py
│   ├── intent_service_pb2_grpc.py
│   ├── Makefile
│   ├── Dockerfile
│   └── requirements.txt
│
├── original_files/
│   ├── [NOTEBOOK] Ollama.ipynb
│   ├── [TEMPLATE] docker-compose.yml
│   ├── [TEMPLATE] Dockerfile
│   ├── [TEMPLATE] intent_service.proto
│   └── [TEMPLATE] Makefile
│
├── docker-compose.yml
├── .env.example
├── smoke_test.py
└── README.md
```

Các file trong `original_files/` là template gốc và không dùng để chạy trực tiếp.

---

## 5. Yêu cầu cài đặt

Bắt buộc:

- Docker Desktop.
- Docker Compose.
- Port `8000`, `50051`, `8501` chưa bị chiếm.

Tùy chọn:

- Ollama local nếu muốn AI response thật.
- Google Colab + Pinggy nếu máy local yếu.
- Python 3.10+ nếu chạy service thủ công ngoài Docker.

---

## 6. Cấu hình môi trường

Copy file mẫu:

```powershell
copy .env.example .env
```

Cấu hình mặc định cho Ollama local:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
INTENT_MODEL_NAME=gpt-oss:20b
PIP_INDEX_URL=https://pypi.org/simple
```

Nếu dùng Colab/Pinggy:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link
INTENT_MODEL_NAME=gpt-oss:20b
```

Không thêm `/api/chat` hoặc `/api/generate` vào `OLLAMA_BASE_URL`.

Đúng:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link
```

Sai:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link/api/chat
```

---

## 7. Chạy project bằng Docker Compose

Tại thư mục root project:

```powershell
docker compose up --build
```

Sau khi chạy thành công, mở:

```txt
Frontend: http://localhost:8501
Backend:  http://localhost:8000
```

Không dùng các URL sau để mở trình duyệt:

```txt
http://0.0.0.0:8501
http://0.0.0.0:8000
```

`0.0.0.0` chỉ là địa chỉ bind bên trong container.

---

## 8. Chạy Ollama

### 8.1. Ollama local

Chạy trên máy host:

```powershell
ollama serve
ollama pull gpt-oss:20b
```

Test Ollama:

```powershell
curl.exe http://localhost:11434/api/tags
```

Với Docker, dùng:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Không dùng `http://localhost:11434` trong container.

### 8.2. Ollama bằng Colab + Pinggy

Dùng khi máy local không đủ tài nguyên.

Trên Colab:

```python
!curl -fsSL https://ollama.com/install.sh | sh
```

Chạy Ollama:

```python
import os, subprocess, time

env = os.environ.copy()
env["OLLAMA_HOST"] = "0.0.0.0:11434"
env["OLLAMA_ORIGINS"] = "*"

process = subprocess.Popen(["ollama", "serve"], env=env)
time.sleep(10)
```

Pull model:

```python
!ollama pull gpt-oss:20b
```

Tạo tunnel:

```python
!ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -p 443 -R0:localhost:11434 qr@a.pinggy.io
```

Copy URL Pinggy vào `.env` local:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link
INTENT_MODEL_NAME=gpt-oss:20b
```

Nếu Colab yếu, dùng model nhẹ hơn:

```python
!ollama pull llama3.2:3b
```

và sửa:

```env
INTENT_MODEL_NAME=llama3.2:3b
```

---

## 9. Test hệ thống

### 9.1. Test backend

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/config
```

### 9.2. Test workflow `/run-agent`

Khuyến nghị dùng `Invoke-RestMethod` trên PowerShell:

```powershell
$body = @{
  message = "I want to buy a big company, how should I do?"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/run-agent" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

Không gọi `/run-agent` qua port `8501`, vì `8501` là frontend.

### 9.3. Test gRPC intent-service

```powershell
docker compose exec intent-service python client.py "I lost my card and need urgent support"
```

---

## 10. Generate gRPC code

Trong container:

```powershell
docker compose exec intent-service make
```

Hoặc chạy local trong thư mục `intent_service`:

```powershell
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. intent_service.proto
```

File sinh ra:

```txt
intent_service_pb2.py
intent_service_pb2_grpc.py
```

---

## 11. Troubleshooting

### 11.1. Frontend build lỗi `IncompleteRead`

Lỗi này do mạng khi pip tải package.

Cách xử lý:

```powershell
$env:PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
docker compose --progress=plain build frontend --no-cache
docker compose up --build
```

### 11.2. Backend trả `DEADLINE_EXCEEDED`

Nguyên nhân thường gặp: intent-service gọi Ollama chậm hơn timeout gRPC của backend.

Cách xử lý nhanh:

- Restart backend:

```powershell
docker compose restart backend
```

- Nếu vẫn lỗi, tăng timeout trong `docker-compose.yml`:

```yaml
GRPC_TIMEOUT_SECONDS: "30"
HTTP_TIMEOUT_SECONDS: "60"
```

Sau đó recreate:

```powershell
docker compose down
docker compose up --build --force-recreate
```

### 11.3. Không truy cập được web

Dùng:

```txt
http://localhost:8501
http://localhost:8000/health
```

Không dùng:

```txt
http://0.0.0.0:8501
```

Kiểm tra container:

```powershell
docker compose ps
```

### 11.4. PowerShell báo JSON invalid

Dùng `Invoke-RestMethod` thay vì `curl.exe -d`.

### 11.5. Port bị chiếm

```powershell
netstat -ano | findstr :8501
netstat -ano | findstr :8000
```

Dừng container cũ:

```powershell
docker compose down
```
