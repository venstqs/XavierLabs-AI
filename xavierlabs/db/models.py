from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Experiment(SQLModel, table=True):
    __tablename__ = "experiments"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    topic: str
    status: str = Field(default="initialized")  # initialized, ideating, reviewing, coding, executing, debugging, synthesizing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    hypotheses: List["HypothesisRecord"] = Relationship(back_populates="experiment")
    runs: List["RunRecord"] = Relationship(back_populates="experiment")
    artifacts: List["ArtifactRecord"] = Relationship(back_populates="experiment")


class HypothesisRecord(SQLModel, table=True):
    __tablename__ = "hypotheses"

    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: int = Field(foreign_key="experiments.id")
    title: str
    motivation: str
    theoretical_basis: str
    parameters_json: str
    metrics_json: str
    is_approved: bool = Field(default=False)
    review_score: Optional[float] = None
    review_feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    experiment: Optional[Experiment] = Relationship(back_populates="hypotheses")


class RunRecord(SQLModel, table=True):
    __tablename__ = "runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: int = Field(foreign_key="experiments.id")
    iteration: int = Field(default=1)
    script_content: str
    returncode: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: Optional[float] = None
    metrics_json: Optional[str] = None
    success: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    experiment: Optional[Experiment] = Relationship(back_populates="runs")


class ArtifactRecord(SQLModel, table=True):
    __tablename__ = "artifacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: int = Field(foreign_key="experiments.id")
    artifact_type: str  # script, plot, report_md, paper_tex, paper_pdf, metrics_json
    file_path: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    experiment: Optional[Experiment] = Relationship(back_populates="artifacts")
