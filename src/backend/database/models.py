"""
SQLAlchemy ORM models for HarborAI.

All eight core domain entities are defined here.
Enums are defined as Python Enum classes and mapped to PostgreSQL native ENUMs.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    FLOAT,
    JSON,
    VARCHAR,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class VesselType(str, enum.Enum):
    container = "container"
    bulk = "bulk"
    tanker = "tanker"
    ro_ro = "ro_ro"
    general = "general"


class VesselPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class VesselStatus(str, enum.Enum):
    at_sea = "at_sea"
    approaching = "approaching"
    waiting = "waiting"
    berth_assigned = "berth_assigned"
    entering_berth = "entering_berth"
    at_berth = "at_berth"
    crane_operations = "crane_operations"
    departing = "departing"
    left_port = "left_port"


class BerthStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"


class CraneStatus(str, enum.Enum):
    available = "available"
    operating = "operating"
    maintenance = "maintenance"


class ScheduleStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class CongestionRisk(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# ---------------------------------------------------------------------------
# Helper: shared timestamp columns via mixin
# ---------------------------------------------------------------------------


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Berth(TimestampMixin, Base):
    __tablename__ = "berths"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(60), nullable=False, unique=True)
    max_vessel_length_m: Mapped[float] = mapped_column(FLOAT, nullable=False)
    max_draft_m: Mapped[float] = mapped_column(FLOAT, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    available_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    occupied_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[BerthStatus] = mapped_column(
        Enum(BerthStatus, name="berthstatus"), nullable=False, default=BerthStatus.available
    )

    # back-references (populated by FK owners)
    vessels: Mapped[list["Vessel"]] = relationship(
        "Vessel", back_populates="assigned_berth", foreign_keys="Vessel.assigned_berth_id"
    )
    cranes: Mapped[list["Crane"]] = relationship(
        "Crane", back_populates="current_berth"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="berth"
    )
    simulation_events: Mapped[list["SimulationEvent"]] = relationship(
        "SimulationEvent", back_populates="berth"
    )


class Vessel(TimestampMixin, Base):
    __tablename__ = "vessels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(120), nullable=False)
    vessel_type: Mapped[VesselType] = mapped_column(
        Enum(VesselType, name="vesseltype"), nullable=False
    )
    length_m: Mapped[float] = mapped_column(FLOAT, nullable=False)
    draft_m: Mapped[float] = mapped_column(FLOAT, nullable=False)
    container_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    containers_to_handle: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[VesselPriority] = mapped_column(
        Enum(VesselPriority, name="vesselpriority"),
        nullable=False,
        default=VesselPriority.normal,
    )
    scheduled_eta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    predicted_eta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_eta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[VesselStatus] = mapped_column(
        Enum(VesselStatus, name="vesselstatus"),
        nullable=False,
        default=VesselStatus.at_sea,
    )
    destination: Mapped[str | None] = mapped_column(VARCHAR(120), nullable=True)
    # One-way FK: Vessel → Berth (no reverse FK on Berth)
    assigned_berth_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("berths.id"), nullable=True
    )
    expected_handling_duration_h: Mapped[float | None] = mapped_column(
        FLOAT, nullable=True
    )
    expected_departure: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    assigned_berth: Mapped["Berth | None"] = relationship(
        "Berth", back_populates="vessels", foreign_keys=[assigned_berth_id]
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="vessel"
    )
    simulation_events: Mapped[list["SimulationEvent"]] = relationship(
        "SimulationEvent", back_populates="vessel"
    )


class Crane(TimestampMixin, Base):
    __tablename__ = "cranes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(60), nullable=False, unique=True)
    status: Mapped[CraneStatus] = mapped_column(
        Enum(CraneStatus, name="cranestatus"), nullable=False, default=CraneStatus.available
    )
    available_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    handling_rate_containers_per_h: Mapped[float] = mapped_column(FLOAT, nullable=False)
    current_berth_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("berths.id"), nullable=True
    )

    current_berth: Mapped["Berth | None"] = relationship(
        "Berth", back_populates="cranes"
    )


class YardZone(TimestampMixin, Base):
    __tablename__ = "yard_zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(60), nullable=False, unique=True)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    occupied_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="yard_zone"
    )


class Route(TimestampMixin, Base):
    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(120), nullable=False, unique=True)
    route_points: Mapped[dict] = mapped_column(JSON, nullable=False)
    nominal_travel_time_h: Mapped[float] = mapped_column(FLOAT, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    congestion_factor: Mapped[float] = mapped_column(FLOAT, nullable=False, default=0.0)
    risk_factor: Mapped[float] = mapped_column(FLOAT, nullable=False, default=0.0)

    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="route"
    )


class Schedule(TimestampMixin, Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vessel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vessels.id"), nullable=False
    )
    berth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("berths.id"), nullable=False
    )
    planned_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    planned_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # Denormalised list of crane UUIDs (strings) for Phase 1
    crane_ids: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    yard_zone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("yard_zones.id"), nullable=True
    )
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True
    )
    waiting_time_h: Mapped[float] = mapped_column(FLOAT, nullable=False, default=0.0)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus, name="schedulestatus"),
        nullable=False,
        default=ScheduleStatus.draft,
    )

    vessel: Mapped["Vessel"] = relationship("Vessel", back_populates="schedules")
    berth: Mapped["Berth"] = relationship("Berth", back_populates="schedules")
    yard_zone: Mapped["YardZone | None"] = relationship(
        "YardZone", back_populates="schedules"
    )
    route: Mapped["Route | None"] = relationship("Route", back_populates="schedules")


class SimulationEvent(Base):
    """Immutable event log — no updated_at."""

    __tablename__ = "simulation_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    simulation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    event_type: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    vessel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vessels.id"), nullable=True
    )
    berth_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("berths.id"), nullable=True
    )
    old_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    vessel: Mapped["Vessel | None"] = relationship(
        "Vessel", back_populates="simulation_events"
    )
    berth: Mapped["Berth | None"] = relationship(
        "Berth", back_populates="simulation_events"
    )


class PortState(Base):
    """Immutable snapshot log — no updated_at."""

    __tablename__ = "port_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    simulation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    berth_utilization: Mapped[float] = mapped_column(FLOAT, nullable=False)
    crane_utilization: Mapped[float] = mapped_column(FLOAT, nullable=False)
    yard_utilization: Mapped[float] = mapped_column(FLOAT, nullable=False)
    waiting_vessel_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    active_vessel_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    upcoming_arrivals_24h: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    congestion_risk: Mapped[CongestionRisk] = mapped_column(
        Enum(CongestionRisk, name="congestionrisk"),
        nullable=False,
        default=CongestionRisk.low,
    )
    snapshot_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
