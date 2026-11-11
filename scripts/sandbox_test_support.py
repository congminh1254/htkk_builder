"""Test sandbox: every git or filesystem mutation in a test runs inside a temporary directory the test created.

A Sandbox is a fresh `tempfile.mkdtemp` directory carrying a random marker. `require(path)` refuses any path that
does not resolve (symlinks followed) inside that live sandbox, and refuses a sandbox that overlaps the builder
checkout itself (for example TMPDIR pointing into the clone). `guard(module)` swaps the module's `subprocess` for a
proxy whose `run` refuses a git command unless its working directory, `-C`/`--git-dir`/`--work-tree` targets and
every absolute-path argument are inside the sandbox, and unless the environment it would pass carries no
repository-locating GIT_* variable that points elsewhere. While a sandbox is active the process environment is
scrubbed of those variables (a suite started from a git hook inherits GIT_DIR) and GIT_CEILING_DIRECTORIES stops
git from discovering a repository above the sandbox.
"""
import os
import pathlib
import secrets
import shutil
import subprocess
import tempfile

CHECKOUT = pathlib.Path(__file__).resolve().parents[1]
MARKER = '.htkk-test-sandbox'
# Variables that make git operate on a repository other than the one named on the command line.
LOCATING = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
            'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES', 'GIT_DISCOVERY_ACROSS_FILESYSTEM')
PATH_OPTIONS = ('-C', '--git-dir', '--work-tree')


class SandboxViolation(AssertionError):
    pass


def _overlaps(a, b):
    return a == b or a.is_relative_to(b) or b.is_relative_to(a)


class Sandbox:
    def __init__(self):
        self.root = pathlib.Path(tempfile.mkdtemp(prefix='htkk-builder-test-')).resolve()
        if _overlaps(self.root, CHECKOUT):
            shutil.rmtree(self.root, ignore_errors=True)
            raise SandboxViolation('temporary directory overlaps the builder checkout; set TMPDIR outside it')
        self.token = secrets.token_hex(16)
        (self.root / MARKER).write_text(self.token)
        self._saved = None

    @classmethod
    def for_test(cls, case):
        """Create, activate and register cleanup on a unittest.TestCase."""
        box = cls()
        box.activate()
        case.addCleanup(box.close)
        return box

    def live(self):
        try:
            return (self.root / MARKER).read_text() == self.token
        except OSError:
            return False

    def require(self, path, base=None):
        path = pathlib.Path(os.fspath(path))
        if not path.is_absolute():
            path = pathlib.Path(base or os.getcwd()) / path
        resolved = path.resolve()
        if not self.live():
            raise SandboxViolation('sandbox is not live: %s' % self.root)
        if not resolved.is_relative_to(self.root):
            raise SandboxViolation('refusing to touch %s outside the test sandbox %s' % (resolved, self.root))
        if _overlaps(resolved, CHECKOUT):
            raise SandboxViolation('refusing to touch the builder checkout: %s' % resolved)
        return resolved

    def activate(self):
        if self._saved is not None:
            return
        self._saved = {k: os.environ[k] for k in LOCATING if k in os.environ}
        for key in LOCATING:
            os.environ.pop(key, None)
        os.environ['GIT_CEILING_DIRECTORIES'] = str(self.root)

    def deactivate(self):
        if self._saved is None:
            return
        for key in LOCATING:
            os.environ.pop(key, None)
        os.environ.update(self._saved)
        self._saved = None

    def close(self):
        self.deactivate()
        if self.live():
            shutil.rmtree(self.root, ignore_errors=True)

    # ------------------------------------------------------------------ git command guard
    def check_git(self, args, cwd=None, env=None):
        """Refuse a git command that could read or write a repository outside this sandbox."""
        args = [os.fspath(a) for a in args]
        if not args or os.path.basename(args[0]) not in ('git', 'git.exe'):
            raise SandboxViolation('only git commands are guarded: %r' % args[:1])
        base = pathlib.Path(cwd if cwd is not None else os.getcwd())
        if cwd is not None:
            base = self.require(base)
        environment = os.environ if env is None else env
        for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_COMMON_DIR'):
            if environment.get(key):
                self.require(environment[key], base)
        located = False
        i = 1
        while i < len(args):
            arg = args[i]
            name, equals, inline = arg.partition('=')
            if name in PATH_OPTIONS:
                value = inline if equals else (args[i + 1] if i + 1 < len(args) else '')
                target = self.require(value, base)
                if name == '-C':
                    base = target
                located = True
                i += 1 if equals else 2
                continue
            if arg.startswith('/') or (len(arg) > 2 and arg[1] == ':' and arg[2] in '\\/'):
                self.require(arg, base)
            i += 1
        if not located:
            # No explicit location: git would discover the repository from the working directory.
            self.require(base)
        return base

    def guard(self, module, case=None):
        """Replace module.subprocess by a proxy that checks every git command against this sandbox."""
        box = self
        real = module.subprocess

        class Guarded:
            def __getattr__(self, name):
                return getattr(real, name)

            @staticmethod
            def run(args, *rest, **kwargs):
                if isinstance(args, (list, tuple)) and args and os.path.basename(os.fspath(args[0])) in ('git', 'git.exe'):
                    box.check_git(args, kwargs.get('cwd'), kwargs.get('env'))
                elif isinstance(args, (str, bytes)) and b'git' in (args if isinstance(args, bytes) else args.encode()):
                    raise SandboxViolation('shell-string git commands are not allowed in tests')
                return real.run(args, *rest, **kwargs)

        module.subprocess = Guarded()

        def restore():
            module.subprocess = real
        if case is not None:
            case.addCleanup(restore)
        return restore

    def git(self, *args, check=True):
        """Run git with an explicit --git-dir or -C inside the sandbox (test-side helper)."""
        command = ['git', *map(os.fspath, args)]
        self.check_git(command, cwd=self.root)
        return subprocess.run(command, cwd=self.root, capture_output=True, text=True, check=check)
