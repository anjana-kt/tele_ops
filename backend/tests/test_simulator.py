import asyncio
import unittest


class TestDeviceSimulator(unittest.IsolatedAsyncioTestCase):
    allowed_delta_Delay:float = 0.2

    test_data = {
        "success": {
            "command_id": "cmd-success",
            "status": DeviceStatus.SUCCEEDED,
            "message": "Command completed successfully",
            "is_fail": False,
            "delay_time": 1.0,
            "timeout": 2.0
        },
        "failure": {
            "command_id": "cmd-failed",
            "status": DeviceStatus.FAILED,
            "message": "Simulated command failure on ",
            "is_fail": True,
            "delay_time": 1.0,
            "timeout": 2.0
        },
        "unknown_command": {
            "command_id": "cmd-unknown",
            "status": DeviceStatus.OUTCOME_UNKNOWN,
            "message": "Timed out after 0.50s; device outcome is unknown",
            "is_fail": False,
            "delay_time": 1.0,
            "timeout": 0.5
        }
    }

    async def _device_execute_helper(self, test_device:SimulatedDevice, command_id:str, status:str, message:str, is_fail=False, delay_time=1.0, timeout=1.0, device_id="station-test"):
        result = await test_device.execute(command_id, fail=is_fail, delay_seconds=delay_time, timeout_seconds=timeout)
        self.assertEqual(result.device_id, device_id)
        self.assertEqual(result.command_id, command_id)
        self.assertEqual(result.status, status)
        self.assertEqual(result.message, message + device_id) if is_fail else self.assertEqual(result.message, message )
        self.assertLessEqual(result.duration_seconds, timeout + self.allowed_delta_Delay)
        print(f"{command_id} | {status} | {message}")

        return result

    async def test_run(self):
        print("\nTesting run command")
        test_device = SimulatedDevice("station-test")

        # for device, data in self.test_data.items():
        #     await self._device_execute_helper(**data)

        await asyncio.gather(
            self._device_execute_helper(test_device, **self.test_data["failure"]),
            self._device_execute_helper(test_device, **self.test_data["success"]),
            self._device_execute_helper(test_device, **self.test_data["unknown_command"])
        )

    async def test_concurrent_run(self):
        print("\nTesting concurrent run:")
        test_device = SimulatedDevice("station-test")
        await asyncio.gather(
            self._device_execute_helper(test_device, **self.test_data["failure"]),
            self._device_execute_helper(test_device, **self.test_data["success"]),
        )

    async def test_sequential_run(self):
        print("\nTesting sequential run:")
        test_device = SimulatedDevice("station-test")
        await self._device_execute_helper(test_device, **self.test_data["success"])
        await self._device_execute_helper(test_device, **self.test_data["failure"])

    async def test_sequential_device_run(self):
        print("\nTesting sequential device usage:")
        device = TrackingDeviceSequential("station-test")

        results = await asyncio.gather(
            self._device_execute_helper(device, **self.test_data["success"]),
            self._device_execute_helper(device, **self.test_data["success"]),
        )

        self.assertTrue(all(r.status == DeviceStatus.SUCCEEDED for r in results))
        self.assertEqual(device.max_active, 1)

    async def test_devices_can_overlap(self):
        print("\nTesting overlap")
        stations = ["station-test-1", "station-test-2"]
        tracker = {"active": 0, "max_active": 0}

        results = await asyncio.gather(
            self._device_execute_helper(TrackingDeviceOverlap(stations[0], tracker), **self.test_data["success"], device_id=stations[0]),
            self._device_execute_helper(TrackingDeviceOverlap(stations[1], tracker), **self.test_data["success"], device_id=stations[1]),
        )

        self.assertTrue(
            all(r.status == DeviceStatus.SUCCEEDED for r in results)
        )
        self.assertEqual(tracker["max_active"], 2)

if __name__ == "__main__":
    unittest.main()