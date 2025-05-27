Below is a **step-by-step design brief** for a *single-file*, *run-anywhere* prototype that uses **Gradio as the entire front-end (and lightweight back-end)**, and **Ollama-hosted VLM** for all text extraction.

---

## 0️⃣  At-a-glance architecture

```
┌──────────────┐
│  Gradio app  │  (Python)
│  ─ Blocks UI │  • File uploader
│  ─ Logic     │  • Calls Ollama
└───────┬──────┘  • Builds pandas DataFrame  ▲
        │                               CSV/XLXS download
    HTTP JSON                            ▼
        │                         ┌────────────┐
        └────────►  Ollama VLM  ◄─┤ llava:7b   │
                POST /api/generate └────────────┘
```

*No FastAPI, no Redis, no JS bundlers—just Gradio + pandas inside one Python process.*

---

## 1️⃣  Directory layout

```
bizcard-gradio/
├─ app.py            # main script (see §4)
├─ requirements.txt  # deps
└─ README.md         # run instructions
```

If you decide to persist data later, add:

```
├─ db.py             # SQLModel helpers
└─ data/             # SQLite file & temp exports
```

---

## 2️⃣  Dependencies

```text
# requirements.txt
gradio>=4.25          # UI & simple hosting
pandas                # DataFrame + exports
requests              # call Ollama REST
python-dotenv         # read .env for config
```

> **Install**
>
> ```bash
> python -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> ```

---

## 3️⃣  Environment & model

Create **`.env`**:

```env
OLLAMA_URL=http://127.0.0.1:11434/api/generate
OLLAMA_MODEL=llava:7b
```

Run Ollama once to cache the model:

```bash
ollama run llava:7b
```

---

## 4️⃣  `app.py` -– core script

```python
import os, base64, json, uuid, tempfile, pathlib
from dotenv import load_dotenv
import gradio as gr
import pandas as pd
import requests

load_dotenv()
URL   = os.getenv("OLLAMA_URL",  "http://127.0.0.1:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llava:7b")

PROMPT = """
You are a business-card extraction agent.
Return exactly one JSON object with keys:
{name, company, title, phone, email, other}
ONLY output valid JSON. No comments, no markdown.
"""

def extract(files, progress=gr.Progress()):
    rows = []
    for i, f in enumerate(files):
        progress((i, len(files)))          # live bar  :contentReference[oaicite:0]{index=0}
        b64 = base64.b64encode(f.read()).decode()
        resp = requests.post(
            URL,
            json={
                "model": MODEL,
                "prompt": PROMPT,
                "stream": False,
                "images": [f"data:image/jpeg;base64,{b64}"],
            },
            timeout=90,
        )
        rows.append(json.loads(resp.json()["response"]))

    df = pd.DataFrame(rows)

    # write a temp CSV so Gradio's File component can serve it
    tmp = pathlib.Path(tempfile.gettempdir()) / f"cards_{uuid.uuid4().hex}.csv"
    df.to_csv(tmp, index=False)
    return df, str(tmp)

with gr.Blocks(title="BizCard Batch Extractor") as demo:
    gr.Markdown("### Upload business-card images → structured contacts")

    uploader = gr.File(
        file_types=["image"],
        file_count="multiple",
        label="Drop or click to choose *.jpg / *.png",
    )
    out_df = gr.Dataframe(
        headers=["name", "company", "title", "phone", "email", "other"],
        interactive=True,                 # users can tweak cells  :contentReference[oaicite:1]{index=1}
        wrap=True,
        max_height=400,
    )
    out_file = gr.File(label="Download CSV")       # download link  :contentReference[oaicite:2]{index=2}

    uploader.upload(extract, uploader, [out_df, out_file])

demo.launch(server_name="0.0.0.0", server_port=7860)
```

**What users see**

1. Drag-drop any number of images.
2. Progress bar updates while each card is processed.
3. A live, editable table appears.
4. A “Download CSV” link pops up when processing is finished.

---

## 5️⃣  Export to Excel / DB (optional)

### Add Excel

```python
if fmt == "xlsx":
    df.to_excel(tmp.with_suffix(".xlsx"), index=False)
```

Expose a **Radio** or **Dropdown** in Blocks and route to whichever writer the user picked.

### Persist to SQLite

```python
from sqlmodel import SQLModel, Field, Session, create_engine
# define Contact model exactly as before...
engine = create_engine("sqlite:///data/cards.db")
SQLModel.metadata.create_all(engine)

def save_to_db(df):
    with Session(engine) as sess:
        sess.add_all(Contact(**row) for row in df.to_dict(orient="records"))
        sess.commit()
```

Wire that to a **Button** (“Save to DB”).

---

## 6️⃣  Packaging & run commands

### Plain Python (dev)

```bash
python app.py
# open http://localhost:7860
```

### Docker (single container)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV OLLAMA_URL=http://host.docker.internal:11434/api/generate
EXPOSE 7860
CMD ["python", "app.py"]
```

```bash
docker build -t bizcard-gradio .
docker run -p 7860:7860 --network="host" bizcard-gradio
```

(Assumes Ollama is already running on your host.)

---

## 7️⃣  Road-map for “next-level” features

| Feature                | Quick hint                                                                                                                     |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Undo / dedupe**      | add `gr.Button("Remove Duplicates")` → pandas `.drop_duplicates(["phone","email"])`                                            |
| **Custom column sets** | store a JSON list in `~/.config/bizcard_gradio/layout.json`; let a **CheckboxGroup** show/hide columns.                        |
| **Multi-user & auth**  | Front Gradio with Nginx + Basic Auth *or* embed this script inside a FastAPI route using `gr.mount_gradio_app(app)`.           |
| **Long jobs**          | Keep Gradio UI, but call a FastAPI/RQ service; stream partial results back with `yield`.                                       |
| **Cloud deploy**       | Containerize both Ollama GPU and script; push to a single-node VM or Replicate/HF Space (swap Ollama for cloud LLM if needed). |

---

### TL;DR

*For a local demo,* the 100-line `app.py` above is the fastest route from **“pile of JPEGs” → “clean CSV”**.
If/when you outgrow Gradio’s simplicity—swap in FastAPI + JS frontend using the **same VLM call** and data models.

Happy hacking! 🛠️
