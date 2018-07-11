
NUMBER, STRING, BOOL, NULL, LBRACKET, RBRACKET, LBRACE, RBRACE, COLON, COMMA, EOF = (
    "NUMBER", "STRING", "BOOL", "NULL", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE", 'COLON', 'COMMA', 'EOF'
)

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """
        移动 pos，并修改 current_char
        """
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        '''
        过滤空格
        '''
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while (
                self.current_char is not None and
                self.current_char.isdigit()
            ):
                result += self.current_char
                self.advance()

            token = Token(NUMBER, float(result))
        else:
            token = Token(NUMBER, int(result))

        return token

    def string(self):
        self.advance()
        text = ""
        while self.current_char != '"' and self.current_char != '\n' and self.current_char != None:
            if self.current_char == '\\':
                self.advance()
            # \/bfnrt
                if self.current_char == '\\':
                    text += '\\'
                elif self.current_char == '/':
                    text += '/'
                elif self.current_char == 'b':
                    text += '\b'
                elif self.current_char == 'f':
                    text += '\f'
                elif self.current_char == 'n':
                    text += '\n'
                elif self.current_char == 'r':
                    text += '\r'
                elif self.current_char == 't':
                    text += '\t'
                else:
                    text += self.current_char
            else:
                text += self.current_char
            
            self.advance()

        if self.current_char == '"':
            self.advance()
            return Token(STRING, text)
        else:
            self.error()

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]


    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.number()

            if self.text[self.pos:].startswith('null'):
                self.advance()
                self.advance()
                self.advance()
                self.advance()
                return Token(NULL, None)

            if self.text[self.pos:].startswith('true'):
                self.advance()
                self.advance()
                self.advance()
                self.advance()
                return Token(BOOL, True)

            if self.text[self.pos:].startswith('false'):
                self.advance()
                self.advance()
                self.advance()
                self.advance()
                self.advance()
                return Token(BOOL, False)

            if self.current_char == '"':
                return self.string()
            
            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '[':
                self.advance()
                return Token(LBRACKET, '[')

            if self.current_char == ']':
                self.advance()
                return Token(RBRACKET, ']')
                
            if self.current_char == '{':
                self.advance()
                return Token(LBRACE, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RBRACE, '}')

            self.error()

        return Token(EOF, None)

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            print('need', token_type)
            print('current', self.current_token)
            print(self.lexer.text[self.lexer.pos:])
            self.error()

    def json(self):
        if self.current_token.type == LBRACE:
            return self.object()
        elif self.current_token.type == LBRACKET:
            return self.array()
        elif self.current_token.type == NULL:
            self.eat(NULL)
            return None
        elif self.current_token.type == BOOL:
            val = self.current_token.value
            self.eat(BOOL)
            return val
        elif self.current_token.type == NUMBER:
            val = self.current_token.value
            self.eat(NUMBER)
            return val
        elif self.current_token.type == STRING:
            val = self.current_token.value
            self.eat(STRING)
            return val
        
        

    def object(self):
        self.eat(LBRACE)
        if self.current_token.type == RBRACE:
            self.eat(RBRACE)
            return {}
    
        obj = { }
        key = self.current_token.value
        self.eat(STRING)
        self.eat(COLON)
        val = self.json()
        obj[key] = val
    
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            key = self.current_token.value
            self.eat(STRING)
            self.eat(COLON)
            val = self.json()
            obj[key] = val
        self.eat(RBRACE)
        return obj

    def array(self):
        self.eat(LBRACKET)
        if self.current_token.type == RBRACKET:
            self.eat(RBRACKET)
            return []
    
        lst = [ self.json() ]

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            lst.append(self.json())
        self.eat(RBRACKET)
        return lst

    def parse(self):
        rt = self.json()
        self.eat(EOF)
        return rt
    


json = """
{
    "name": [
        1.22323,
        2456,
        true,
        false,
        null
    ]
}
"""

lexer = Lexer(json)
# token = lexer.get_next_token()

# while token.type != EOF:
#     print(token)
#     token = lexer.get_next_token()

parser = Parser(lexer)
print(parser.parse())