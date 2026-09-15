"""Initial schema — all eight HarborAI domain models.

Revision ID: 0001
Revises:
Create Date: 2026-01-15 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enum types ---
    berthstatus = postgresql.ENUM(
        "available", "occupied", "maintenance", name="berthstatus", create_type=False
    )
    berthstatus.create(op.get_bind(), checkfirst=True)

    vesseltype = postgresql.ENUM(
        "container", "bulk", "tanker", "ro_ro", "general",
        name="vesseltype", create_type=False
    )
    vesseltype.create(op.get_bind(), checkfirst=True)

    vesselpriority = postgresql.ENUM(
        "low", "normal", "high", "critical", name="vesselpriority", create_type=False
    )
    vesselpriority.create(op.get_bind(), checkfirst=True)

    vesselstatus = postgresql.ENUM(
        "at_sea", "approaching", "waiting", "berth_assigned",
        "entering_berth", "at_berth", "crane_operations", "departing", "left_port",
        name="vesselstatus", create_type=False
    )
    vesselstatus.create(op.get_bind(), checkfirst=True)

    cranestatus = postgresql.ENUM(
        "available", "operating", "maintenance", name="cranestatus", create_type=False
    )
    cranestatus.create(op.get_bind(), checkfirst=True)

    schedulestatus = postgresql.ENUM(
        "draft", "active", "completed", "cancelled",
        name="schedulestatus", create_type=False
    )
    schedulestatus.create(op.get_bind(), checkfirst=True)

    congestionrisk = postgresql.ENUM(
        "low", "medium", "high", "critical", name="congestionrisk", create_type=False
    )
    congestionrisk.create(op.get_bind(), checkfirst=True)

    # --- Tables (in FK dependency order) ---

    op.create_table(
        "berths",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.VARCHAR(60), nullable=False),
        sa.Column("max_vessel_length_m", sa.FLOAT, nullable=False),
        sa.Column("max_draft_m", sa.FLOAT, nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("available_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("occupied_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("available", "occupied", "maintenance", name="berthstatus"), nullable=False, server_default="available"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_berths_name"),
    )

    op.create_table(
        "vessels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.VARCHAR(120), nullable=False),
        sa.Column("vessel_type", sa.Enum("container", "bulk", "tanker", "ro_ro", "general", name="vesseltype"), nullable=False),
        sa.Column("length_m", sa.FLOAT, nullable=False),
        sa.Column("draft_m", sa.FLOAT, nullable=False),
        sa.Column("container_capacity", sa.Integer, nullable=True),
        sa.Column("containers_to_handle", sa.Integer, nullable=True),
        sa.Column("priority", sa.Enum("low", "normal", "high", "critical", name="vesselpriority"), nullable=False, server_default="normal"),
        sa.Column("scheduled_eta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("predicted_eta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_eta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Enum("at_sea", "approaching", "waiting", "berth_assigned", "entering_berth", "at_berth", "crane_operations", "departing", "left_port", name="vesselstatus"), nullable=False, server_default="at_sea"),
        sa.Column("destination", sa.VARCHAR(120), nullable=True),
        sa.Column("assigned_berth_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("berths.id"), nullable=True),
        sa.Column("expected_handling_duration_h", sa.FLOAT, nullable=True),
        sa.Column("expected_departure", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "cranes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.VARCHAR(60), nullable=False),
        sa.Column("status", sa.Enum("available", "operating", "maintenance", name="cranestatus"), nullable=False, server_default="available"),
        sa.Column("available_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("handling_rate_containers_per_h", sa.FLOAT, nullable=False),
        sa.Column("current_berth_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("berths.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_cranes_name"),
    )

    op.create_table(
        "yard_zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.VARCHAR(60), nullable=False),
        sa.Column("total_capacity", sa.Integer, nullable=False),
        sa.Column("occupied_capacity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_yard_zones_name"),
    )

    op.create_table(
        "routes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.VARCHAR(120), nullable=False),
        sa.Column("route_points", postgresql.JSON, nullable=False),
        sa.Column("nominal_travel_time_h", sa.FLOAT, nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("congestion_factor", sa.FLOAT, nullable=False, server_default="0.0"),
        sa.Column("risk_factor", sa.FLOAT, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_routes_name"),
    )

    op.create_table(
        "schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vessel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vessels.id"), nullable=False),
        sa.Column("berth_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("berths.id"), nullable=False),
        sa.Column("planned_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("planned_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("crane_ids", postgresql.JSON, nullable=True),
        sa.Column("yard_zone_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("yard_zones.id"), nullable=True),
        sa.Column("route_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("routes.id"), nullable=True),
        sa.Column("waiting_time_h", sa.FLOAT, nullable=False, server_default="0.0"),
        sa.Column("status", sa.Enum("draft", "active", "completed", "cancelled", name="schedulestatus"), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "simulation_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("simulation_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.VARCHAR(60), nullable=False),
        sa.Column("vessel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vessels.id"), nullable=True),
        sa.Column("berth_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("berths.id"), nullable=True),
        sa.Column("old_state", postgresql.JSON, nullable=True),
        sa.Column("new_state", postgresql.JSON, nullable=True),
        sa.Column("metadata", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "port_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("simulation_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("berth_utilization", sa.FLOAT, nullable=False),
        sa.Column("crane_utilization", sa.FLOAT, nullable=False),
        sa.Column("yard_utilization", sa.FLOAT, nullable=False),
        sa.Column("waiting_vessel_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("active_vessel_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("upcoming_arrivals_24h", sa.Integer, nullable=False, server_default="0"),
        sa.Column("congestion_risk", sa.Enum("low", "medium", "high", "critical", name="congestionrisk"), nullable=False, server_default="low"),
        sa.Column("snapshot_metadata", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("port_states")
    op.drop_table("simulation_events")
    op.drop_table("schedules")
    op.drop_table("routes")
    op.drop_table("yard_zones")
    op.drop_table("cranes")
    op.drop_table("vessels")
    op.drop_table("berths")

    op.execute("DROP TYPE IF EXISTS congestionrisk")
    op.execute("DROP TYPE IF EXISTS schedulestatus")
    op.execute("DROP TYPE IF EXISTS cranestatus")
    op.execute("DROP TYPE IF EXISTS vesselstatus")
    op.execute("DROP TYPE IF EXISTS vesselpriority")
    op.execute("DROP TYPE IF EXISTS vesseltype")
    op.execute("DROP TYPE IF EXISTS berthstatus")
