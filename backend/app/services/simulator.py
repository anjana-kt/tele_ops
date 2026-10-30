from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class DeviceStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    OUTCOME_UNKNOWN = "outcome_unknown"


@dataclass(frozen=True, slots=True)
class DeviceResult:
    device_id: str
    command_id: str
    status: DeviceStatus
    duration_seconds: float
    message: str


class DeviceCommandError(Exception):
    """The simulator completed a command with a known failure."""


class SimulatedDevice:
    """One simulated test station.

    Each device serializes its own commands with a lock. Different devices
    can execute concurrently. Later, this boundary can be replaced by a real
    device adapter without changing the job orchestration API.
    """

    def __init__(self, device_id: str, *, base_delay: float = 1.0) -> None:
        self.device_id = device_id
        self.base_delay = base_delay
        self.status = DeviceStatus.IDLE
        self._command_lock = asyncio.Lock()

    async def execute(
        self,
        command_id: str,
        *,
        fail: bool = False,
        delay_seconds: float | None = None,
        timeout_seconds: float = 3.0,
    ) -> DeviceResult:
        """Execute one simulated command and return a typed outcome.

        A timeout is marked OUTCOME_UNKNOWN: the command may have started,
        so callers must not assume that retrying is safe.
        """
        async with self._command_lock:
            started = time.perf_counter()
            delay = self.base_delay if delay_seconds is None else delay_seconds
            self.status = DeviceStatus.RUNNING

            try:
                await asyncio.wait_for(
                    self._perform(delay_seconds=delay, fail=fail),
                    timeout=timeout_seconds,
                )
            except TimeoutError:
                self.status = DeviceStatus.OUTCOME_UNKNOWN
                return DeviceResult(
                    device_id=self.device_id,
                    command_id=command_id,
                    status=self.status,
                    duration_seconds=time.perf_counter() - started,
                    message=(
                        f"Timed out after {timeout_seconds:.2f}s; "
                        "device outcome is unknown"
                    ),
                )
            except DeviceCommandError as exc:
                self.status = DeviceStatus.FAILED
                return DeviceResult(
                    device_id=self.device_id,
                    command_id=command_id,
                    status=self.status,
                    duration_seconds=time.perf_counter() - started,
                    message=str(exc),
                )
            else:
                self.status = DeviceStatus.SUCCEEDED
                return DeviceResult(
                    device_id=self.device_id,
                    command_id=command_id,
                    status=self.status,
                    duration_seconds=time.perf_counter() - started,
                    message="Command completed successfully",
                )

    async def _perform(self, *, delay_seconds: float, fail: bool) -> None:
        await asyncio.sleep(delay_seconds)
        if fail:
            raise DeviceCommandError(
                f"Simulated command failure on {self.device_id}"
            )


async def execute_batch(
    devices: Sequence[SimulatedDevice],
    *,
    fail_device_id: str | None = None,
    slow_device_id: str | None = None,
) -> list[DeviceResult]:
    """Run one command per device concurrently and retain every outcome."""
    tasks = []
    for device in devices:
        is_slow = device.device_id == slow_device_id
        tasks.append(
            device.execute(
                command_id=f"cmd-{device.device_id}",
                fail=device.device_id == fail_device_id,
                delay_seconds=5.0 if is_slow else None,
                timeout_seconds=2.0,
            )
        )

    # execute() converts expected device failures/timeouts into typed results,
    # so gather can collect every device's outcome in input order.
    return await asyncio.gather(*tasks)


async def main() -> None:
    devices = [
        SimulatedDevice(f"station-{number}", base_delay=1.0 + number * 0.1)
        for number in range(1, 6)
    ]

    print("SiliconOps simulator starting: 5 stations")
    started = time.perf_counter()
    results = await execute_batch(
        devices,
        fail_device_id="station-3",
        slow_device_id="station-5",
    )
    elapsed = time.perf_counter() - started

    for result in results:
        print(
            f"{result.device_id:10} | {result.status.value:15} | "
            f"{result.duration_seconds:5.2f}s | {result.message}"
        )
    print(f"Batch finished in {elapsed:.2f}s")


class TrackingDeviceSequential(SimulatedDevice):
    def __init__(self, device_id):
        super().__init__(device_id)
        self.active = 0
        self.max_active = 0

    async def _perform(self, *, delay_seconds, fail):
        self.active += 1
        self.max_active = max(self.max_active, self.active)

        try:
            await asyncio.sleep(delay_seconds)
            if fail:
                raise DeviceCommandError(
                    f"Simulated command failure on {self.device_id}"
                )
        finally:
            self.active -= 1

class TrackingDeviceOverlap(SimulatedDevice):
            both_started = asyncio.Event()
            def __init__(self, device_id, tracker):
                super().__init__(device_id)
                self.tracker = tracker

            async def _perform(self, *, delay_seconds, fail):
                tracker = self.tracker
                tracker["active"] += 1
                tracker["max_active"] = max(
                    tracker["max_active"], tracker["active"]
                )

                if tracker["active"] >= 2:
                    self.both_started.set()

                try:
                    await asyncio.wait_for(
                        self.both_started.wait(),
                        timeout=0.5,
                    )
                    await asyncio.sleep(delay_seconds)
                finally:
                    tracker["active"] -= 1

if __name__ == "__main__":
    asyncio.run(main())
