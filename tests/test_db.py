import uuid
from sqlmodel import Session, select
from xavierlabs.db.models import Experiment, HypothesisRecord, RunRecord
from xavierlabs.db.session import engine, init_db


def test_db_initialization_and_crud():
    init_db()
    slug = f"test-exp-{uuid.uuid4().hex[:8]}"
    with Session(engine) as session:
        exp = Experiment(slug=slug, topic="Testing convergence of SGD")
        session.add(exp)
        session.commit()
        session.refresh(exp)

        assert exp.id is not None
        assert exp.status == "initialized"

        hyp = HypothesisRecord(
            experiment_id=exp.id,
            title="SGD with momentum converges 2x faster",
            motivation="Acceleration in deep learning",
            theoretical_basis="Polyak momentum dynamics",
            parameters_json="{}",
            metrics_json="[]",
            is_approved=True,
            review_score=8.5,
        )
        session.add(hyp)
        session.commit()

        # Query back
        stmt = select(Experiment).where(Experiment.slug == "test-exp-001")
        retrieved = session.exec(stmt).first()
        assert retrieved is not None
        assert len(retrieved.hypotheses) == 1
        assert retrieved.hypotheses[0].title == "SGD with momentum converges 2x faster"
