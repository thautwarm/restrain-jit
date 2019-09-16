paths = [
    'restrain_jit/bejulia/instructions',
    'restrain_jit/bejulia/representations',
]

for FROM, TO in [(path, path + '.py') for path in paths]:
    with open(FROM) as f:
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
            code.append('@dataclass')
            code.append(f'class {name}:')
            for v in fields:
                code.append('    ' + v)
            else:
                code.append('    pass')
    code.append('')

    with open(TO, 'w') as f:
        f.write('\n'.join(code))
