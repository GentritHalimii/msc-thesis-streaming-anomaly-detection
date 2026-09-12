"""A one-at-a-time job queue for re-running the study from the browser.

The experiments in this project compete for every core on the machine, so
running two of them at once would not be faster and would corrupt the timing
columns that the thesis reports. The queue is therefore strictly serial: one
worker thread, a FIFO of pending jobs, and a log buffer per job that the
browser tails over server-sent events.

Nothing here accepts a command line. A request names a catalogue id, the
catalogue supplies the module and its arguments, and anything unknown is
rejected before a process is created.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from queue import Empty, Queue
from typing import Any

from src.config import REPO_ROOT
from webapp.catalog import resolve

MAX_LINES = 4000
PENDING, RUNNING, DONE, FAILED, CANCELLED = "pending", "running", "done", "failed", "cancelled"


@dataclass
class Step:
    experiment_id: str
    title: str
    command: list[str]
    status: str = PENDING
    started: str | None = None
    finished: str | None = None
    returncode: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "command": " ".join(self.command[2:]),
            "status": self.status,
            "started": self.started,
            "finished": self.finished,
            "returncode": self.returncode,
        }


@dataclass
class Job:
    id: str
    target: str
    label: str
    steps: list[Step]
    status: str = PENDING
    created: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started: str | None = None
    finished: str | None = None
    error: str | None = None
    _lines: deque[str] = field(default_factory=lambda: deque(maxlen=MAX_LINES))
    _offset: int = 0  # lines already dropped from the left of the ring buffer
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _process: subprocess.Popen | None = None
    _cancel: bool = False

    # -- log buffer ---------------------------------------------------------
    def append(self, line: str) -> None:
        with self._lock:
            if len(self._lines) == self._lines.maxlen:
                self._offset += 1
            self._lines.append(line.rstrip("\n"))

    def lines_from(self, index: int) -> tuple[int, list[str]]:
        """Lines produced at or after `index`, plus the next index to ask for."""
        with self._lock:
            start = max(index - self._offset, 0)
            chunk = list(self._lines)[start:]
            return self._offset + len(self._lines), chunk

    @property
    def n_lines(self) -> int:
        with self._lock:
            return self._offset + len(self._lines)

    def as_dict(self, with_steps: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "target": self.target,
            "label": self.label,
            "status": self.status,
            "created": self.created,
            "started": self.started,
            "finished": self.finished,
            "error": self.error,
            "n_lines": self.n_lines,
            "n_steps": len(self.steps),
            "n_done": sum(1 for s in self.steps if s.status in (DONE, FAILED, CANCELLED)),
        }
        if with_steps:
            payload["steps"] = [s.as_dict() for s in self.steps]
        return payload


class JobRunner:
    """Serial worker. Start it once per process."""

    def __init__(self, max_history: int = 60) -> None:
        self._queue: Queue[str] = Queue()
        self._jobs: dict[str, Job] = {}
        self._order: deque[str] = deque(maxlen=max_history)
        self._current: str | None = None
        self._lock = threading.Lock()
        self._worker = threading.Thread(target=self._loop, name="job-runner", daemon=True)
        self._worker.start()

    # -- public API ---------------------------------------------------------
    def submit(self, target: str) -> Job:
        experiments = resolve(target)  # raises KeyError for anything unknown
        steps = [
            Step(
                experiment_id=exp.id,
                title=exp.title,
                command=[sys.executable, "-u", "-m", exp.module, *exp.args],
            )
            for exp in experiments
        ]
        label = experiments[0].title if len(experiments) == 1 else f"{target} ({len(steps)} hapa)"
        job = Job(id=uuid.uuid4().hex[:12], target=target, label=label, steps=steps)
        with self._lock:
            self._jobs[job.id] = job
            self._order.append(job.id)
        job.append(f"[radha] {label} u vendos në radhë")
        self._queue.put(job.id)
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            ids = list(self._order)[-limit:][::-1]
        return [self._jobs[i].as_dict(with_steps=False) for i in ids if i in self._jobs]

    def active(self) -> dict[str, Any] | None:
        with self._lock:
            current = self._current
        job = self._jobs.get(current) if current else None
        return job.as_dict() if job else None

    def queued(self) -> list[dict[str, Any]]:
        with self._lock:
            ids = [i for i in self._order if self._jobs[i].status == PENDING and i != self._current]
        return [self._jobs[i].as_dict(with_steps=False) for i in ids]

    def is_busy(self) -> bool:
        with self._lock:
            return self._current is not None

    def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None or job.status in (DONE, FAILED, CANCELLED):
            return False
        job._cancel = True
        process = job._process
        if process is not None and process.poll() is None:
            job.append("[radha] u kërkua ndalimi")
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                process.terminate()
            return True
        # still queued: it will be skipped when the worker reaches it
        job.status = CANCELLED
        job.finished = datetime.now(UTC).isoformat()
        job.append("[radha] u anulua para se të niste")
        return True

    # -- worker -------------------------------------------------------------
    def _loop(self) -> None:
        while True:
            try:
                job_id = self._queue.get(timeout=0.5)
            except Empty:
                continue
            job = self._jobs.get(job_id)
            if job is None or job.status == CANCELLED:
                continue
            with self._lock:
                self._current = job_id
            try:
                self._run(job)
            except Exception as exc:  # noqa: BLE001 - the worker must never die
                job.status = FAILED
                job.error = f"{type(exc).__name__}: {exc}"
                job.append(f"[gabim] {job.error}")
            finally:
                job.finished = datetime.now(UTC).isoformat()
                with self._lock:
                    self._current = None

    def _run(self, job: Job) -> None:
        job.status = RUNNING
        job.started = datetime.now(UTC).isoformat()
        for index, step in enumerate(job.steps, start=1):
            if job._cancel:
                step.status = CANCELLED
                continue
            step.status = RUNNING
            step.started = datetime.now(UTC).isoformat()
            job.append("")
            job.append(f"=== [{index}/{len(job.steps)}] {step.title} ===")
            job.append(f"$ {' '.join(step.command[1:])}")
            code = self._spawn(job, step)
            step.returncode = code
            step.finished = datetime.now(UTC).isoformat()
            if job._cancel:
                step.status = CANCELLED
                job.status = CANCELLED
                job.append("[radha] u ndal")
                return
            if code != 0:
                step.status = FAILED
                job.status = FAILED
                job.error = f"{step.title} dështoi me kod {code}"
                job.append(f"[gabim] {job.error}")
                return
            step.status = DONE
            job.append(f"[ok] {step.title}")
        job.status = DONE
        job.append("")
        job.append("[përfundoi] të gjitha hapat kaluan")

    def _spawn(self, job: Job, step: Step) -> int:
        env = dict(os.environ, PYTHONUNBUFFERED="1", MPLBACKEND="Agg")
        process = subprocess.Popen(  # noqa: S603 - argv comes from the catalogue only
            step.command,
            cwd=REPO_ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
        job._process = process
        assert process.stdout is not None
        for line in process.stdout:
            job.append(line)
        process.stdout.close()
        code = process.wait()
        job._process = None
        return code


_RUNNER: JobRunner | None = None


def runner() -> JobRunner:
    global _RUNNER
    if _RUNNER is None:
        _RUNNER = JobRunner()
    return _RUNNER


def sse_stream(job: Job, start: int = 0, poll: float = 0.25):
    """Generator of server-sent events: log lines, then a terminal status.

    A tick carries the whole job object, so it is only sent when something in
    it actually changed. Without that guard a quiet job that imports pandas
    for ten seconds would push forty identical payloads down the socket.
    """
    index = start
    yield _event("hello", {"job": job.as_dict(), "from": index})
    last_state: str | None = None
    while True:
        index, chunk = job.lines_from(index)
        if chunk:
            yield _event("log", {"lines": chunk, "next": index})
        state = job.as_dict(with_steps=True)
        serialized = json.dumps(state, ensure_ascii=False, sort_keys=True)
        if job.status in (DONE, FAILED, CANCELLED) and not chunk:
            yield _event("end", {"job": state})
            return
        if not chunk:
            if serialized != last_state:
                last_state = serialized
                yield _event("tick", {"job": state})
            else:
                yield ": keep-alive\n\n"
            time.sleep(poll)


def _event(name: str, payload: dict[str, Any]) -> str:
    return f"event: {name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
