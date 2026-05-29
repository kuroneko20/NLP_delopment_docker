# Banking AI-Agent Microservice

## Video demo

Link demo: https://drive.google.com/file/d/19xXnEonvF9thZNYr2hs-eiu2aaH55acJ/view?usp=sharing

### Thông tin sinh viên

- Họ và tên: `Nguyễn Trịnh Quang`
- MSSV: `23120345`

---

## 1. Tổng quan project

Project triển khai **Banking AI-Agent** theo kiến trúc microservice.

Hệ thống gồm:

| Service | Công nghệ | Vai trò | Port |
|---|---|---|---|
| `frontend` | Streamlit | Giao diện nhập message và hiển thị kết quả | `8501` |
| `backend` | FastAPI + Uvicorn | API Gateway, điều phối workflow agent | `8000` |
| `intent-service` | Python gRPC | Nhận diện intent từ message | `50051` |
| `Ollama` | HTTP API | Sinh phản hồi AI | `11434` nếu chạy local |

Backend có các endpoint chính:

```txt
GET  /health
GET  /config
POST /run-agent
```

Hệ thống vẫn chạy demo được nếu Ollama không khả dụng vì có fallback rule-based intent classifier và fallback draft response.

---

## 2. Luồng chạy của project

### 2.1. Luồng tổng thể

```txt
User
 ↓
Streamlit Frontend
 http://localhost:8501
 ↓ HTTP
FastAPI Backend
 http://backend:8000 hoặc http://localhost:8000 từ máy host
 ↓ gRPC
Intent Service
 intent-service:50051
 ↓
Agent Workflow Nodes
 priority → policy → validation → router → draft
 ↓ HTTP
Ollama
 OLLAMA_BASE_URL
 ↓
Structured JSON Response
```

### 2.2. Luồng xử lý `/run-agent`

```txt
1. User nhập message trên frontend hoặc gọi API trực tiếp.
2. Frontend gửi HTTP request tới backend `/run-agent`.
3. Backend gọi intent-service qua gRPC để lấy:
   - intent
   - confidence
   - reason
4. Backend chạy các node còn lại:
   - priority_node: xác định mức ưu tiên.
   - policy_node: lấy policy phù hợp với intent.
   - validation_node: kiểm tra thông tin còn thiếu.
   - router_node: chọn hành động tiếp theo.
   - draft_node: tạo draft reply.
5. Draft node gọi Ollama qua HTTP nếu Ollama khả dụng.
6. Backend trả về JSON cuối cùng cho frontend hoặc API caller.
```

Output chính:

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

## 3. Cấu trúc thư mục

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

Các file trong `original_files/` là file template gốc, được giữ nguyên và không dùng để chạy trực tiếp.

---

## 4. Yêu cầu cài đặt

Bắt buộc:

- Docker Desktop.
- Docker Compose.
- Port `8000`, `50051`, `8501` chưa bị chiếm.

Tùy chọn:

- Ollama local nếu muốn sinh phản hồi AI thật.
- Google Colab + Pinggy nếu máy local yếu.
- Python 3.10+ nếu muốn chạy service thủ công ngoài Docker.

---

## 5. Cấu hình môi trường

Copy file cấu hình mẫu:

```powershell
copy .env.example .env
```

Cấu hình mặc định khi chạy Ollama local trên máy host:

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

## 6. Cách chạy project

### 6.1. Chạy nhanh bằng Docker Compose

Tại thư mục root project:

```powershell
docker compose up --build
```

Sau khi chạy thành công, truy cập:

```txt
Frontend: http://localhost:8501
Backend:  http://localhost:8000
```

Không mở bằng:

```txt
http://0.0.0.0:8501
http://0.0.0.0:8000
```

`0.0.0.0` chỉ là địa chỉ bind bên trong container.

### 6.2. Chạy với Ollama local

Mở terminal riêng trên máy host:

```powershell
ollama serve
ollama pull gpt-oss:20b
```

Test Ollama:

```powershell
curl.exe http://localhost:11434/api/tags
```

Sau đó chạy project:

```powershell
docker compose up --build
```

Trong Docker, service phải dùng:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Không dùng:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

vì `localhost` bên trong container là chính container đó.

### 6.3. Chạy với Ollama trên Colab + Pinggy

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

Tạo tunnel Pinggy:

```python
!ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -p 443 -R0:localhost:11434 qr@a.pinggy.io
```

Copy URL Pinggy vào `.env` local:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link
INTENT_MODEL_NAME=gpt-oss:20b
```

Sau đó chạy lại project local:

```powershell
docker compose down
docker compose up --build --force-recreate
```

Nếu Colab không đủ tài nguyên, dùng model nhẹ hơn:

```python
!ollama pull llama3.2:3b
```

và đổi `.env`:

```env
INTENT_MODEL_NAME=llama3.2:3b
```

---

## 7. Test hệ thống

### 7.1. Test backend

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/config
```

### 7.2. Test workflow `/run-agent`

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

Không gọi `/run-agent` qua port `8501`, vì `8501` là frontend Streamlit.

### 7.3. Test gRPC intent-service

```powershell
docker compose exec intent-service python client.py "I lost my card and need urgent support"
```

### 7.4. Generate lại gRPC code

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

## 8. Troubleshooting ngắn

### Frontend build lỗi `IncompleteRead`

Lỗi do mạng khi pip tải package.

```powershell
$env:PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
docker compose --progress=plain build frontend --no-cache
docker compose up --build
```

### Backend trả `DEADLINE_EXCEEDED`

Nguyên nhân thường gặp: intent-service gọi Ollama chậm hơn timeout gRPC của backend.

Cách xử lý:

```powershell
docker compose restart backend
```

Nếu vẫn lỗi, tăng timeout trong `docker-compose.yml`:

```yaml
GRPC_TIMEOUT_SECONDS: "30"
HTTP_TIMEOUT_SECONDS: "60"
```

Sau đó recreate:

```powershell
docker compose down
docker compose up --build --force-recreate
```

### Không truy cập được web

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

### PowerShell báo JSON invalid

Dùng `Invoke-RestMethod` thay vì `curl.exe -d`.

### Port bị chiếm

```powershell
netstat -ano | findstr :8501
netstat -ano | findstr :8000
docker compose down
```
