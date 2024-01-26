import configparser

# INI-style config file text
config_text = "[global]\nversion = 1.0\n\n\n\nname = something\n[section1]\nfruit = kiwi\ncolor=green\n[section2]\ncheese=brie\n"

# Parse the config text using configparser
config_parser = configparser.ConfigParser()
config_parser.read_string(config_text)

# CST (Concrete Syntax Tree) - The parsed data structure by configparser
cst = config_parser._sections

# AST (Abstract Syntax Tree) - A simplified representation focusing on semantics
ast = {section: dict(options) for section, options in config_parser.items()}

# Print the CST and AST
print("CST:")
print(cst)
print("\nAST:")
print(ast)
