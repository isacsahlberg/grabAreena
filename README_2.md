# grabAreena (new-data-backend branch)

This branch is a **rewrite** of grabAreena to use the JSON schedule endpoint
instead of scraping HTML. It is a work in progress.

## Setup

1. Clone the repo and switch to this branch:

```bash
git clone https://github.com/isacsahlberg/grabAreena.git
cd grabAreena
git checkout new-data-backend
```

2. Install dependencies with [uv](https://github.com/astral-sh/uv):
```bash
uv sync
```
This creates a local `.venv/` and installs `requests` and `termcolor`.

3. To run the playground script:
...
