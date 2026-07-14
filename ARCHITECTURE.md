# Architecture

```text
Streamlit UI (app.py)
        |
        +-- src/db.py -------- SQLite CRUD and validation
        +-- src/matcher.py --- TF-IDF, cosine similarity, skill extraction
        +-- src/analytics.py - KPI and aggregation logic
        +-- src/utils.py ----- Input validation and formatting
```

## Design decisions

### Local-first storage
SQLite removes setup friction and makes the project runnable without a cloud account. Parameterized queries reduce SQL-injection risk. The database file is excluded from Git.

### Explainable matching
The score combines two components:

1. **65% text similarity:** TF-IDF vectors and cosine similarity.
2. **35% skill coverage:** recognized job skills present in the CV.

This is intentionally transparent. It is not presented as a proprietary ATS replica.

### Separation of concerns
Business logic is independent from Streamlit wherever possible, which makes unit testing straightforward and allows a future API or React frontend to reuse the same core.

## Production roadmap

- User authentication and tenant isolation
- PostgreSQL persistence
- Background reminders and email integration
- CV version history
- Configurable skill taxonomy
- REST API using FastAPI
- Observability, audit logs, and encrypted secrets
