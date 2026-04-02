"""initial schema"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("assets", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("symbol", sa.String(32), unique=True))
    op.create_table("strategies", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(64), unique=True))
    op.create_table("strategy_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("strategies.id")), sa.Column("asset_id", sa.Integer(), sa.ForeignKey("assets.id")), sa.Column("status", sa.String(32)), sa.Column("created_at", sa.DateTime()))
    op.create_table("backtest_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("strategy_run_id", sa.Integer(), sa.ForeignKey("strategy_runs.id")), sa.Column("metrics", sa.JSON()))
    op.create_table("optimization_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("strategy_run_id", sa.Integer(), sa.ForeignKey("strategy_runs.id")), sa.Column("best_params", sa.JSON()))
    op.create_table("walk_forward_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("strategy_run_id", sa.Integer(), sa.ForeignKey("strategy_runs.id")), sa.Column("summary", sa.JSON()))
    op.create_table("signals", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("symbol", sa.String(32)), sa.Column("strategy", sa.String(64)), sa.Column("timeframe", sa.String(16)), sa.Column("direction", sa.String(8)), sa.Column("entry", sa.Float()), sa.Column("stop_loss", sa.Float()), sa.Column("take_profit", sa.Float()), sa.Column("confidence_label", sa.String(32)), sa.Column("reason", sa.Text()), sa.Column("created_at", sa.DateTime()))
    op.create_table("paper_positions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("symbol", sa.String(32)), sa.Column("direction", sa.String(8)), sa.Column("entry_price", sa.Float()), sa.Column("quantity", sa.Float()), sa.Column("stop_loss", sa.Float()), sa.Column("take_profit", sa.Float()), sa.Column("opened_at", sa.DateTime()))
    op.create_table("closed_trades", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("symbol", sa.String(32)), sa.Column("pnl", sa.Float()), sa.Column("reason_code", sa.String(64)), sa.Column("closed_at", sa.DateTime()))
    op.create_table("metrics_snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("payload", sa.JSON()), sa.Column("created_at", sa.DateTime()))
    op.create_table("engine_heartbeat", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("engine_name", sa.String(64)), sa.Column("status", sa.String(32)), sa.Column("last_seen", sa.DateTime()))
    op.create_table("emergency_events", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("event_type", sa.String(64)), sa.Column("reason_code", sa.String(64)), sa.Column("details", sa.JSON()), sa.Column("created_at", sa.DateTime()))
    op.create_table("strategy_health_reports", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("symbol", sa.String(32)), sa.Column("report_text", sa.Text()), sa.Column("created_at", sa.DateTime()))
    op.create_table("config_snapshots", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("config_data", sa.JSON()), sa.Column("created_at", sa.DateTime()))
    op.create_table("engine_state", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("key", sa.String(64), unique=True), sa.Column("state", sa.JSON()), sa.Column("updated_at", sa.DateTime()))


def downgrade() -> None:
    for table in ["engine_state","config_snapshots","strategy_health_reports","emergency_events","engine_heartbeat","metrics_snapshots","closed_trades","paper_positions","signals","walk_forward_runs","optimization_runs","backtest_runs","strategy_runs","strategies","assets"]:
        op.drop_table(table)
