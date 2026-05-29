from app.core.schemas import IntentResult
from app.core.settings import get_settings
from app.clients.base import ExternalServiceError
from app.clients.intent_grpc import intent_service_pb2, intent_service_pb2_grpc

try:
    import grpc
except ImportError:  # pragma: no cover - container installs grpcio
    grpc = None


class IntentGrpcClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def classify(self, message: str) -> IntentResult:
        if grpc is None:
            raise ExternalServiceError("grpcio is not installed")

        target = self.settings.intent_service_target
        try:
            with grpc.insecure_channel(target) as channel:
                grpc.channel_ready_future(channel).result(timeout=self.settings.grpc_timeout_seconds)
                stub = intent_service_pb2_grpc.IntentServiceStub(channel)
                response = stub.IntentRecognizer(
                    intent_service_pb2.IntentRequest(message=message),
                    timeout=self.settings.grpc_timeout_seconds,
                )
                return IntentResult(
                    intent=response.intent or "unknown",
                    confidence=float(response.confidence),
                    reason=response.reason or "Intent returned by gRPC intent-service.",
                )
        except Exception as exc:
            raise ExternalServiceError(f"intent-service gRPC call failed: {exc}") from exc
