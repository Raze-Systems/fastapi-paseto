## Sharing feedback

This project is still relatively new and probably has flaws, both in terms of internal usability as well as code quality.\
I have tried my best to however make sure that it is as secure as it can be.\
I also do not yet have a complete understanding of the project, especially the CI/CD and tests. If you find something I missed to adjust, please feel free to let me know.

If you have suggestions for improvements or want to help, feel free to <a href="https://github.com/Chloe-ko/fastapi-paseto-auth/issues/new" target="_blank">open an issue</a> or create a PR with your modifications.

## Developing

If you already cloned the repository and you know that you need to deep dive in the code, here are some guidelines to set up your environment.

This project uses VS Code Development containers.
With the <a href="https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers" target="_blank">Remote - Containers</a> extension installed in VSCode, and Docker installed on your device, VSCode should automatically prompt you about having found a development container configuration file and offer you to open the project in the container.

If not, you can always press F1 and manually click "Remote-Containers: Open Folder in Container" and select the source of this repo that contains the .devcontainer folder.

Any development dependencies will be automatically installed.

You might need to select the correct Python interpreter after opening the project in the container.

### uv

This repository uses <a href="https://docs.astral.sh/uv/" target="_blank">uv</a> for local development. To create the local environment with the development dependencies used for tests, docs, and examples, run:

```bash
$ uv sync --python 3.14
```

This will create a local `.venv/`, install the project in editable mode, and install the `dev` dependency group declared in `pyproject.toml`. The repo also includes a `.python-version` file so `uv` will prefer Python 3.14 for local development.

If you want a production-like local environment without the development tools, run:

```bash
$ uv sync --python 3.14 --no-dev
```

**Using your local FastAPI PASETO Auth**

If you create a Python file that imports and uses FastAPI PASETO Auth, and run it with `uv run` from the project root, it will use your local FastAPI PASETO Auth source code. `uv sync` installs the project as editable by default, so source changes are immediately reflected without reinstalling.

That way, you don't have to reinstall your local version to test every change.

## Docs

The documentation uses <a href="https://www.mkdocs.org/" class="external-link" target="_blank">MkDocs</a>.

All the documentation is in Markdown format in the directory `./docs`.

Many of the sections in the User Guide have blocks of code.

In fact, those blocks of code are not written inside the Markdown, they are Python files in the `./examples/` directory.

And those Python files are included/injected in the documentation when generating the site.

### Docs for tests

Most of the tests actually run against the example source files in the documentation.

This helps making sure that:

* The documentation is up to date.
* The documentation examples can be run as is.
* Most of the features are covered by the documentation, ensured by test coverage.

During local development, there is a script that builds the site and checks for any changes, live-reloading:

```bash
$ bash scripts/docs-live.sh
```

It will serve the documentation on `http://0.0.0.0:5000`.

That way, you can edit the documentation/source files and see the changes live.

## Tests

There is a script that you can run locally to test all the code and generate coverage reports in HTML:

```bash
$ bash scripts/tests.sh
```

If you prefer to invoke the tools directly instead of using the helper scripts, use `uv run`, for example `uv run --python 3.14 pytest -v` or `uv run --python 3.14 mkdocs serve -a 0.0.0.0:5000`.

This command generates a directory `./htmlcov/`, if you open the file `./htmlcov/index.html` in your browser, you can explore interactively the regions of code that are covered by the tests, and notice if there is any region missing.
