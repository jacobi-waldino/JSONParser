# Defines token types to be returned to the class Token
class TokenType:
    LCURLY = 'LCURLY'       # '{'
    RCURLY = 'RCURLY'       # '}'
    LSQUARE = 'LSQUARE'     # '['
    RSQUARE = 'RSQUARE'     # ']'
    COMMA = 'COMMA'         # ','
    COLON = 'COLON'         # ':'
    STRING = 'STRING'       # Strings
    NUMBER = 'NUMBER'       # Numeric values
    BOOLEAN = 'BOOLEAN'     # True or False
    NULL = 'NULL'           # Null values
    EOF = 'EOF'             # End of input

# Creates Tokens based off the TokenType class when given the type and optional value parameter
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.type == TokenType.STRING:
            return f"<str, {self.value}>"
        elif self.type == TokenType.NUMBER:
            return f"<num, {self.value}>"
        elif self.type == TokenType.BOOLEAN:
            return f"<bool, {self.value}>"
        elif self.type == TokenType.LCURLY:
            return "<{>"
        elif self.type == TokenType.RCURLY:
            return "<}>"
        elif self.type == TokenType.LSQUARE:
            return "<[>"
        elif self.type == TokenType.RSQUARE:
            return "<]>"
        elif self.type == TokenType.COMMA:
            return "<,>"
        elif self.type == TokenType.COLON:
            return "<:>"
        else:
            return f"<{self.type}>"

# DFA Class responsible for doing state transitions for non-terminal data types
class DFA:
    # Defines states
    def __init__(self):
        self.states = {
            "START": 0,
            "INVALID": 1,
            "START_NUMBER": 2,
            "START_STRING": 3,
            "START_TRUE": 4,
            "START_FALSE": 5,
            "START_NULL": 6,

            "END_NUMBER": 7,
            "END_STRING": 8,

            "2_TRUE": 9,
            "3_TRUE": 10,
            "END_TRUE": 11,

            "2_FALSE": 12,
            "3_FALSE": 13,
            "4_FALSE": 14,
            "END_FALSE": 15,

            "2_NULL": 16,
            "3_NULL": 17,
            "END_NULL": 18,
        }

        self.current_state = self.states["START"]

    # Defines transitions
    def transition(self, symbol):

        # --- START DFA ---

        if self.current_state == self.states["START"]:
            if symbol.isdigit() or symbol in ['.', '-', '+']:
                self.current_state = self.states["START_NUMBER"]
            elif symbol == '"':
                self.current_state = self.states["START_STRING"]
            elif symbol == "t":
                self.current_state = self.states["START_TRUE"]
            elif symbol == "f":
                self.current_state = self.states["START_FALSE"]
            elif symbol == "n":
                self.current_state = self.states["START_NULL"]
            else:
                self.current_state = self.states["INVALID"]

        # --- NUMBER DFA ---

        elif self.current_state == self.states["START_NUMBER"]:
            if symbol.isdigit() or symbol in ['.', '-', '+']:
                self.current_state = self.states["START_NUMBER"]
            else:
                self.current_state = self.states["END_NUMBER"]
        elif self.current_state == self.states ["END_NUMBER"]:
            self.current_state = self.states["INVALID"]

        # --- STRING DFA ---

        elif self.current_state == self.states["START_STRING"]:
            if symbol == '"':
                self.current_state = self.states["END_STRING"]
            elif symbol in ['\n', '\t', '\r']:
                self.current_state = self.states["INVALID"]
            elif symbol == "\\":
                self.current_state = self.states["START_STRING"]
            else:
                self.current_state = self.states["START_STRING"]
        elif self.current_state == self.states["END_STRING"]:
            self.current_state = self.states["INVALID"]

        # --- TRUE DFA ---

        elif self.current_state == self.states["START_TRUE"]:
            if symbol == "r":
                self.current_state = self.states["2_TRUE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["2_TRUE"]:
            if symbol == "u":
                self.current_state = self.states["3_TRUE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["3_TRUE"]:
            if symbol == "e":
                self.current_state = self.states["END_TRUE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["END_TRUE"]:
            self.current_state = self.states["INVALID"]

        # --- FALSE DFA ---

        elif self.current_state == self.states["START_FALSE"]:
            if symbol == "a":
                self.current_state = self.states["2_FALSE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["2_FALSE"]:
            if symbol == "l":
                self.current_state = self.states["3_FALSE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["3_FALSE"]:
            if symbol == "s":
                self.current_state = self.states["4_FALSE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["4_FALSE"]:
            if symbol == "e":
                self.current_state = self.states["END_FALSE"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["END_FALSE"]:
            self.current_state = self.states["INVALID"]

        # --- NULL DFA ---

        elif self.current_state == self.states["START_NULL"]:
            if symbol == "u":
                self.current_state = self.states["2_NULL"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["2_NULL"]:
            if symbol == "l":
                self.current_state = self.states["3_NULL"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["3_NULL"]:
            if symbol == "l":
                self.current_state = self.states["END_NULL"]
            else:
                self.current_state = self.states["INVALID"]
        elif self.current_state == self.states["END_NULL"]:
            self.current_state = self.states["INVALID"]

        # --- INVALID DFA ---

        elif self.current_state == self.states["INVALID"]:
            self.current_state = self.states["INVALID"]

    # Resets DFA to start state
    def reset(self):
        self.current_state = self.states["START"]

    # Checks to see if current state is one of the final states
    def is_accepting(self):
        return self.current_state in [self.states["END_STRING"], self.states["END_NUMBER"], self.states["END_TRUE"],
                                      self.states["END_FALSE"], self.states["END_NULL"]]

# Exception to be raised in instance that character is invalid
class LexerError(Exception):
    def __init__(self, position, character):
        self.position = position
        self.character = character
        super().__init__(f"Invalid character '{character}' at position {position}")

class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.current_char = self.input_text[self.position] if self.input_text else None
        self.symbol_table = {}
        self.dfa = DFA()

    def advance(self):
        self.position += 1
        if self.position >= len(self.input_text):
            self.current_char = None
        else:
            self.current_char = self.input_text[self.position]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def recognize_number(self):
        result = ""
        stop_states = [self.dfa.states["END_NUMBER"], self.dfa.states["INVALID"]]

        while self.dfa.current_state not in stop_states:
            self.dfa.transition(self.current_char)
            if self.dfa.current_state not in stop_states:
                result += self.current_char
                self.advance()

        if self.dfa.is_accepting():
            return Token(TokenType.NUMBER, float(result))
        else:
            raise LexerError(self.position, self.current_char)

    def recognize_string(self):
        result = ""
        self.advance() # Skips beginning double quote
        stop_states = [self.dfa.states["END_STRING"], self.dfa.states["INVALID"]]

        while self.current_char is not None and self.dfa.current_state not in stop_states:
            self.dfa.transition(self.current_char)
            if self.dfa.current_state not in stop_states:
                result += self.current_char
                self.advance()

        if self.dfa.current_state == self.dfa.states["END_STRING"]:
            self.advance() # Skips end double quote
        else:
            raise LexerError(self.position, self.current_char)

        self.symbol_table[result] = "STRING"
        return Token(TokenType.STRING, result)

    def recognize_true(self):
        stop_states = [self.dfa.states["END_TRUE"], self.dfa.states["INVALID"]]

        while self.dfa.current_state not in stop_states:
            self.dfa.transition(self.current_char)
            if self.dfa.current_state not in stop_states:
                self.advance()

        if self.dfa.is_accepting():
            self.advance()
            return Token(TokenType.BOOLEAN, True)
        else:
            raise LexerError(self.position, self.current_char)

    def recognize_false(self):
        stop_states = [self.dfa.states["END_FALSE"], self.dfa.states["INVALID"]]

        while self.dfa.current_state not in stop_states:
            self.dfa.transition(self.current_char)
            if self.dfa.current_state not in stop_states:
                self.advance()

        if self.dfa.is_accepting():
            self.advance()
            return Token(TokenType.BOOLEAN, False)
        else:
            raise LexerError(self.position, self.current_char)

    def recognize_null(self):
        stop_states = [self.dfa.states["END_NULL"], self.dfa.states["INVALID"]]

        while self.dfa.current_state not in stop_states:
            self.dfa.transition(self.current_char)
            if self.dfa.current_state not in stop_states:
                self.advance()

        if self.dfa.is_accepting():
            # self.dfa.reset()
            self.advance()
            return Token(TokenType.NULL)
        else:
            raise LexerError(self.position, self.current_char)

    def get_next_token(self):
        self.dfa.reset()
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            elif self.current_char == '{':  # Terminals
                self.advance()
                return Token(TokenType.LCURLY)
            elif self.current_char == '}':
                self.advance()
                return Token(TokenType.RCURLY)
            elif self.current_char == '[':
                self.advance()
                return Token(TokenType.LSQUARE)
            elif self.current_char == ']':
                self.advance()
                return Token(TokenType.RSQUARE)
            elif self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA)
            elif self.current_char == ':':
                self.advance()
                return Token(TokenType.COLON)
            # Check for these BEFORE DFA transition
            elif self.current_char == 't':
                return self.recognize_true()
            elif self.current_char == 'f':
                return self.recognize_false()
            elif self.current_char == 'n':
                return self.recognize_null()
            else:  # Now handle numbers and strings
                self.dfa.transition(self.current_char)
                if self.dfa.current_state == self.dfa.states["START_NUMBER"]:
                    return self.recognize_number()
                elif self.dfa.current_state == self.dfa.states["START_STRING"]:
                    return self.recognize_string()
                else:
                    raise LexerError(self.position, self.current_char)
        return Token(TokenType.EOF)

    def tokenize(self):
        tokens = []
        while True:
            try:
                token = self.get_next_token()
            except LexerError as e:
                print(f"Lexical Error: {e}")
                break
            if token.type == TokenType.EOF:
                break
            tokens.append(token)
        return tokens

# Testing the Lexer with input
if __name__ == "__main__":
    for i in range(5):
        try:
            input_file = open(f'tests/input{i}.txt', 'r')
            input_string = input_file.read()
        except Exception as e:
            raise Exception("Couldn't open input text file")

        output = f'tokenized/tokens{i}.txt'
        lexer = Lexer(input_string)
        tokens = lexer.tokenize()

        try:
            output_file = open(output, 'w')
            for token in tokens:
                output_file.write(str(token) + "\n")
        except Exception as e:
            raise Exception("Couldn't write to output file")