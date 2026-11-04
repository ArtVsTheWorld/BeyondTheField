"""Offline verifier for the small emitted APT subset, never a game bridge."""
import struct

UNDEFINED = object()


class ScriptFunction:
    def __init__(self, machine, program, begin, end, params, registers):
        self.machine, self.program = machine, program
        self.begin, self.end, self.params = begin, end, params
        self.registers = registers

    def call(self, receiver, args):
        registers = {1: receiver}
        for index, register in enumerate(self.params):
            registers[register] = args[index] if index < len(args) else UNDEFINED
        return self.machine.run(self.program, registers, self.begin, self.end)


class Machine:
    def __init__(self, globals_, pool):
        self.globals, self.pool = globals_, pool
        self.depth = 0

    def invoke(self, function, receiver, args):
        if isinstance(function, ScriptFunction):
            return function.call(receiver, args)
        if not callable(function):
            raise AssertionError(f'Attempt to call a non-function: {function!r}')
        return function(*args)

    @staticmethod
    def member(receiver, key):
        if isinstance(receiver, dict):
            return receiver.get(key, UNDEFINED)
        if isinstance(receiver,str):
            if key=='charAt':return lambda i:receiver[i:i+1]
            if key=='length':return len(receiver)
        if isinstance(receiver, list):
            if key == 'length':
                return len(receiver)
            if key == 'push':
                def push(*args):
                    receiver.extend(args)
                    return len(receiver)
                return push
            return receiver[key] if isinstance(key, int) and 0 <= key < len(receiver) else UNDEFINED
        raise AssertionError(f'Unguarded member access: {receiver!r}.{key!r}')

    @staticmethod
    def equal(left, right, loose=False):
        nullish = lambda x: x is UNDEFINED or x is None
        if loose and nullish(left) and nullish(right):
            return True
        if isinstance(left, (dict, list, ScriptFunction)) or isinstance(right, (dict, list, ScriptFunction)):
            return left is right
        return type(left) is type(right) and left == right

    def run(self, program, registers, begin=0, end=None):
        code, literals = program.code, dict(program.literals)
        references = dict(program.references)
        end = len(code) if end is None else end
        pc, stack = begin, []
        self.depth += 1
        if self.depth > 16:
            raise AssertionError('Unexpected recursive action execution')

        def word():
            nonlocal pc
            pc = (pc + 7) & ~7
            value = struct.unpack_from('<i', code, pc)[0]
            pc += 4
            return value

        try:
            for _ in range(10000):
                if pc == end:
                    if stack:
                        raise AssertionError(f'Unbalanced implicit return: {stack!r}')
                    return UNDEFINED
                if not begin <= pc < end:
                    raise AssertionError('Action branch escaped its function')
                op = code[pc]
                pc += 1
                if op in (0x59, 0x5A, 0x73, 0x74, 0x76):
                    stack.append({0x59: 0, 0x5A: 1, 0x73: True,
                                  0x74: False, 0x76: UNDEFINED}[op])
                elif op == 0xB5:
                    stack.append(struct.unpack_from('<b', code, pc)[0])
                    pc += 1
                elif op == 0xB6:
                    stack.append(struct.unpack_from('<h', code, pc)[0])
                    pc += 2
                elif op == 0xB9:
                    stack.append(registers.get(code[pc], UNDEFINED))
                    pc += 1
                elif op == 0x50:
                    stack.append(stack.pop()+1)
                elif op == 0xA2:
                    stack.append(self.pool[code[pc]])
                    pc += 1
                elif op == 0xAF:
                    stack.append(self.member(stack.pop(), self.pool[code[pc]]))
                    pc += 1
                elif op == 0xA1:
                    pc = (pc + 7) & ~7
                    stack.append(literals[pc])
                    pc += 8
                elif op == 0xAD:
                    count = code[pc]
                    pc += 1
                    names = [self.pool[n] for n in code[pc:pc + count]]
                    pc += count
                    if names == ['logic_com', 'enum', 'Navigation', 'MENU_CAREER']:
                        stack.append('career-menu-enum')
                    elif names == ['fb_shared_enum', 'BindingType', 'NEWS_CATEGORY']:
                        stack.append('news-category-enum')
                    else:
                        value = self.globals[names[0]]
                        for name in names[1:]:
                            value = self.member(value, name)
                        stack.append(value)
                elif op == 0x87:
                    registers[word()] = stack[-1]
                elif op == 0x17:
                    stack.pop()
                elif op == 0x1C:
                    stack.append(self.globals[stack.pop()])
                elif op in (0x42, 0x43):
                    count = stack.pop()
                    if not isinstance(count, int) or count < 0 or count > 128:
                        raise AssertionError('Collection exceeds verifier bounds')
                    if op == 0x43 and count:
                        raise AssertionError('Only empty object constructors are emitted')
                    stack.append([stack.pop() for _ in range(count)] if op == 0x42 else {})
                elif op == 0x40:
                    name, count = stack.pop(), stack.pop()
                    if name != 'Object' or count != 0:
                        raise AssertionError('Unverified constructor')
                    stack.append({})
                elif op == 0x4E:
                    key, receiver = stack.pop(), stack.pop()
                    stack.append(self.member(receiver, key))
                elif op == 0x4F:
                    value, key, receiver = stack.pop(), stack.pop(), stack.pop()
                    receiver[key] = value
                elif op in (0x49, 0x66):
                    right, left = stack.pop(), stack.pop()
                    stack.append(self.equal(left, right, loose=op == 0x49))
                elif op==0x44:
                    value=stack.pop();stack.append('string' if isinstance(value,str) else 'undefined' if value is UNDEFINED else 'number' if isinstance(value,(int,float)) else 'object')
                elif op==0x0C:
                    right,left=stack.pop(),stack.pop();stack.append(left*right)
                elif op in (0x47, 0x0B, 0x48, 0x67):
                    right, left = stack.pop(), stack.pop()
                    if op == 0x47:
                        stack.append(str(left) + str(right) if isinstance(left, str) or isinstance(right, str) else left + right)
                    elif op == 0x0B:
                        stack.append(left - right)
                    elif op == 0x48:
                        stack.append(left < right)
                    else:
                        stack.append(left > right)
                elif op == 0x12:
                    stack.append(not stack.pop())
                elif op == 0x54:
                    constructor, instance = stack.pop(), stack.pop()
                    stack.append(isinstance(instance, dict) and instance.get('_class') is constructor)
                elif op in (0xB8, 0x9D, 0x99):
                    distance = word()
                    take = op == 0x99
                    if op != 0x99:
                        condition = bool(stack.pop())
                        take = condition if op == 0x9D else not condition
                    if take:
                        pc += distance
                elif op == 0x8E:
                    header = (pc + 7) & ~7
                    argc, count, flags = struct.unpack_from('<IHH', code, header + 8)
                    size = struct.unpack_from('<I', code, header + 24)[0]
                    if literals[header] != '' or flags != 0x29 or not 2 <= count <= 16:
                        raise AssertionError('Unverified nested function metadata')
                    if struct.unpack_from('<I', code, header + 32)[0] != 0x98765432 or struct.unpack_from('<Q', code, header + 40)[0] != 0x12345678:
                        raise AssertionError('Nested constant-pool scratch metadata changed')
                    if argc == 0:
                        params = ()
                    elif argc == 1 and references.get(header + 16) == 'focusParameters':
                        params = (2,)
                    else:
                        raise AssertionError('Unverified nested function parameters')
                    body, next_pc = header + 48, header + 48 + size
                    if next_pc > end:
                        raise AssertionError('Nested body escaped its definition')
                    stack.append(ScriptFunction(self, program, body, next_pc, params, count))
                    pc = next_pc
                elif op in (0x52, 0xB2):
                    if op == 0xB2:
                        name = self.pool[code[pc]]
                        pc += 1
                    else:
                        name = stack.pop()
                    receiver, count = stack.pop(), stack.pop()
                    args = [stack.pop() for _ in range(count)]
                    result = self.invoke(self.member(receiver, name), receiver, args)
                    if op == 0x52:
                        stack.append(result)
                elif op == 0x3E:
                    result = stack.pop()
                    if stack:
                        raise AssertionError(f'Unbalanced explicit return: {stack!r}')
                    return result
                else:
                    raise AssertionError(f'Unexpected opcode {op:#x} at {pc - 1:#x}')
            raise AssertionError('Action execution exceeded its bounded step count')
        finally:
            self.depth -= 1
