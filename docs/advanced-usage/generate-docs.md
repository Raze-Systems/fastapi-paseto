Because *fastapi-paseto* reads request data directly from Starlette request and
websocket objects, FastAPI will not automatically describe those auth inputs in
OpenAPI for you. If you want the generated docs to show the header or body
contract, extend the OpenAPI schema manually.

Here is an example:

```python hl_lines="37 57-65 69 71-78"
{!../examples/generate_doc.py!}
```
