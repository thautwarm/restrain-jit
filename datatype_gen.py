from pathlib import Path


def find_paths(p: Path):
    if not p.is_dir():
        if p.suffix == '.gen':
            yield p
    else:
        for i in p.iterdir():
            if i == p:
                continue
            yield from find_paths(i)


for FROM, TO in [(path, path.with_suffix('.py'))
                 for path in find_paths(Path('.'))]:
    with FROM.open() as f:
        text = f.read()

    defs = [[e.strip() for e in i.strip().split()] for i in text.split(';')]
    code = [
        'from enum import Enum, auto as _auto', 'import abc',
        'import typing as t', 'from dataclasses import dataclass'
    ]
    defs = list(filter(None, defs))

    for each in defs:
        code.append('')
        code.append('')

        head, *each = each
        if head == 'typevar':
            var, *args = each
            cov = ""
            if args:
                cov = "bound=" + "t.Union[" + ', '.join(map(repr, args)) + "]"
            code.append(f'{var} = t.TypeVar({var!r}, {cov})')
        if head == 'import':
            code.append(f'from {each[0]} import *')
        elif head == "enum":
            name, *variants = each
            code.append(f'class {name}(Enum):')
            for v in variants:
                code.append(f'    {v} = _auto()')
            else:
                code.append('    pass')
        elif head == 'abc':
            abc = each[0]
            code.append(f'class {abc}:')
            code.append('    pass')
            continue
        elif head == 'data':
            name, *fields = each
            code.append('@dataclass(frozen=True, order=True)')
            code.append(f'class {name}:')
            for v in fields:
                code.append('    ' + v)
            else:
                code.append('    pass')
    code.append('')

    with TO.open('w') as f:
        f.write('\n'.join(code))
