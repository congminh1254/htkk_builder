"""Selected HTKK oracle version for the trusted Python steps of a native run.

The workflow input ``htkk_version`` reaches these steps only as HTKK_ORACLE_VERSION. Absent
means the default (5.8.1); any other value than a reviewed baseline is refused. A non-default
oracle never shares a status context, an output branch or an immutable anchor with the
default cohort, so a 5.8.2 run can never satisfy or overwrite 5.8.1 release evidence.
"""
import importlib.util, pathlib

_spec = importlib.util.spec_from_file_location('htkk_oracle_baselines', pathlib.Path(__file__).with_name('generate-htkk-oracle-baselines.py'))
_generator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_generator)
BASELINES = _generator.load()
DEFAULT = BASELINES['default']
VERSIONS = tuple(BASELINES['versions'])


def version(environ):
    value = environ.get('HTKK_ORACLE_VERSION')
    if value is None or value == '':
        return DEFAULT
    if value not in VERSIONS:
        raise ValueError('HTKK_ORACLE_VERSION')
    return value


def baseline(value):
    if value not in VERSIONS:
        raise ValueError('HTKK_ORACLE_VERSION')
    return BASELINES['versions'][value]


def suffix(value):
    """'' for the default oracle, '-htkk582' for 5.8.2 (branch / anchor-safe)."""
    baseline(value)
    return '' if value == DEFAULT else '-htkk' + value.replace('.', '')


def status_context(context, value):
    baseline(value)
    return context + ('' if value == DEFAULT else '@htkk' + value.replace('.', ''))


def output_branch(branch, value):
    return branch + suffix(value)


def service_version(value):
    return baseline(value)['serviceVersion']


def pins(base, value):
    """Source pins of a retained manifest for the selected oracle.

    Every path the baseline pins takes that version's hash; the default oracle must already
    equal its baseline (tested), so a default-version manifest is byte-for-byte unchanged.
    """
    files = baseline(value)['files']
    return {path: files.get(path, sha) for path, sha in base.items()}
