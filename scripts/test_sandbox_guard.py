"""Regression: tests that run git can only touch a sandbox the test created, never the builder checkout.

An agent once saw its scratch clone reduced to a single `base` commit while this suite ran. The cause was another
session recreating the same scratch path, but the suite had one real exposure: MarkerCommit ran `git -C .` from
the process working directory (the checkout) and inherited GIT_DIR. These tests pin the guard that now closes it.
"""
import importlib.util
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sandbox_test_support as support
from sandbox_test_support import Sandbox, SandboxViolation

spec = importlib.util.spec_from_file_location('pages_deploy_guard', ROOT / 'pages-deploy.py')
pages = importlib.util.module_from_spec(spec); spec.loader.exec_module(pages)


class Refusals(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox.for_test(self)

    def test_checkout_and_foreign_temp_dirs_are_refused(self):
        foreign = pathlib.Path(tempfile.mkdtemp(prefix='htkk-foreign-'))
        self.addCleanup(shutil.rmtree, foreign, True)
        for path in (support.CHECKOUT, ROOT, support.CHECKOUT / '.git', foreign, foreign / 'x', self.box.root / '..'):
            with self.subTest(path=path), self.assertRaises(SandboxViolation):
                self.box.require(path)
        self.assertEqual(self.box.require(self.box.root / 'a' / 'b'), self.box.root / 'a' / 'b')

    def test_symlink_escape_and_dead_sandbox_are_refused(self):
        link = self.box.root / 'escape'
        link.symlink_to(support.CHECKOUT, target_is_directory=True)
        with self.assertRaises(SandboxViolation):
            self.box.require(link / '.git')
        (self.box.root / support.MARKER).write_text('forged')
        with self.assertRaises(SandboxViolation):
            self.box.require(self.box.root / 'inside')

    def test_sandbox_inside_the_checkout_is_refused(self):
        with mock.patch.object(support.tempfile, 'mkdtemp', return_value=str(ROOT / '__pycache__')):
            with mock.patch.object(support.shutil, 'rmtree') as rmtree, self.assertRaises(SandboxViolation):
                Sandbox()
        rmtree.assert_called_once()

    def test_git_commands_aimed_outside_are_refused_before_running(self):
        repo = str(support.CHECKOUT)
        inside = str(self.box.root / 'r.git')
        cases = [
            (['git', '-C', '.', 'init', '--bare', inside], None, None),          # the old MarkerCommit setUp
            (['git', '-C', repo, 'log'], None, None),
            (['git', '--git-dir', repo + '/.git', 'update-ref', '-d', 'HEAD'], None, None),
            (['git', '--git-dir=' + repo + '/.git', 'reset', '--hard'], None, None),
            (['git', '--work-tree', repo, '--git-dir', inside, 'checkout', '--orphan', 'x'], None, None),
            (['git', 'init', '--quiet', repo], self.box.root, None),
            (['git', 'push', repo, 'HEAD:refs/heads/main'], self.box.root, None),
            (['git', 'status'], support.CHECKOUT, None),                        # implicit discovery from cwd
            (['git', 'status'], None, None),                                    # process cwd is not the sandbox
            (['git', '-C', inside, 'init', '--bare'], None, {'GIT_DIR': repo + '/.git'}),
        ]
        guard = self.box.guard(pages)
        self.addCleanup(guard)
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('must not run')) as run:
            for args, cwd, env in cases:
                with self.subTest(args=args, cwd=cwd), self.assertRaises(SandboxViolation):
                    pages.subprocess.run(args, cwd=cwd, env=env)
            run.assert_not_called()
        with self.assertRaises(SandboxViolation):
            pages.subprocess.run('git reset --hard', shell=True)

    def test_inherited_repository_variables_are_scrubbed_while_active(self):
        self.box.deactivate()
        with mock.patch.dict(os.environ, {'GIT_DIR': str(support.CHECKOUT / '.git'), 'GIT_WORK_TREE': str(support.CHECKOUT)}):
            self.box.activate()
            self.assertNotIn('GIT_DIR', os.environ); self.assertNotIn('GIT_WORK_TREE', os.environ)
            self.assertEqual(os.environ['GIT_CEILING_DIRECTORIES'], str(self.box.root))
            self.box.deactivate()
            self.assertEqual(os.environ['GIT_DIR'], str(support.CHECKOUT / '.git'))


@unittest.skipUnless(shutil.which('git'), 'git required')
class CanaryRepository(unittest.TestCase):
    """The pages-deploy marker flow run with GIT_DIR pointing at another repository leaves that repository alone."""

    def test_marker_flow_with_hostile_environment_leaves_canary_untouched(self):
        canary_box = Sandbox.for_test(self)
        canary = canary_box.root / 'canary'
        canary_box.git('init', '--quiet', canary)
        canary_box.git('-C', canary, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '--quiet', '--allow-empty', '-m', 'keep')
        def state():
            out = canary_box.git('-C', canary, 'for-each-ref', '--format=%(refname) %(objectname)').stdout
            return out, canary_box.git('-C', canary, 'rev-parse', 'HEAD').stdout, sorted(p.name for p in (canary / '.git' / 'objects').iterdir())
        before = state()
        canary_box.deactivate()
        with mock.patch.dict(os.environ, {'GIT_DIR': str(canary / '.git'), 'GIT_WORK_TREE': str(canary)}):
            box = Sandbox.for_test(self)
            box.guard(pages, self)
            remote, work = str(box.root / 'remote.git'), str(box.root / 'work.git')
            for path in (remote, work):
                pages.git(str(box.root), 'init', '--quiet', '--bare', path)
            record = pages.provenance('8' * 40, 'f' * 40, '5' * 40, '7', '1')
            commit = pages.make_marker(work, record, '', remote)
            pages.git(work, *pages.push_args(commit, '', remote))
            self.assertEqual(pages.remote_head(work, remote), commit)
            with self.assertRaises(SandboxViolation):
                pages.git(str(canary), 'update-ref', '-d', 'HEAD')
            box.close()
        canary_box.activate()
        self.assertEqual(state(), before)


class EveryGitTestUsesTheSandbox(unittest.TestCase):
    """Static lock: a test module that runs git (directly or through a module under test) uses the sandbox."""

    GIT_CALL = re.compile(r"""subprocess\.run\(\s*\[\s*['"]git['"]|\bd\.git\(|\bx\.publish\(|run_git\(""")

    def test_git_running_test_modules_import_the_sandbox(self):
        offenders = []
        for path in sorted(ROOT.glob('test_*.py')):
            text = path.read_text(encoding='utf-8')
            if self.GIT_CALL.search(text) and 'from sandbox_test_support import Sandbox' not in text:
                offenders.append(path.name)
        self.assertEqual(offenders, [])
        for name in ('test_pages_deploy.py', 'test_source_extract.py'):
            text = (ROOT / name).read_text(encoding='utf-8')
            self.assertIn('Sandbox.for_test(self)', text)
            self.assertIn('.guard(', text)
        self.assertNotIn("d.git('.'", (ROOT / 'test_pages_deploy.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
