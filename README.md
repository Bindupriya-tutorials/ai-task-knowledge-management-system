# AI-Powered Task & Knowledge Management System

A minimal but complete MVP where an **admin** builds a knowledge base of documents and
assigns tasks, and **users** semantically search that knowledge base and complete their
assigned tasks. Built for the "Python Full Stack Assignment (AI)".

---

## Tech stack

| Layer          | Technology                                                        |
|----------------|---------------------------------------------------------------------|
| Backend        | Python, **FastAPI**, SQLAlchemy ORM                                 |
| Database       | **MySQL** (relational schema with PK/FK constraints)                |
| Auth           | **JWT** (python-jose) + bcrypt password hashing, role-based access  |
| AI / Search    | **sentence-transformers** (`all-MiniLM-L6-v2`) for embeddings + **FAISS** as the vector store |
| Frontend       | **React.js** (Vite), React Router, Axios                            |

The semantic search is implemented from first principles as required by the brief:
text is converted to a 384-dim embedding locally with a Sentence-Transformer model,
stored in a FAISS `IndexFlatIP` (cosine similarity via normalized inner product), and
queries are embedded the same way and matched with FAISS nearest-neighbour search.
**No external LLM API is used for the search itself.**

---

## Project structure

```
ai-task-knowledge-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, table creation, role seeding
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models.py            # users, roles, tasks, documents, activity_logs
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── core/
│   │   │   ├── config.py        # env-based settings
│   │   │   ├── security.py      # JWT + bcrypt helpers
│   │   │   └── deps.py          # get_current_user / require_role (RBAC)
│   │   ├── routers/
│   │   │   ├── auth.py          # /auth/register, /auth/login
│   │   │   ├── users.py         # /users (admin)
│   │   │   ├── documents.py     # /documents (upload + list)
│   │   │   ├── tasks.py         # /tasks (create, list+filter, update status)
│   │   │   ├── search.py        # /search (semantic search)
│   │   │   └── analytics.py     # /analytics
│   │   └── services/
│   │       ├── embedding_service.py   # core AI: embeddings + FAISS
│   │       └── activity_service.py    # activity log writer
│   ├── schema.sql                # reference relational schema
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/client.js         # axios instance + JWT interceptor
    │   ├── context/AuthContext.jsx
    │   ├── components/           # Topbar, ProtectedRoute
    │   └── pages/                # Login, Register, AdminDashboard, UserDashboard
    ├── index.html
    ├── package.json
    └── .env.example
```

---

## Setup

### 1. MySQL

Create a database (the app also auto-creates tables on first run, but the DB itself
must exist):

```sql
CREATE DATABASE ai_task_knowledge_db;
```

(`backend/schema.sql` is provided for reference / manual inspection — SQLAlchemy's
`Base.metadata.create_all()` creates the actual tables automatically on startup.)

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your MySQL credentials and a strong SECRET_KEY

uvicorn app.main:app --reload --port 8000
```

The first request that touches the embedding service will download the
`all-MiniLM-L6-v2` model (~90MB) from Hugging Face — this requires internet access
once; it's cached locally afterward. API docs: `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env    # defaults to http://localhost:8000
npm run dev
```

App runs at `http://localhost:5173`.

### 4. Try it out

1. Register an **admin** account and a **user** account (`/register`).
2. Sign in as admin → upload a few `.txt` documents → create and assign a task to the user.
3. Sign in as the user → search the knowledge base → view and complete the assigned task.

---

## API summary

| Method | Endpoint                          | Access       | Notes                                  |
|--------|------------------------------------|--------------|-----------------------------------------|
| POST   | `/auth/register`                   | Public       | Create user or admin account            |
| POST   | `/auth/login`                      | Public       | Returns JWT + role                      |
| GET    | `/users`                           | Admin        | For task-assignment dropdown            |
| POST   | `/documents`                       | Admin        | Upload `.txt`, embeds + indexes it      |
| GET    | `/documents`                       | Authenticated| List knowledge base                     |
| POST   | `/search`                          | Authenticated| Semantic search (FAISS)                 |
| POST   | `/tasks`                           | Admin        | Create & assign a task                  |
| GET    | `/tasks?status=&assigned_to=`      | Authenticated| Dynamic filtering; users see only theirs|
| PATCH  | `/tasks/{id}`                      | Authenticated| Update status (owner or admin)          |
| GET    | `/analytics`                       | Authenticated| Task counts + most-searched queries     |

## Design notes

- **RBAC** is enforced with a `require_role(*roles)` FastAPI dependency reused across routers.
- **Activity logging** happens on login, document upload, search, and task status changes,
  and directly powers the "most searched queries" analytics.
- **Dynamic filtering** on `/tasks` supports `status` and `assigned_to` query params.
- The vector index and its document-id mapping are persisted to `backend/vector_store/`
  so search survives a server restart.
