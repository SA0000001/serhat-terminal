# Architecture

- **Research Engine (`app/research`)**: IS/OOS split, grid optimization, walk-forward, robustness and multi-metric ranking.
- **Paper Engine (`app/paper_engine`)**: stateful paper positions persisted in DB, restart-safe via `engine_state` table.
- **Risk (`app/risk`)**: independent stop-state decisions and emergency controls.
- **Notifications (`app/notifications`)**: channel abstraction + Telegram implementation.
- **AI Reports (`app/ai_reports`)**: optional diagnostics module with prompt templates.
- **API (`app/api`)**: health, signal webhook, heartbeat endpoints.
- **Dashboard (`app/dashboard`)**: Streamlit pages with TODO hooks to repository/service layer.
- **Storage (`app/storage`)**: SQLAlchemy models + repositories + Alembic migration baseline.

## Safety notes
- Phase 1 is paper-trading only.
- No live order execution included.
- Explicit TODO markers identify areas planned for phase 2.
