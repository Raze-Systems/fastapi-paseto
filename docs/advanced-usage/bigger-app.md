Because *fastapi-paseto* stores configuration on class state shared by all
`AuthPASETO` instances, you only need to call `load_config()` once before your
routes start handling requests.

In a larger FastAPI application, that usually means loading the config in the
module that creates the main `FastAPI` app and then importing routers normally.

## An example file structure

Let's say you have a file structure like this:

```
.
├── multiple_files
│   ├── __init__.py
│   ├── app.py
│   └── routers
│       ├── __init__.py
│       ├── items.py
│       └── users.py
```

Here is an example of `app.py`:

```python
{!../examples/multiple_files/app.py!}
```

Here is an example of `users.py`:

```python
{!../examples/multiple_files/routers/users.py!}
```

Here is an example of `items.py`:

```python
{!../examples/multiple_files/routers/items.py!}
```
