from sly import Lexer, Parser

class ConfLexer(Lexer):
    tokens = {BEGIN, END, NAME, SEMICOLON, STRING}
    BEGIN = r'{'
    END = r'}'
    ignore = r' \t'
    ignore_comment = r'\#.*'
    ignore_newline = r'\n+'
    NAME = r'[^ \t\#{};\']+'
    SEMICOLON = r';'
    STRING = r"'.*'"


class ConfParser(Parser):
    tokens = ConfLexer.tokens

    @_('directive directives')
    def directives(self, p):
        return [p.directive] + p.directives

    @_('empty')
    def directives(self, p):
        return []

    @_('simple_directive', 'block_directive')
    def directive(self, p):
        return p[0]

    @_('name names SEMICOLON')
    def simple_directive(self, p):
        return dict(type="simple", args=[p.name] + p.names, ctx=[])

    @_('name names BEGIN directives END')
    def block_directive(self, p):
        return dict(type="block", args=[p.name] + p.names, ctx=p.directives)

    @_('name names')
    def names(self, p):
        return [p.name] + p.names

    @_('empty')
    def names(self, p):
        return []

    @_('NAME')
    def name(self, p):
        return p[0]

    @_('STRING')
    def name(self, p):
        return p[0][1:-1]

    @_('')
    def empty(self, p):
        pass


def main():
    from json import dumps
    from pathlib import Path
    text = Path("nginx.conf").read_text()
    lexer = ConfLexer()
    parser = ConfParser()
    data = parser.parse(lexer.tokenize(text))
    Path("conf_parsed.json").write_text(dumps(data, indent=2))


if __name__ == '__main__':
    main()
