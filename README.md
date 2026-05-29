# Banking AI-Agent Microservice

Project triển khai Banking AI-Agent theo kiến trúc microservice, sử dụng FastAPI, gRPC, Streamlit, Ollama và Docker Compose.

Mục tiêu chính:

- Tách prototype Banking AI-Agent thành nhiều service độc lập.
- Dùng FastAPI làm API Gateway.
- Dùng gRPC cho service nhận diện intent.
- Dùng Ollama để sinh phản hồi AI qua HTTP.
- Chạy toàn bộ hệ thống bằng Docker Compose.
- Vẫn demo được khi Ollama không khả dụng nhờ fallback rule-based.

---

## 1. Thành phần hệ thống

| Service | Công nghệ | Vai trò | Port trên máy host |
|---|---|---|---|
| `backend` | FastAPI + Uvicorn | Nhận request HTTP, điều phối workflow, gọi intent-service qua gRPC, gọi Ollama qua HTTP | `8000` |
| `intent-service` | Python gRPC | Nhận diện intent từ message người dùng | `50051` |
| `frontend` | Streamlit | Giao diện nhập message và hiển thị kết quả JSON | `8501` |
| Ollama | Ollama HTTP API | Chạy model sinh phản hồi hoặc hỗ trợ phân loại intent | `11434` nếu chạy local |

Endpoint chính:

```txt
GET  /health
GET  /config
POST /run-agent
```

---

## 2. Luồng xử lý

```txt
User Message
    ↓
Frontend Streamlit
    ↓ HTTP
FastAPI Backend /run-agent
    ↓
Intent Node
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

Response của `/run-agent` có dạng:

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
│   │   ├── agent/
│   │   │   └── orchestrator.py
│   │   ├── clients/
│   │   │   ├── base.py
│   │   │   ├── grpc_intent_client.py
│   │   │   ├── ollama_client.py
│   │   │   └── intent_grpc/
│   │   │       ├── intent_service_pb2.py
│   │   │       └── intent_service_pb2_grpc.py
│   │   ├── core/
│   │   │   ├── schemas.py
│   │   │   └── settings.py
│   │   ├── data/
│   │   │   └── policies.py
│   │   ├── nodes/
│   │   │   ├── draft_node.py
│   │   │   ├── intent_node.py
│   │   │   ├── policy_node.py
│   │   │   ├── priority_node.py
│   │   │   ├── router_node.py
│   │   │   └── validation_node.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── Dockerfile
│   ├── interface.py
│   └── requirements.txt
│
├── intent_service/
│   ├── app/
│   ├── clients/
│   ├── core/
│   ├── data/
│   ├── nodes/
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

Các file trong `original_files/` là file template gốc, được giữ nguyên để đối chiếu. Project chạy thật bằng các file ở root và trong từng service.

---

## 4. Yêu cầu cài đặt

Bắt buộc để chạy project bằng Docker:

- Docker Desktop.
- Docker Compose.
- Các port `8000`, `50051`, `8501` chưa bị chiếm.

Không bắt buộc nhưng cần nếu muốn dùng AI response thật:

- Ollama local, hoặc
- Ollama chạy trên Colab/VPS/máy khác và expose URL HTTP.

Project vẫn chạy được khi không có Ollama nhờ fallback:

- `intent-service`: rule-based intent classifier.
- `backend`: fallback draft reply.

---

## 5. Chạy nhanh không cần Ollama

Dùng cách này để kiểm tra Docker, frontend, backend và gRPC trước.

```powershell
cd "D:\bt_lap_trinh\NLP\Ứng dụng\BT4\banking-service-v2"
docker compose up --build
```

Truy cập bằng trình duyệt:

```txt
Frontend: http://localhost:8501
Backend:  http://localhost:8000/health
```

Không mở bằng `http://0.0.0.0:8501`. `0.0.0.0` là địa chỉ bind bên trong container, không phải địa chỉ để truy cập từ trình duyệt.

---

## 6. Chạy với Ollama trên máy local

### 6.1. Cài và chạy Ollama

Mở terminal riêng:

```powershell
ollama serve
```

Mở terminal khác:

```powershell
ollama pull gpt-oss:20b
```

Test Ollama:

```powershell
curl.exe http://localhost:11434/api/generate `
  -H "Content-Type: application/json" `
  -d "{\"model\":\"gpt-oss:20b\",\"prompt\":\"Say OK only\",\"stream\":false}"
```

### 6.2. Cấu hình `.env`

Tạo file `.env` từ `.env.example`:

```powershell
copy .env.example .env
```

Nội dung `.env` cho Ollama local:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
INTENT_MODEL_NAME=gpt-oss:20b
PIP_INDEX_URL=https://pypi.org/simple
```

Không dùng `http://localhost:11434` trong container, vì `localhost` bên trong container là chính container đó, không phải máy host.

### 6.3. Chạy Docker Compose

```powershell
docker compose down
docker compose up --build --force-recreate
```

---

## 7. Chạy với Ollama trên Google Colab

Dùng cách này khi máy local yếu hoặc không đủ RAM/VRAM để chạy model.

### 7.1. Trên Colab

Upload file:

```txt
original_files/[NOTEBOOK] Ollama.ipynb
```

Chọn GPU:

```txt
Runtime → Change runtime type → Hardware accelerator → GPU
```

Chạy Ollama trong notebook. Nếu cần chạy thủ công, dùng cell sau:

```python
!sudo apt update -y
!sudo apt install -y pciutils zstd openssh-client
!curl -fsSL https://ollama.com/install.sh | sh

import os
import subprocess
import time

env = os.environ.copy()
env["OLLAMA_HOST"] = "0.0.0.0:11434"
env["OLLAMA_ORIGINS"] = "*"

process = subprocess.Popen(
    ["ollama", "serve"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

time.sleep(10)
!curl http://localhost:11434/api/tags
```

Pull model:

```python
!ollama pull gpt-oss:20b
```

Nếu Colab không đủ tài nguyên cho `gpt-oss:20b`, dùng model nhẹ hơn:

```python
!ollama pull llama3.2:3b
```

### 7.2. Tạo tunnel bằng Pinggy

Chạy cell sau và giữ cell này chạy liên tục:

```python
!ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -p 443 -R0:localhost:11434 qr@a.pinggy.io
```

Copy URL dạng:

```txt
https://xxxxx.a.free.pinggy.link
```

Test từ máy Windows:

```powershell
curl.exe https://xxxxx.a.free.pinggy.link/api/tags
```

### 7.3. Cấu hình project local dùng URL Colab

Trong file `.env` tại root project:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link
INTENT_MODEL_NAME=gpt-oss:20b
PIP_INDEX_URL=https://pypi.org/simple
```

Nếu dùng model nhẹ hơn:

```env
OLLAMA_BASE_URL=https://xxxxx.a.free.pinggy.link
INTENT_MODEL_NAME=llama3.2:3b
PIP_INDEX_URL=https://pypi.org/simple
```

Chạy lại container:

```powershell
docker compose down
docker compose up --build --force-recreate
```

Lưu ý: nếu Colab ngắt session hoặc cell Pinggy dừng, URL tunnel sẽ không còn dùng được. Khi đó cần chạy lại notebook, lấy URL mới và cập nhật `.env`.

---

## 8. Chạy với Ollama trên thiết bị khác cùng mạng LAN

Trên máy chạy Ollama:

```powershell
$env:OLLAMA_HOST="0.0.0.0:11434"
ollama serve
```

Lấy IP máy đó, ví dụ:

```txt
192.168.1.20
```

Trong `.env` của project:

```env
OLLAMA_BASE_URL=http://192.168.1.20:11434
INTENT_MODEL_NAME=gpt-oss:20b
PIP_INDEX_URL=https://pypi.org/simple
```

Test từ máy chạy Docker:

```powershell
curl.exe http://192.168.1.20:11434/api/tags
```

Nếu không truy cập được, kiểm tra firewall cho port `11434` trên máy chạy Ollama.

---

## 9. Test API Gateway

### 9.1. Health check

```powershell
curl.exe http://localhost:8000/health
```

Kết quả kỳ vọng:

```json
{
  "status": "running",
  "service": "backend",
  "version": "1.0.0"
}
```

### 9.2. Config

```powershell
curl.exe http://localhost:8000/config
```

Kết quả kỳ vọng:

```json
{
  "service": "Banking AI-Agent API Gateway",
  "intent_service_target": "intent-service:50051",
  "ollama_base_url": "http://host.docker.internal:11434",
  "intent_model_name": "gpt-oss:20b",
  "grpc_timeout_seconds": 5.0,
  "http_timeout_seconds": 30.0
}
```

Nếu dùng Colab/Pinggy, `ollama_base_url` phải là URL tunnel đã cấu hình trong `.env`.

### 9.3. Run agent

```powershell
curl.exe -X POST http://localhost:8000/run-agent `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"I lost my card and need urgent support\"}"
```

Kết quả kỳ vọng có đủ các trường:

```json
{
  "message": "I lost my card and need urgent support",
  "intent": "card_lost",
  "confidence": 0.82,
  "reason": "...",
  "priority": "high",
  "policy": "...",
  "validation": "valid",
  "draft_reply": "...",
  "missing_information": [],
  "next_recommended_action": "freeze_card_and_escalate_to_card_support"
}
```

---

## 10. Test frontend

Mở trình duyệt:

```txt
http://localhost:8501
```

Nhập thử message:

```txt
I lost my card and need urgent support
```

Nếu Docker log hiện:

```txt
URL: http://0.0.0.0:8501
```

vẫn phải mở bằng:

```txt
http://localhost:8501
```

---

## 11. Test gRPC intent-service

Khi Docker Compose đang chạy:

```powershell
docker compose exec intent-service python client.py "I want to transfer 100 USD to John"
```

Kết quả kỳ vọng:

```txt
{'intent': 'transfer_money', 'confidence': 0.82, 'reason': '...'}
```

---

## 12. Generate lại gRPC code

Chỉ cần chạy khi sửa `intent_service/intent_service.proto`.

```powershell
cd intent_service
make clean
make
```

Các file sinh ra:

```txt
intent_service_pb2.py
intent_service_pb2_grpc.py
```

Sau khi generate lại trong `intent_service`, nếu contract thay đổi thì cần copy file tương ứng sang:

```txt
backend/app/clients/intent_grpc/
```

Với project hiện tại, contract đã đúng yêu cầu nên không cần generate lại trước khi chạy.

---

## 13. Các lệnh Docker thường dùng

Chạy toàn bộ hệ thống:

```powershell
docker compose up --build
```

Chạy nền:

```powershell
docker compose up --build -d
```

Dừng hệ thống:

```powershell
docker compose down
```

Xem container:

```powershell
docker compose ps
```

Xem log backend:

```powershell
docker compose logs backend --tail=100
```

Xem log intent-service:

```powershell
docker compose logs intent-service --tail=100
```

Xem log frontend:

```powershell
docker compose logs frontend --tail=100
```

Build riêng frontend:

```powershell
docker compose --progress=plain build frontend --no-cache
```

Build lại toàn bộ không cache:

```powershell
docker compose build --no-cache
```

---

## 14. Sửa lỗi thường gặp

### 14.1. Không truy cập được `http://0.0.0.0:8501`

Không dùng `0.0.0.0` để truy cập từ trình duyệt.

Dùng:

```txt
http://localhost:8501
```

hoặc:

```txt
http://127.0.0.1:8501
```

### 14.2. Kiểm tra port mapping

```powershell
docker compose ps
```

Cần thấy mapping tương tự:

```txt
0.0.0.0:8501->8501/tcp
0.0.0.0:8000->8000/tcp
0.0.0.0:50051->50051/tcp
```

### 14.3. Port bị chiếm

Kiểm tra:

```powershell
netstat -ano | findstr :8501
netstat -ano | findstr :8000
netstat -ano | findstr :50051
```

Dừng container cũ:

```powershell
docker compose down
docker ps
```

Nếu còn container chiếm port:

```powershell
docker stop <container_id>
```

### 14.4. `pip install` lỗi `IncompleteRead`

Đây là lỗi mạng khi Docker tải package Python.

Build lại frontend:

```powershell
docker compose --progress=plain build frontend --no-cache
```

Nếu vẫn lỗi, dùng mirror pip:

```powershell
$env:PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
docker compose --progress=plain build frontend --no-cache
docker compose up --build
```

Đổi lại PyPI mặc định:

```powershell
$env:PIP_INDEX_URL="https://pypi.org/simple"
```

### 14.5. Backend không gọi được Ollama local

Kiểm tra `.env`:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Không dùng:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

Test trên máy host:

```powershell
curl.exe http://localhost:11434/api/tags
```

Test trong container backend:

```powershell
docker compose exec backend python -c "import requests; print(requests.get('http://host.docker.internal:11434/api/tags', timeout=5).text)"
```

### 14.6. `/config` vẫn hiện URL Ollama cũ

Chạy lại container:

```powershell
docker compose down
docker compose up --build --force-recreate
```

Kiểm tra file `.env` nằm đúng thư mục root project, cùng cấp với `docker-compose.yml`.

### 14.7. Colab/Pinggy không phản hồi

Nguyên nhân thường gặp:

- Cell Pinggy đã dừng.
- Colab đã ngắt runtime.
- URL tunnel cũ đã hết hiệu lực.
- Model chưa được pull trong Colab.

Cách xử lý:

1. Chạy lại Ollama trong Colab.
2. Chạy lại cell Pinggy.
3. Copy URL mới.
4. Cập nhật `.env`.
5. Chạy lại Docker Compose.

### 14.8. Warning `version is obsolete`

Nếu có warning:

```txt
the attribute `version` is obsolete
```

Đây không phải lỗi build. File `docker-compose.yml` hiện tại không cần khai báo `version`.

---

## 15. Demo script 2–3 phút

Nội dung demo đề xuất:

1. Giới thiệu mục tiêu project: Banking AI-Agent microservice.
2. Mở cấu trúc thư mục, chỉ ra `backend`, `intent_service`, `frontend`.
3. Mở `docker-compose.yml`, chỉ ra 3 service và port `8000`, `50051`, `8501`.
4. Chạy:

   ```powershell
   docker compose up --build
   ```

5. Mở:

   ```txt
   http://localhost:8501
   ```

6. Test backend:

   ```powershell
   curl.exe http://localhost:8000/health
   curl.exe http://localhost:8000/config
   ```

7. Test workflow:

   ```powershell
   curl.exe -X POST http://localhost:8000/run-agent `
     -H "Content-Type: application/json" `
     -d "{\"message\":\"I lost my card and need urgent support\"}"
   ```

8. Chỉ ra output gồm intent, confidence, priority, policy, validation, draft reply và next action.
9. Nêu fallback: nếu Ollama không chạy, hệ thống vẫn trả kết quả demo bằng rule-based classifier và fallback draft.

# NLP_delopment_docker
