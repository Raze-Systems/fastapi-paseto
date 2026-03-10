# Examples

The project examples live in the `examples/` directory and are embedded into the
documentation pages that describe each feature. This index gives you a quick map
from example file to the relevant guide.

| Example | Shows | Related guide |
| --- | --- | --- |
| `examples/basic.py` | Basic login flow with access-token protection | [Basic Usage](usage/basic.md) |
| `examples/json_transport.py` | HTTP JSON body token transport | [JSON Body Tokens](usage/json.md) |
| `examples/websocket.py` | WebSocket auth via headers and query params | [WebSocket Usage](usage/websocket.md) |
| `examples/optional.py` | Optional protection for mixed anonymous/authenticated routes | [Partially Protecting](usage/optional.md) |
| `examples/refresh.py` | Access and refresh token rotation | [Refresh Tokens](usage/refresh.md) |
| `examples/freshness.py` | Fresh-token checks for sensitive routes | [Freshness Tokens](usage/freshness.md) |
| `examples/denylist.py` | In-memory denylist callback | [Revoking Tokens](usage/revoking.md) |
| `examples/denylist_redis.py` | Redis-backed denylist storage | [Revoking Tokens](usage/revoking.md) |
| `examples/additional_claims.py` | Custom claims in token payloads | [Additional claims](advanced-usage/additional-claims.md) |
| `examples/purpose.py` | Local vs public token purpose | [Token Purpose](advanced-usage/purpose.md) |
| `examples/overrides.py` | Route-level transport overrides | [Per-route Overrides](advanced-usage/overrides.md) |
| `examples/validation.py` | Issuer, audience, base64, and custom token types | [Validation and Custom Types](advanced-usage/validation.md) |
| `examples/generate_doc.py` | Manual OpenAPI customization | [Generate Documentation](advanced-usage/generate-docs.md) |
| `examples/multiple_files/` | Multi-module application layout | [Bigger Applications](advanced-usage/bigger-app.md) |
