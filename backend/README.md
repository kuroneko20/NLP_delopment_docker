# Backend API Gateway

FastAPI service exposing:

- `GET /health`
- `GET /config`
- `POST /run-agent`

Run locally from this folder:

```bash
pip install -r requirements.txt
python run.py
```

The backend calls `intent-service:50051` through gRPC when running under Docker Compose and calls Ollama through HTTP using `OLLAMA_BASE_URL`.
