"""Offline approximation of C# compiler errors CS0128/CS0136 for the driver sources.

Windows csc refuses a local (or lambda/anonymous-method parameter) whose name is already declared in the same method in an
enclosing or the same scope, whatever the order (CS0136: the name would mean something else in the enclosing scope);
mono mcs, used offline, does not always report it (run 43804931601: every native case stopped at the x86 reference host
build, compilerErrorCodes ["CS0136"]). This scanner reads the compact C# 2 style of scripts/*.cs: it strips comments and
literals, builds the block tree, collects local declarations, for/foreach/using/catch variables and anonymous-method
parameters, and reports two declarations of one name in one member when the scope of one contains the other.
It is a lint, not a parser: it may miss a conflict, it must never be the only check of a compiler.
"""
import pathlib, re, sys

KEYWORDS = {'return', 'else', 'new', 'throw', 'case', 'goto', 'in', 'out', 'ref', 'is', 'as', 'typeof', 'using', 'namespace', 'class',
            'struct', 'enum', 'interface', 'public', 'private', 'protected', 'internal', 'static', 'readonly', 'const', 'override',
            'virtual', 'abstract', 'sealed', 'extern', 'unsafe', 'volatile', 'delegate', 'event', 'operator', 'implicit', 'explicit',
            'if', 'while', 'for', 'foreach', 'do', 'switch', 'catch', 'finally', 'try', 'lock', 'checked', 'unchecked', 'default',
            'break', 'continue', 'yield', 'await', 'sizeof', 'stackalloc', 'this', 'base', 'null', 'true', 'false', 'params', 'get', 'set'}


def strip(text):
    """Comments and string/char literals replaced by spaces (positions kept)."""
    out, i, n = list(text), 0, len(text)
    def blank(a, b):
        for k in range(a, b):
            if out[k] != '\n':
                out[k] = ' '
    while i < n:
        c = text[i]
        if text.startswith('//', i):
            j = text.find('\n', i); j = n if j < 0 else j; blank(i, j); i = j
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2); j = n if j < 0 else j + 2; blank(i, j); i = j
        elif c == '@' and i + 1 < n and text[i + 1] == '"':
            j = i + 2
            while j < n:
                if text[j] == '"' and j + 1 < n and text[j + 1] == '"':
                    j += 2; continue
                if text[j] == '"':
                    break
                j += 1
            blank(i + 1, j + 1 if j < n else n); i = j + 1
        elif c in '"\'':
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == '\\' else 1
            blank(i + 1, min(j, n)); i = j + 1
        else:
            i += 1
    return ''.join(out)


TYPE = r'(?:[A-Za-z_][\w.]*(?:<[^<>;(){}=]*(?:<[^<>;(){}=]*>)?[^<>;(){}=]*>)?(?:\[\])*\??)'
DECL = re.compile(r'(?<![\w.])(' + TYPE + r')\s+([A-Za-z_]\w*)\s*(?==(?!=)|;|,|\bin\b|\))')
HEADER = re.compile(r'\b(for|foreach|using|catch|delegate)\s*\(')
MEMBER = re.compile(r'(?:\)|\bget|\bset|\badd|\bremove)\s*$')


def blocks(code):
    """Block tree: list of (start, end, parent index)."""
    out, stack = [], []
    for i, c in enumerate(code):
        if c == '{':
            out.append([i, None, stack[-1] if stack else -1]); stack.append(len(out) - 1)
        elif c == '}' and stack:
            out[stack.pop()][1] = i
    for b in out:
        if b[1] is None:
            b[1] = len(code)
    return out


def innermost(tree, pos):
    best = -1
    for k, (a, b, _) in enumerate(tree):
        if a < pos <= b and (best < 0 or a > tree[best][0]):
            best = k
    return best


PSEUDO = {}  # pseudo scope (the brace-less statement of a for/foreach/using/catch header) -> its enclosing block


def ancestors(tree, k):
    out = set()
    if k in PSEUDO:
        out.add(k); k = PSEUDO[k]
    while k >= 0:
        out.add(k); k = tree[k][2]
    return out


def close_paren(code, i):
    depth = 0
    for j in range(i, len(code)):
        if code[j] == '(':
            depth += 1
        elif code[j] == ')':
            depth -= 1
            if depth == 0:
                return j
    return len(code)


def declarators(code, start, name_end):
    """Further names of a multi-declarator statement (int a=0,b=1;) after the first name."""
    names, depth, j = [], 0, name_end
    while j < len(code):
        c = code[j]
        if c in '([{':
            depth += 1
        elif c in ')]}':
            if depth == 0:
                break
            depth -= 1
        elif c == ';' and depth == 0:
            break
        elif c == ',' and depth == 0:
            m = re.match(r'\s*([A-Za-z_]\w*)\s*(?==(?!=)|;|,)', code[j + 1:])
            if not m:
                break
            names.append((m.group(1), j + 1 + m.start(1)))
        j += 1
    return names


def conflicts(text):
    code = strip(text)
    tree = blocks(code)
    # Member bodies: a block whose opening brace follows a parameter list or an accessor keyword and whose parent is a
    # type body (a block that is not itself inside a member body).
    member = {}
    for k, (a, _, parent) in enumerate(tree):
        if parent in member:
            member[k] = member[parent]; continue
        if MEMBER.search(code[max(0, a - 200):a]) and not re.search(r'\b(if|while|for|foreach|switch|catch|using|lock|delegate)\s*\([^{};]*\)\s*$', code[max(0, a - 400):a]):
            member[k] = k
    decls = []  # (member, scope block, name, position)
    PSEUDO.clear()
    def add(name, scope, pos):
        base = PSEUDO.get(scope, scope)
        if name in KEYWORDS or base < 0 or base not in member:
            return
        decls.append((member[base], scope, name, pos))
    # Parameters of members and anonymous methods/headers: scope = the block that follows the parenthesis.
    for m in HEADER.finditer(code):
        close = close_paren(code, m.end() - 1)
        after = code[close + 1:close + 40].lstrip()
        params = code[m.end():close]
        body = innermost(tree, close + 1 + (len(code[close + 1:close + 40]) - len(after)) + 1) if after.startswith('{') else None
        if body is not None:
            scope = body
        else:
            scope = ('stmt', m.start()); PSEUDO[scope] = innermost(tree, m.start())
        for p in re.finditer(r'(?<![\w.])(' + TYPE + r')\s+([A-Za-z_]\w*)\s*(?==(?!=)|;|,|\bin\b|$)', params if m.group(1) != 'for' else params.split(';')[0]):
            if p.group(1) not in KEYWORDS:
                add(p.group(2), scope, m.end() + p.start(2))
    for k in list(member):
        if member[k] != k:
            continue
        a = tree[k][0]
        head = code[max(0, a - 400):a]
        if head.rstrip().endswith(')'):
            close = len(head.rstrip()) - 1; depth = 0; open_ = None
            for j in range(close, -1, -1):
                if head[j] == ')':
                    depth += 1
                elif head[j] == '(':
                    depth -= 1
                    if depth == 0:
                        open_ = j; break
            if open_ is not None and not re.search(r'\b(if|while|for|foreach|switch|catch|using|lock|delegate)\s*$', head[:open_]):
                for p in re.finditer(r'(?:\b(?:out|ref|params)\s+)?(?<![\w.])(' + TYPE + r')\s+([A-Za-z_]\w*)\s*(?=,|$|=)', head[open_ + 1:close]):
                    if p.group(1) not in KEYWORDS:
                        add(p.group(2), k, a)
    for m in DECL.finditer(code):
        type_, name = m.group(1), m.group(2)
        if type_ in KEYWORDS or name in KEYWORDS:
            continue
        before = code[max(0, m.start() - 1):m.start()]
        if before and before not in ' \t\n;{})':
            continue
        if before in ' \t\n':
            prev = code[:m.start()].rstrip()[-1:]
            if prev and prev not in ';{})':
                continue
        # Declarations inside a header parenthesis are handled above.
        line_start = max(code.rfind(';', 0, m.start()), code.rfind('{', 0, m.start()), code.rfind('}', 0, m.start()))
        prefix = code[line_start + 1:m.start()]
        if '(' in prefix and prefix.count('(') > prefix.count(')'):
            continue
        scope = innermost(tree, m.start())
        add(name, scope, m.start(2))
        if code[m.end():].lstrip().startswith(('=', ',')):
            for extra, pos in declarators(code, m.start(), m.end()):
                add(extra, scope, pos)
    out = []
    by_member = {}
    for d in decls:
        by_member.setdefault((d[0], d[2]), []).append(d)
    for (_, name), items in by_member.items():
        seen = set()
        for x in items:
            for y in items:
                if x is y or (y[3], x[3]) in seen or x[3] == y[3]:
                    continue
                if x[1] in ancestors(tree, y[1]) or y[1] in ancestors(tree, x[1]):
                    seen.add((x[3], y[3]))
                    out.append((name, text.count('\n', 0, min(x[3], y[3])) + 1, text.count('\n', 0, max(x[3], y[3])) + 1))
    return sorted(set(out), key=lambda v: (v[1], v[0]))


def main(paths):
    bad = 0
    for path in paths:
        for name, first, second in conflicts(pathlib.Path(path).read_text(encoding='utf-8-sig')):
            print('%s:%d: local %s declared again at line %d in an enclosing or the same scope (CS0128/CS0136)' % (path, second, name, first)); bad += 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or sorted(str(p) for p in pathlib.Path(__file__).parent.glob('*.cs'))))
