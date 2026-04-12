from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from harbor.automation_task_registry import (
    AutomationTaskCreate,
    complete_automation_task_observer,
    create_automation_task,
    fail_automation_task_observer,
    get_automation_task,
    list_automation_tasks_for_project,
    mark_automation_task_failed,
    mark_automation_task_running,
    mark_automation_task_succeeded,
    start_automation_task_observer,
)
from harbor.exceptions import InvalidPayloadError, NotFoundError
from harbor.persistence import Base
from harbor.persistence.models import ProjectRecord


@pytest.fixture()
def session(tmp_path):
    db_file = tmp_path / "automation_unit.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_file.as_posix()}")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as s:
        yield s


@pytest.fixture()
def project(session: Session) -> ProjectRecord:
    record = ProjectRecord(
        title="Unit Project",
        short_description="Unit project",
        project_type="standard",
    )
    session.add(record)
    session.flush()
    session.refresh(record)
    return record


def test_create_rejects_unknown_trigger_source(session: Session) -> None:
    with pytest.raises(InvalidPayloadError):
        create_automation_task(
            session,
            AutomationTaskCreate(
                task_kind="draft_handbook",
                trigger_source="cosmic_ray",
            ),
        )


def test_create_rejects_unknown_project(session: Session) -> None:
    with pytest.raises(NotFoundError):
        create_automation_task(
            session,
            AutomationTaskCreate(
                project_id="no-such-project",
                task_kind="draft_handbook",
                trigger_source="manual",
            ),
        )


def test_running_requires_pending(session: Session, project: ProjectRecord) -> None:
    record = create_automation_task(
        session,
        AutomationTaskCreate(
            project_id=project.project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
    )
    mark_automation_task_running(session, record.automation_task_id)
    with pytest.raises(InvalidPayloadError):
        mark_automation_task_running(session, record.automation_task_id)


def test_succeeded_is_terminal(session: Session, project: ProjectRecord) -> None:
    record = create_automation_task(
        session,
        AutomationTaskCreate(
            project_id=project.project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
    )
    mark_automation_task_running(session, record.automation_task_id)
    mark_automation_task_succeeded(session, record.automation_task_id, result_summary="ok")
    with pytest.raises(InvalidPayloadError):
        mark_automation_task_failed(session, record.automation_task_id, "late failure")


def test_failed_sets_error_and_completed(session: Session, project: ProjectRecord) -> None:
    record = create_automation_task(
        session,
        AutomationTaskCreate(
            project_id=project.project_id,
            task_kind="draft_handbook",
            trigger_source="scheduled",
        ),
    )
    updated = mark_automation_task_failed(session, record.automation_task_id, "boom")
    assert updated.status == "failed"
    assert updated.error_message == "boom"
    assert updated.completed_at is not None
    assert updated.started_at is not None


def test_list_orders_by_created_at_desc(session: Session, project: ProjectRecord) -> None:
    first = create_automation_task(
        session,
        AutomationTaskCreate(
            project_id=project.project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
    )
    second = create_automation_task(
        session,
        AutomationTaskCreate(
            project_id=project.project_id,
            task_kind="draft_handbook",
            trigger_source="webhook",
        ),
    )
    items = list_automation_tasks_for_project(session, project.project_id)
    ids = [item.automation_task_id for item in items]
    assert first.automation_task_id in ids
    assert second.automation_task_id in ids


def test_get_unknown_task_raises(session: Session) -> None:
    with pytest.raises(NotFoundError):
        get_automation_task(session, "nonexistent-id")


def test_list_unknown_project_raises(session: Session) -> None:
    with pytest.raises(NotFoundError):
        list_automation_tasks_for_project(session, "nonexistent-project")


@pytest.fixture()
def observer_factory(tmp_path):
    db_file = tmp_path / "automation_observer.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_file.as_posix()}")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as seed:
        project_record = ProjectRecord(
            title="Observer Project",
            short_description="Observer",
            project_type="standard",
        )
        seed.add(project_record)
        seed.commit()
        project_id = project_record.project_id
    return factory, project_id


def test_observer_persists_running_task_then_failed(observer_factory) -> None:
    factory, project_id = observer_factory

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
        session_factory=factory,
    )

    with factory() as check:
        task = get_automation_task(check, task_id)
        assert task.status == "running"
        assert task.started_at is not None

    fail_automation_task_observer(task_id, "boom", session_factory=factory)

    with factory() as check:
        task = get_automation_task(check, task_id)
        assert task.status == "failed"
        assert task.error_message == "boom"
        assert task.completed_at is not None


def test_observer_survives_unrelated_session_rollback(observer_factory) -> None:
    factory, project_id = observer_factory

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
        session_factory=factory,
    )

    with factory() as scratch:
        scratch.add(
            ProjectRecord(
                title="Rolled Back",
                short_description="Will not persist",
                project_type="standard",
            )
        )
        scratch.rollback()

    with factory() as check:
        task = get_automation_task(check, task_id)
        assert task.status == "running"


def test_observer_complete_marks_succeeded(observer_factory) -> None:
    factory, project_id = observer_factory

    task_id = start_automation_task_observer(
        AutomationTaskCreate(
            project_id=project_id,
            task_kind="draft_handbook",
            trigger_source="manual",
        ),
        session_factory=factory,
    )
    complete_automation_task_observer(
        task_id,
        result_summary="handbook_version_id=abc",
        session_factory=factory,
    )

    with factory() as check:
        task = get_automation_task(check, task_id)
        assert task.status == "succeeded"
        assert task.result_summary == "handbook_version_id=abc"
