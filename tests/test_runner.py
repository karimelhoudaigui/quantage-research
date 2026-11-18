import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from scripts.run_cycles import main, invoke
from scripts.check import validate_completion, check


class Runner(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ('config', 'prompts', 'research'):
            (self.root/directory).mkdir()
        (self.root/'config/policy.json').write_text(json.dumps({'max_cycles_per_launch':4,'seconds_per_cycle':2}))
        (self.root/'prompts/cycle.md').write_text('Read state and finish one cycle.')
        (self.root/'research/claims.json').write_text('[]')
        self.clean = patch('scripts.run_cycles.subprocess.check_output', return_value='')
        self.clean.start()
        self.checker = patch('scripts.run_cycles.subprocess.run')
        self.checker.start()

    def tearDown(self):
        self.clean.stop()
        self.checker.stop()
        self.temp.cleanup()

    def executor(self, status='complete'):
        def execute(cmd, prompt, log, timeout):
            run = Path(log.name).parent
            (run/'summary.md').write_text('Software fixture, not scientific evidence.')
            (run/'completion.json').write_text(json.dumps({'status':status, 'question':'fixture', 'next_action':'next fixture'}))
        return execute

    def test_dry_run_never_executes(self):
        executor = Mock(side_effect=AssertionError('must not execute'))
        self.assertEqual(main(['--dry-run'], self.root, executor), 0)
        executor.assert_not_called()

    def test_success_resume_and_bound(self):
        self.assertEqual(main(['--cycles','2'], self.root, self.executor()), 0)
        self.assertEqual(main(['--cycles','1'], self.root, self.executor()), 0)
        self.assertEqual(len(list((self.root/'runs').glob('*/completion.json'))), 3)
        self.assertFalse((self.root/'.runner.lock').exists())

    def test_blocked_stops_and_resume_refuses(self):
        self.assertEqual(main(['--cycles','3'], self.root, self.executor('blocked')), 1)
        self.assertEqual(len(list((self.root/'runs').glob('*/completion.json'))), 1)
        other = Mock()
        self.assertEqual(main([], self.root, other), 1)
        other.assert_not_called()
        self.assertFalse((self.root/'.runner.lock').exists())

    def test_timeout_and_missing_completion_stop(self):
        for fail in (subprocess.TimeoutExpired('fixture', 2), FileNotFoundError('fixture')):
            with self.subTest(fail=fail):
                executor = Mock(side_effect=fail)
                # Isolate the previous failure to test each error path.
                for path in (self.root/'runs').glob('*/prompt.md'):
                    self.executor()([], '', type('Log', (), {'name':str(path.with_name('codex.log'))})(), 2)
                self.assertEqual(main([], self.root, executor), 1)
                self.assertFalse((self.root/'.runner.lock').exists())

    def test_missing_handoff_lock_and_dirty(self):
        self.assertEqual(main([], self.root, Mock()), 1)
        self.assertTrue(list((self.root/'runs').glob('*/runner-error.txt')))
        self.assertEqual(main([], self.root, Mock()), 1)
        with patch('scripts.run_cycles.subprocess.check_output', return_value=' M file'):
            self.assertEqual(main([], self.root, Mock()), 1)
        # A fresh workspace with no previous run and a live lock.
        for p in (self.root/'runs').glob('*/prompt.md'):
            self.executor()([], '', type('Log', (), {'name':str(p.with_name('codex.log'))})(), 2)
        (self.root/'.runner.lock').touch()
        self.assertEqual(main([], self.root, Mock()), 1)

    def test_timeout_kills_group(self):
        process = Mock(pid=123, returncode=-9)
        process.communicate.side_effect = [subprocess.TimeoutExpired('fixture', 2), (None, None)]
        with patch('scripts.run_cycles.subprocess.Popen', return_value=process), patch('scripts.run_cycles.os.killpg') as kill:
            with self.assertRaises(subprocess.TimeoutExpired):
                invoke(['fixture'], '', Mock(), 2)
            kill.assert_called_once()

    def test_validation_survives_python_optimization(self):
        run = self.root/'runs'/'test'
        run.mkdir(parents=True)
        path = run/'completion.json'
        path.write_text('{"status":"complete","question":" ","next_action":"x"}')
        (run/'summary.md').write_text('fixture')
        with self.assertRaises(ValueError): validate_completion(path)
        claims = [{'id':'x','status':'verified','statement':'x','limitations':'x','evidence':[]}]
        (self.root/'research/claims.json').write_text(json.dumps(claims))
        with self.assertRaises(ValueError): check(self.root)


if __name__ == '__main__':
    unittest.main()
