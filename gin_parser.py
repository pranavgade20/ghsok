import itertools

from gin.config_parser import ConfigParser, BindingStatement


class GinParser:
    def __init__(self, file):
        self.parser = ConfigParser(file, None)
        lines = [line for line in self.parser]
        self.combinations = [self.get_combination_len(line) for line in lines]
        self.lines = [line if combs > 1 else line.location.line_content.strip() for line, combs in zip(lines, self.combinations)]

    def __iter__(self):
        self._iter = itertools.product(*[range(x) for x in self.combinations])
        return self

    def __next__(self):
        ret = []
        for line, i in zip(self.lines, next(self._iter)):
            if isinstance(line, BindingStatement):
                ret.append('/'.join(x for x in (line.scope, '.'.join(y for y in (line.selector, line.arg_name) if y != '')) if x != '') + '=' + str(line.value[i]))
            else:
                ret.append(line)

        return '\n'.join(ret)

    @staticmethod
    def get_combination_len(line):
        if isinstance(line, BindingStatement) and isinstance(line.value, list) and not line.location.line_content.strip().endswith("skip"):
            return len(line.value)
        return 1
