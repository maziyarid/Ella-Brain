"""Bounded store-lock waiting and cleanup; Linux/POSIX only.

Revision 2 (corrected regression): the reviewer's draft tests verbatim,
plus the supervised public-mutation regression at the end (timeout
before load, critique and entity publication). Correction vs the failed
attempt's file (sha256 2345248ee278eeaae0283b090913367141b83bc8f48f849f0d2b28ee698ae236):
the regression's follow-up now creates a valid owner Agent through the
public API AFTER the timeout half, instead of a random nonexistent
owner UUID that the gate correctly rejects ("missing owner"); the
timeout half itself is unchanged, and the holder's release and exit
are now asserted before any follow-up write. Two documented limits:

- The release test proves eventual acquisition after the holder
  releases; it does NOT prove the contender first observed contention
  (its started event fires before _root_lock entry). A first-contention
  signal would need production-code instrumentation and is deferred:
  the timeout test already proves waiting under contention, and the
  release test proves success after release; together they cover the
  behaviour, and neither test claims more than that.
- The cleanup tests assert attempted closure and release of the
  process-local lock only. They do NOT promise that an actual OS-level
  close failure leaves no descriptor behind.
"""

import multiprocessing as mp
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import fcntl
import pytest

from ella_brain import AgentType, Ella, EntityKind, Status, TaskType
from ella_brain import _stages as stages
from ella_brain.errors import MutationRejected


def test_contention_timeout_uses_monotonic_deadline(monkeypatch):
    ticks = iter([10.0, 10.0, 10.05, 10.10])
    sleeps = []

    class Handle:
        def fileno(self):
            return 123

    def busy(fd, operation):
        assert operation == fcntl.LOCK_EX | fcntl.LOCK_NB
        raise BlockingIOError()

    monkeypatch.setattr(stages, "_LOCK_TIMEOUT_SECONDS", 0.10)
    monkeypatch.setattr(stages.time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(stages.time, "sleep", sleeps.append)
    monkeypatch.setattr(stages.fcntl, "flock", busy)

    with pytest.raises(MutationRejected, match="no entity mutation applied"):
        stages._acquire_file_lock(Handle())

    assert sleeps
    assert all(0 < interval <= stages._LOCK_POLL_SECONDS for interval in sleeps)


def test_unexpected_acquisition_error_propagates(monkeypatch):
    class Handle:
        def fileno(self):
            return 123

    def fail(fd, operation):
        raise PermissionError("acquisition denied")

    monkeypatch.setattr(stages.fcntl, "flock", fail)

    with pytest.raises(PermissionError, match="acquisition denied"):
        stages._acquire_file_lock(Handle())


@pytest.mark.parametrize("failure", ["acquire", "unlock", "close"])
def test_cleanup_releases_local_lock(tmp_path, monkeypatch, failure):
    handles = []

    class Handle:
        closed = False

        def fileno(self):
            return 123

        def close(self):
            self.closed = True
            if failure == "close":
                raise OSError("close failed")

    def fake_open(*args, **kwargs):
        handle = Handle()
        handles.append(handle)
        return handle

    def acquire(handle):
        if failure == "acquire":
            raise PermissionError("acquire failed")

    def unlock(fd, operation):
        assert operation == fcntl.LOCK_UN
        if failure == "unlock":
            raise OSError("unlock failed")

    with monkeypatch.context() as patch:
        patch.setattr(stages, "open", fake_open, raising=False)
        patch.setattr(stages, "_acquire_file_lock", acquire)
        patch.setattr(stages.fcntl, "flock", unlock)

        with pytest.raises(OSError, match=f"{failure} failed"):
            with stages._root_lock(tmp_path):
                pass

    assert handles[0].closed
    assert not stages._THREAD_LOCK.locked()

    with stages._root_lock(tmp_path):
        pass


def _holder(root, ready, release):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    with open(root / ".lock", "a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ready.set()
        if not release.wait(10):
            raise RuntimeError("holder supervision deadline expired")


def _contender(root, timeout, started, send):
    try:
        stages._LOCK_TIMEOUT_SECONDS = timeout
        started.set()
        with stages._root_lock(Path(root)):
            send.send(("acquired", None))
    except Exception as exc:
        send.send((type(exc).__name__, str(exc)))
    finally:
        send.close()


@contextmanager
def _held_store(root):
    ctx = mp.get_context("spawn")
    ready = ctx.Event()
    release = ctx.Event()
    holder = ctx.Process(target=_holder, args=(str(root), ready, release))
    holder.start()
    try:
        assert ready.wait(5), "holder did not become ready"
        yield ctx, release, holder
    finally:
        release.set()
        holder.join(3)
        if holder.is_alive():
            holder.terminate()
            holder.join(3)
        if holder.is_alive():
            holder.kill()
            holder.join(3)


def _receive_contender(ctx, root, timeout, release=None):
    started = ctx.Event()
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_contender,
        args=(str(root), timeout, started, send),
    )
    process.start()
    send.close()
    try:
        assert started.wait(5), "contender did not start"
        if release is not None:
            release.set()
        assert receive.poll(5), "contender exceeded supervision deadline"
        result = receive.recv()
        process.join(2)
        assert process.exitcode == 0
        return result
    finally:
        receive.close()
        if process.is_alive():
            process.terminate()
            process.join(3)
        if process.is_alive():
            process.kill()
            process.join(3)


def test_real_process_contention_times_out(tmp_path):
    marker = tmp_path / "sentinel"
    marker.write_bytes(b"unchanged")

    with _held_store(tmp_path) as (ctx, release, holder):
        kind, message = _receive_contender(ctx, tmp_path, 0.15)
        assert kind == "MutationRejected"
        assert "no entity mutation applied" in message
        assert marker.read_bytes() == b"unchanged"
        assert not list(tmp_path.rglob("v*.json"))

    with stages._root_lock(tmp_path):
        pass


def test_real_process_acquires_after_holder_release(tmp_path):
    # Proves eventual acquisition after release only. It does not prove
    # the contender first observed contention: started fires before
    # _root_lock entry, and a first-contention signal would need
    # production-code instrumentation (deferred; see module note).
    with _held_store(tmp_path) as (ctx, release, holder):
        assert _receive_contender(
            ctx, tmp_path, 2.0, release=release
        ) == ("acquired", None)


def test_uncontended_lock_and_in_process_rejection(tmp_path):
    with stages._root_lock(tmp_path):
        with pytest.raises(MutationRejected, match="re-entrant"):
            with stages._root_lock(tmp_path):
                pass

    with stages._root_lock(tmp_path):
        pass


def _public_mutator(root, timeout, started, send):
    """Attempt one real public mutation under a held store lock."""
    try:
        stages._LOCK_TIMEOUT_SECONDS = timeout
        started.set()
        Ella(Path(root)).mutate(
            EntityKind.task,
            uuid4(),
            {
                "type": TaskType.perceive,
                "status": Status.pending,
                "owner": uuid4(),
                "deps": [],
            },
        )
        send.send(("created", None))
    except Exception as exc:
        send.send((type(exc).__name__, str(exc)))
    finally:
        send.close()


def _receive_mutator(ctx, root, timeout):
    started = ctx.Event()
    receive, send = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_public_mutator,
        args=(str(root), timeout, started, send),
    )
    process.start()
    send.close()
    try:
        assert started.wait(5), "mutator did not start"
        assert receive.poll(5), "mutator exceeded supervision deadline"
        result = receive.recv()
        process.join(2)
        assert process.exitcode == 0
        return result
    finally:
        receive.close()
        if process.is_alive():
            process.terminate()
            process.join(3)
        if process.is_alive():
            process.kill()
            process.join(3)


def test_public_mutate_times_out_before_publication(tmp_path):
    """Timeout fires before load, critique and entity publication.

    The contender runs the complete public mutate() path while another
    process holds the store lock. It must fail with the timeout message
    and leave no version file behind; afterwards, once the holder has
    released the lock and exited, the store must accept a fresh
    mutation whose owner Agent is created first through the public API,
    proving no partial state was published.
    """
    with _held_store(tmp_path) as (ctx, release, holder):
        kind, message = _receive_mutator(ctx, tmp_path, 0.15)
        assert kind == "MutationRejected"
        assert "no entity mutation applied" in message
        assert not list(tmp_path.rglob("v*.json"))

    # The holder process released the lock and exited before any
    # follow-up write; the helper joins (then terminates/kills) it.
    assert not holder.is_alive()

    agent_id = uuid4()
    owner = Ella(tmp_path).mutate(
        EntityKind.agent,
        agent_id,
        {
            "type": AgentType.companion,
            "status": Status.active,
            "owner": agent_id,
            "deps": [],
        },
    )
    assert owner.version == 1
    assert Ella(tmp_path).get(EntityKind.agent, agent_id).version == 1

    task_id = uuid4()
    created = Ella(tmp_path).mutate(
        EntityKind.task,
        task_id,
        {
            "type": TaskType.perceive,
            "status": Status.pending,
            "owner": agent_id,
            "deps": [],
        },
    )
    assert created.version == 1
    read_back = Ella(tmp_path).get(EntityKind.task, task_id)
    assert read_back.version == 1
    assert read_back.owner == agent_id
    assert read_back.status == Status.pending
    assert set(tmp_path.rglob("v*.json")) == {
        tmp_path / "agents" / str(agent_id) / "v1.json",
        tmp_path / "tasks" / str(task_id) / "v1.json",
    }
