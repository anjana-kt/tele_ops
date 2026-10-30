from unittest import IsolatedAsyncioTestCase

from app.models.job_appstore import JobStates, Job
from tests.helpers.scenario_decorator import test_scenario


class TestJob(IsolatedAsyncioTestCase):

    @test_scenario("success")
    def test_job_success(self):
        test_job = Job('test-device', job_id='test-job')

        test_job.transition_to(JobStates.RUNNING)
        self.assertEqual(test_job.state, JobStates.RUNNING)

        test_job.transition_to(JobStates.SUCCEEDED)
        self.assertEqual(test_job.state, JobStates.SUCCEEDED)

    @test_scenario("failure")
    def test_job_failed(self):

        test_job = Job('test-device', job_id='test-job')

        test_job.transition_to(JobStates.RUNNING)
        self.assertEqual(test_job.state, JobStates.RUNNING)

        test_job.transition_to(JobStates.FAILED)
        self.assertEqual(test_job.state, JobStates.FAILED)

    @test_scenario("value error")
    def test_job_transition_error(self):
        test_job = Job('test-device', job_id='test-job')

        self.assertRaises(ValueError, test_job.transition_to, JobStates.SUCCEEDED)
        self.assertRaises(ValueError, test_job.transition_to, JobStates.FAILED)

    @test_scenario("value error from success")
    def test_job_transition_from_success(self):
        test_job = Job('test-device', job_id='test-job')

        test_job.transition_to(JobStates.RUNNING)
        test_job.transition_to(JobStates.SUCCEEDED)
        self.assertEqual(test_job.state, JobStates.SUCCEEDED)
        with self.assertRaises(ValueError):
            test_job.transition_to(JobStates.RUNNING)

    @test_scenario("value error from failure")
    def test_job_transition_from_failure(self):
        test_job = Job('test-device', job_id='test-job')

        test_job.transition_to(JobStates.RUNNING)
        test_job.transition_to(JobStates.FAILED)
        self.assertEqual(test_job.state, JobStates.FAILED)
        with self.assertRaises(ValueError):
            test_job.transition_to(JobStates.SUCCEEDED)


