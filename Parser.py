# Defines token types to be returned to the class Token
class TokenType:
    LCURLY = 'LCURLY'  # '{'
    RCURLY = 'RCURLY'  # '}'
    LSQUARE = 'LSQUARE'  # '['
    RSQUARE = 'RSQUARE'  # ']'
    COMMA = 'COMMA'  # ','
    COLON = 'COLON'  # ':'
    STRING = 'STRING'  # Strings
    NUMBER = 'NUMBER'  # Numeric values
    BOOLEAN = 'BOOLEAN'  # True or False
    NULL = 'NULL'  # Null values
    EOF = 'EOF'  # End of input


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


# Defines nodes in a tree
class Node:
    def __init__(self, label=None, branch_length=None, is_leaf=False):
        self.label = label
        self.branch_length = branch_length
        self.children = []
        self.is_leaf = is_leaf

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self, depth=-1, file=None):
        indent = "  " * depth
        if self.is_leaf:
            print(f"{indent}{self.label}", file=file)
        else:
            if self.label:
                label = self.label
                print(f"{indent}{label}", file=file)
            for child in self.children:
                child.print_tree(depth + 1, file=file)
        if self.branch_length is not None:
            print(f"{indent}{self.branch_length}", file=file)


# Defines the parser used to iterate over the input file
class Parser:
    def __init__(self, lexer):
        self.lexer = iter(lexer)
        self.current_token = Token(None)
        self.end_of_input = False
        self.index = 0
        self.errors = []
        self.dict_stack = []

    # Converts a string into a token if its a valid token
    def get_next_token(self):
        if self.end_of_input:
            self.current_token = Token(TokenType.EOF)
            return self.current_token
        try:
            token = next(self.lexer).strip()
            self.index += 1

            # removes whitespace in the text file between tokens
            while token == "":
                token = next(self.lexer).strip()
                self.index += 1

            if token == "<{>":
                self.current_token = Token(TokenType.LCURLY)
            elif token == "<}>":
                self.current_token = Token(TokenType.RCURLY)
            elif token == "<[>":
                self.current_token = Token(TokenType.LSQUARE)
            elif token == "<]>":
                self.current_token = Token(TokenType.RSQUARE)
            elif token == "<:>":
                self.current_token = Token(TokenType.COLON)
            elif token == "<,>":
                self.current_token = Token(TokenType.COMMA)
            elif token.startswith("<str, "):
                # takes rest of token as value
                val = token[6:-1]
                self.current_token = Token(TokenType.STRING, val)
            elif token.startswith("<num, "):
                # takes rest of token as value
                val = token[6:-1]
                self.current_token = Token(TokenType.NUMBER, val)
            elif token == ("<bool, True>"):
                self.current_token = Token(TokenType.BOOLEAN, True)
            elif token == ("<bool, False>"):
                self.current_token = Token(TokenType.BOOLEAN, False)
            elif token == ("<null>"):
                self.current_token = Token(TokenType.NULL)
            else:
                raise Exception(f"Invalid token format at line {self.index}: {token}")

        # hits end of file
        except StopIteration:
            self.current_token = Token(TokenType.EOF)
            self.end_of_input = True
        except Exception as e:
            raise Exception(f"Error processing token at line {self.index}: {str(e)}")

        return self.current_token

    # skips over token if token type is expected
    def eat(self, token_type):
        if self.current_token.type == token_type:
            token = self.current_token
            self.get_next_token()
            return token
        else:
            raise Exception(f"Expected token {token_type}, got {self.current_token.type} "
                            f"at line {self.index}")

    # starts recursive descent parsing
    def parse(self):
        try:
            self.get_next_token()
            return self.value()
        except Exception as e:
            raise Exception(f"Unexpected error while parsing: {str(e)}")

    # parses dictionaries
    def dict(self):
        self.eat(TokenType.LCURLY)
        self.dict_stack.append(set())

        node = Node(label="Dictionary")

        # checks for an empty dictionary
        if self.current_token.type == TokenType.RCURLY:
            self.eat(TokenType.RCURLY)
            return node

        pair_node = self.pair()
        node.add_child(pair_node)

        # iterates through the dictionary
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            pair_node = self.pair()
            node.add_child(pair_node)

        self.eat(TokenType.RCURLY)
        self.dict_stack.pop()
        return node

    # parses pairs
    def pair(self):
        if self.current_token.type != TokenType.STRING:
            raise Exception(f"Expected string key in pair, got {self.current_token.type}")

        node = Node(label="Pair")

        self.validate_empty_key(self.current_token.value)
        self.validate_reserved_key(self.current_token.value)
        self.validate_duplicate_keys(self.current_token.value)

        key = self.current_token.value
        self.eat(TokenType.STRING)
        self.eat(TokenType.COLON)

        node.add_child(Node(label=f"Key: {key}"))

        value_node = self.value()
        node.add_child(value_node)

        return node

    # parses values
    def value(self):
        node = Node()
        token = self.current_token

        if token.type == TokenType.STRING:
            self.validate_reserved_strings(token.value)
            self.eat(TokenType.STRING)
            node = Node(label=f"String: {token.value}")
            return node
        elif token.type == TokenType.NUMBER:
            self.validate_decimal_number(token.value)
            self.validate_number_format(token.value)
            self.eat(TokenType.NUMBER)
            node = Node(label=f"Number: {token.value}")
            return node
        elif token.type == TokenType.BOOLEAN:
            self.eat(TokenType.BOOLEAN)
            node = Node(label=f"Boolean: {token.value}")
            return node
        elif token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            node = Node(label="Null", is_leaf=True)
            return node
        elif token.type == TokenType.LCURLY:
            node.add_child(self.dict())
            return node
        elif token.type == TokenType.LSQUARE:
            node.add_child(self.list())
            return node
        else:
            raise Exception(f"Unexpected token in value: {token}")

    # parses lists
    def list(self):
        self.eat(TokenType.LSQUARE)

        node = Node(label="List")

        # checks for an empty list
        if self.current_token.type == TokenType.RSQUARE:
            self.eat(TokenType.RSQUARE)
            return node

        # get the first value and its type
        first_value = self.current_token
        first_type = first_value.type
        value_node = self.value()
        node.add_child(value_node)

        # iterates through the list values
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)

            # check if current value type matches first value type
            self.validate_list_types(first_type, self.current_token.type)

            value_node = self.value()
            node.add_child(value_node)

        self.eat(TokenType.RSQUARE)
        return node

    # Type 1 Error
    def validate_decimal_number(self, value):
        if isinstance(value, str) and '.' in value:
            parts = value.split('.')
            if len(parts) != 2 or not parts[0] or not parts[1]:
                self.errors.append(f"Type 1 Error at {value}: Invalid decimal number format")
                return False
        return True

    # Type 2 Error
    def validate_empty_key(self, key):
        if not key or key.strip() == "":
            self.errors.append("Type 2 Error: Empty dictionary key")
            return False
        return True

    # Type 3 Error
    def validate_number_format(self, value):
        if isinstance(value, str):
            # handle scientific notation
            value = value.lower()
            if 'e' in value:
                base, exp = value.split('e')
                if exp.startswith('+'):  # no leading + allowed
                    self.errors.append(f"Type 3 Error at {value}: Invalid number format - leading + in exponent")
                    return False
                try:
                    float(value)  # validate the entire number
                except ValueError:
                    self.errors.append(f"Type 3 Error at {value}: Invalid number format")
                    return False
            else:
                # check for leading zeros in non-decimal numbers
                if value.startswith('0') and len(value) > 1 and not value.startswith('0.'):
                    self.errors.append(f"Type 3 Error at {value}: Invalid number format - leading zeros")
                    return False
                # check for leading plus sign
                elif value.startswith('+'):
                    self.errors.append(f"Type 3 Error at {value}: Invalid number format - leading + sign")
                    return False
        return True

    # Type 4 Error
    def validate_reserved_key(self, key):
        reserved_words = ['true', 'false', 'null']
        if key.lower() in reserved_words:
            self.errors.append(f"Type 4 Error: Reserved word '{key}' cannot be used as dictionary key")
            return False
        return True

    # Type 5 Error
    def validate_duplicate_keys(self, key):
        if not self.dict_stack:  # Should never happen, but good to check
            raise Exception("Internal error: No dictionary scope found")

        current_dict_keys = self.dict_stack[-1]  # Get the current dictionary's keys

        if key in current_dict_keys:
            self.errors.append(f"Type 5 Error: Duplicate key '{key}' in dictionary")
            return False

        current_dict_keys.add(key)
        return True

    # Type 6 Error
    def validate_list_types(self, first_type, current_type):
        if first_type in [TokenType.LSQUARE, TokenType.LCURLY]:
            return True
        if current_type != first_type:
            self.errors.append("Type 6 Error: Inconsistent types in list")
            return False
        return True

    # Type 7 Error
    def validate_reserved_strings(self, value):
        reserved_words = ['true', 'false', 'null']
        if isinstance(value, str) and value.lower() in reserved_words:
            self.errors.append(f"Type 7 Error: Reserved word '{value}' cannot be used as a string")
            return False
        return True

    def errors_exist(self):
        if not self.errors:
            return True
        else:
            return False

    # Writes errors to output.txt
    def print_errors(self, file=None):
        try:
            for error in self.errors:
                print(error, file=file)
        except IOError as e:
            raise IOError(f"Couldn't write errors to output file: {e}")


if __name__ == "__main__":

    for i in range(5):
        try:
            input_file = open(f'tokenized/tokens{i}.txt', 'r')
            input_string = input_file.readlines()
        except Exception as e:
            raise Exception("Couldn't open input text file")

        output = f'outputs/output{i}.txt'
        parser = Parser(input_string)
        tree = parser.parse()

        if parser.errors_exist():
            # print abstract tree
            try:
                output_file = open(output, 'w')
                tree.print_tree(file=output_file)
            except Exception as e:
                raise Exception("Couldn't write to output file")
        else:
            # print syntactic errors
            try:
                output_file = open(output, 'w')
                parser.print_errors(file=output_file)
            except Exception as e:
                raise Exception("Couldn't write to output file")
