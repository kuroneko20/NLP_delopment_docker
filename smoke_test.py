from pathlib import Path
import importlib.util

root = Path(__file__).parent
pb2_path = root / "intent_service" / "intent_service_pb2.py"
spec = importlib.util.spec_from_file_location("intent_service_pb2", pb2_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

request = module.IntentRequest(message="I lost my card")
decoded_request = module.IntentRequest.FromString(request.SerializeToString())
assert decoded_request.message == "I lost my card"

response = module.IntentResponse(intent="card_lost", confidence=0.82, reason="fallback")
decoded_response = module.IntentResponse.FromString(response.SerializeToString())
assert decoded_response.intent == "card_lost"
assert round(decoded_response.confidence, 2) == 0.82
assert decoded_response.reason == "fallback"

print("protobuf-lite smoke test passed")
