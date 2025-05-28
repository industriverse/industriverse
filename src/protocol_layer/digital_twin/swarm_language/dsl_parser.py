"""
Digital Twin Swarm Language Parser for Industriverse Protocol Layer

This module implements the DSL Parser component of the Digital Twin Swarm Language,
enabling parsing and validation of declarative configurations for digital twin swarms.

Features:
1. Parsing of DTSL definitions
2. Validation of DTSL syntax and semantics
3. Transformation of DTSL to executable configurations
4. Schema validation and type checking
5. Error reporting and diagnostics
"""

import uuid
import time
import asyncio
import logging
import json
import re
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Token types for the DTSL parser."""
    IDENTIFIER = "identifier"
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    KEYWORD = "keyword"
    OPERATOR = "operator"
    PUNCTUATION = "punctuation"
    COMMENT = "comment"
    WHITESPACE = "whitespace"
    EOF = "eof"
    UNKNOWN = "unknown"


@dataclass
class Token:
    """
    Represents a token in the DTSL parser.
    """
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self) -> str:
        return f"{self.type.value}({self.value}) at {self.line}:{self.column}"


@dataclass
class ParseError:
    """
    Represents a parsing error in the DTSL parser.
    """
    message: str
    line: int
    column: int
    context: str = ""
    
    def __str__(self) -> str:
        if self.context:
            return f"Error at {self.line}:{self.column}: {self.message}\nContext: {self.context}"
        else:
            return f"Error at {self.line}:{self.column}: {self.message}"


class DTSLLexer:
    """
    Lexer for the Digital Twin Swarm Language.
    """
    
    # Token patterns
    PATTERNS = [
        (r'[ \t\r\n]+', TokenType.WHITESPACE),
        (r'//.*$', TokenType.COMMENT),
        (r'/\*[\s\S]*?\*/', TokenType.COMMENT),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.IDENTIFIER),
        (r'-?\d+\.\d+', TokenType.NUMBER),
        (r'-?\d+', TokenType.NUMBER),
        (r'"(?:\\.|[^"\\])*"', TokenType.STRING),
        (r"'(?:\\.|[^'\\])*'", TokenType.STRING),
        (r'==|!=|<=|>=|<|>|\+|-|\*|/|=', TokenType.OPERATOR),
        (r'[{}()\[\],;:]', TokenType.PUNCTUATION),
    ]
    
    # Keywords
    KEYWORDS = {
        'twin', 'swarm', 'event', 'action', 'rule', 'when', 'then', 'if', 'else',
        'for', 'in', 'true', 'false', 'null', 'import', 'export', 'as', 'from',
        'sensor', 'actuator', 'property', 'state', 'transition', 'threshold',
        'alert', 'log', 'notify', 'schedule', 'interval', 'timeout', 'retry'
    }
    
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.errors: List[ParseError] = []
        self.pos = 0
        self.line = 1
        self.column = 1
    
    def tokenize(self) -> Tuple[List[Token], List[ParseError]]:
        """Tokenize the source code."""
        while self.pos < len(self.source):
            matched = False
            
            # Try to match a pattern
            for pattern, token_type in self.PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.source[self.pos:])
                
                if match:
                    value = match.group(0)
                    
                    # Skip whitespace and comments
                    if token_type not in (TokenType.WHITESPACE, TokenType.COMMENT):
                        # Check if identifier is a keyword
                        if token_type == TokenType.IDENTIFIER and value in self.KEYWORDS:
                            token_type = TokenType.KEYWORD
                        
                        # Handle boolean literals
                        if token_type == TokenType.IDENTIFIER and value.lower() in ('true', 'false'):
                            token_type = TokenType.BOOLEAN
                        
                        # Create token
                        token = Token(
                            type=token_type,
                            value=value,
                            line=self.line,
                            column=self.column
                        )
                        self.tokens.append(token)
                    
                    # Update position and line/column
                    for char in value:
                        if char == '\n':
                            self.line += 1
                            self.column = 1
                        else:
                            self.column += 1
                    
                    self.pos += len(value)
                    matched = True
                    break
            
            # If no pattern matched, report error and skip character
            if not matched:
                error = ParseError(
                    message=f"Unexpected character: '{self.source[self.pos]}'",
                    line=self.line,
                    column=self.column,
                    context=self._get_context()
                )
                self.errors.append(error)
                
                self.pos += 1
                self.column += 1
        
        # Add EOF token
        self.tokens.append(Token(
            type=TokenType.EOF,
            value="",
            line=self.line,
            column=self.column
        ))
        
        return self.tokens, self.errors
    
    def _get_context(self) -> str:
        """Get the context around the current position for error reporting."""
        start = max(0, self.pos - 20)
        end = min(len(self.source), self.pos + 20)
        before = self.source[start:self.pos]
        after = self.source[self.pos:end]
        pointer = " " * len(before) + "^"
        return f"{before}{after}\n{pointer}"


class DTSLParser:
    """
    Parser for the Digital Twin Swarm Language.
    """
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.errors: List[ParseError] = []
        self.current = 0
    
    def parse(self, source: str) -> Tuple[Dict[str, Any], List[ParseError]]:
        """Parse DTSL source code."""
        # Tokenize the source
        lexer = DTSLLexer(source)
        self.tokens, lexer_errors = lexer.tokenize()
        self.errors = lexer_errors.copy()
        self.current = 0
        
        # If there are lexer errors, return empty AST
        if lexer_errors:
            return {}, self.errors
        
        # Parse the program
        try:
            ast = self._parse_program()
            return ast, self.errors
        except Exception as e:
            # Catch any unexpected errors
            error = ParseError(
                message=f"Unexpected error: {str(e)}",
                line=self._current_token().line,
                column=self._current_token().column
            )
            self.errors.append(error)
            return {}, self.errors
    
    def _parse_program(self) -> Dict[str, Any]:
        """Parse a complete DTSL program."""
        declarations = []
        
        while not self._is_at_end():
            try:
                declaration = self._parse_declaration()
                if declaration:
                    declarations.append(declaration)
            except Exception as e:
                # Report error and synchronize
                error = ParseError(
                    message=str(e),
                    line=self._current_token().line,
                    column=self._current_token().column,
                    context=self._get_context()
                )
                self.errors.append(error)
                self._synchronize()
        
        return {
            "type": "program",
            "declarations": declarations
        }
    
    def _parse_declaration(self) -> Dict[str, Any]:
        """Parse a declaration."""
        token = self._current_token()
        
        if self._match(TokenType.KEYWORD, "twin"):
            return self._parse_twin_declaration()
        elif self._match(TokenType.KEYWORD, "swarm"):
            return self._parse_swarm_declaration()
        elif self._match(TokenType.KEYWORD, "event"):
            return self._parse_event_declaration()
        elif self._match(TokenType.KEYWORD, "action"):
            return self._parse_action_declaration()
        elif self._match(TokenType.KEYWORD, "rule"):
            return self._parse_rule_declaration()
        elif self._match(TokenType.KEYWORD, "import"):
            return self._parse_import_declaration()
        else:
            raise Exception(f"Expected declaration, got {token.type.value} '{token.value}'")
    
    def _parse_twin_declaration(self) -> Dict[str, Any]:
        """Parse a twin declaration."""
        # 'twin' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected twin name")
        
        # Parse optional extends clause
        extends = None
        if self._match(TokenType.KEYWORD, "extends"):
            extends = self._consume(TokenType.IDENTIFIER, "Expected parent twin name").value
        
        self._consume(TokenType.PUNCTUATION, "Expected '{' after twin name", "{")
        
        # Parse twin body
        properties = []
        sensors = []
        actuators = []
        states = []
        
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            if self._match(TokenType.KEYWORD, "property"):
                properties.append(self._parse_property())
            elif self._match(TokenType.KEYWORD, "sensor"):
                sensors.append(self._parse_sensor())
            elif self._match(TokenType.KEYWORD, "actuator"):
                actuators.append(self._parse_actuator())
            elif self._match(TokenType.KEYWORD, "state"):
                states.append(self._parse_state())
            else:
                token = self._current_token()
                raise Exception(f"Unexpected token in twin body: {token.type.value} '{token.value}'")
        
        self._consume(TokenType.PUNCTUATION, "Expected '}' after twin body", "}")
        
        return {
            "type": "twin_declaration",
            "name": name.value,
            "extends": extends,
            "properties": properties,
            "sensors": sensors,
            "actuators": actuators,
            "states": states
        }
    
    def _parse_property(self) -> Dict[str, Any]:
        """Parse a property declaration."""
        # 'property' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected property name")
        
        # Parse type
        self._consume(TokenType.PUNCTUATION, "Expected ':' after property name", ":")
        type_token = self._consume(TokenType.IDENTIFIER, "Expected property type")
        
        # Parse optional default value
        default_value = None
        if self._match(TokenType.OPERATOR, "="):
            default_value = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ';' after property declaration", ";")
        
        return {
            "type": "property_declaration",
            "name": name.value,
            "property_type": type_token.value,
            "default_value": default_value
        }
    
    def _parse_sensor(self) -> Dict[str, Any]:
        """Parse a sensor declaration."""
        # 'sensor' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected sensor name")
        
        # Parse type
        self._consume(TokenType.PUNCTUATION, "Expected ':' after sensor name", ":")
        type_token = self._consume(TokenType.IDENTIFIER, "Expected sensor type")
        
        # Parse configuration
        config = {}
        if self._match(TokenType.PUNCTUATION, "{"):
            config = self._parse_config_block()
        else:
            self._consume(TokenType.PUNCTUATION, "Expected ';' after sensor declaration", ";")
        
        return {
            "type": "sensor_declaration",
            "name": name.value,
            "sensor_type": type_token.value,
            "config": config
        }
    
    def _parse_actuator(self) -> Dict[str, Any]:
        """Parse an actuator declaration."""
        # 'actuator' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected actuator name")
        
        # Parse type
        self._consume(TokenType.PUNCTUATION, "Expected ':' after actuator name", ":")
        type_token = self._consume(TokenType.IDENTIFIER, "Expected actuator type")
        
        # Parse configuration
        config = {}
        if self._match(TokenType.PUNCTUATION, "{"):
            config = self._parse_config_block()
        else:
            self._consume(TokenType.PUNCTUATION, "Expected ';' after actuator declaration", ";")
        
        return {
            "type": "actuator_declaration",
            "name": name.value,
            "actuator_type": type_token.value,
            "config": config
        }
    
    def _parse_state(self) -> Dict[str, Any]:
        """Parse a state declaration."""
        # 'state' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected state name")
        
        self._consume(TokenType.PUNCTUATION, "Expected '{' after state name", "{")
        
        # Parse state body
        entry_actions = []
        exit_actions = []
        transitions = []
        
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            if self._match(TokenType.KEYWORD, "entry"):
                entry_actions.append(self._parse_action_reference())
            elif self._match(TokenType.KEYWORD, "exit"):
                exit_actions.append(self._parse_action_reference())
            elif self._match(TokenType.KEYWORD, "transition"):
                transitions.append(self._parse_transition())
            else:
                token = self._current_token()
                raise Exception(f"Unexpected token in state body: {token.type.value} '{token.value}'")
        
        self._consume(TokenType.PUNCTUATION, "Expected '}' after state body", "}")
        
        return {
            "type": "state_declaration",
            "name": name.value,
            "entry_actions": entry_actions,
            "exit_actions": exit_actions,
            "transitions": transitions
        }
    
    def _parse_transition(self) -> Dict[str, Any]:
        """Parse a state transition."""
        # 'transition' keyword already consumed
        target = self._consume(TokenType.IDENTIFIER, "Expected target state name")
        
        # Parse condition
        condition = None
        if self._match(TokenType.KEYWORD, "when"):
            condition = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ';' after transition", ";")
        
        return {
            "type": "transition",
            "target": target.value,
            "condition": condition
        }
    
    def _parse_swarm_declaration(self) -> Dict[str, Any]:
        """Parse a swarm declaration."""
        # 'swarm' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected swarm name")
        
        self._consume(TokenType.PUNCTUATION, "Expected '{' after swarm name", "{")
        
        # Parse swarm body
        twins = []
        rules = []
        
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            if self._match(TokenType.KEYWORD, "twin"):
                twins.append(self._parse_twin_reference())
            elif self._match(TokenType.KEYWORD, "rule"):
                rules.append(self._parse_rule_reference())
            else:
                token = self._current_token()
                raise Exception(f"Unexpected token in swarm body: {token.type.value} '{token.value}'")
        
        self._consume(TokenType.PUNCTUATION, "Expected '}' after swarm body", "}")
        
        return {
            "type": "swarm_declaration",
            "name": name.value,
            "twins": twins,
            "rules": rules
        }
    
    def _parse_twin_reference(self) -> Dict[str, Any]:
        """Parse a twin reference in a swarm."""
        # 'twin' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected twin name")
        
        # Parse optional instance name
        instance_name = None
        if self._match(TokenType.KEYWORD, "as"):
            instance_name = self._consume(TokenType.IDENTIFIER, "Expected instance name").value
        
        # Parse optional count
        count = None
        if self._match(TokenType.PUNCTUATION, "["):
            count = self._parse_expression()
            self._consume(TokenType.PUNCTUATION, "Expected ']' after count", "]")
        
        self._consume(TokenType.PUNCTUATION, "Expected ';' after twin reference", ";")
        
        return {
            "type": "twin_reference",
            "twin_name": name.value,
            "instance_name": instance_name,
            "count": count
        }
    
    def _parse_event_declaration(self) -> Dict[str, Any]:
        """Parse an event declaration."""
        # 'event' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected event name")
        
        # Parse parameters
        parameters = []
        if self._match(TokenType.PUNCTUATION, "("):
            if not self._check(TokenType.PUNCTUATION, ")"):
                parameters = self._parse_parameter_list()
            self._consume(TokenType.PUNCTUATION, "Expected ')' after parameters", ")")
        
        self._consume(TokenType.PUNCTUATION, "Expected ';' after event declaration", ";")
        
        return {
            "type": "event_declaration",
            "name": name.value,
            "parameters": parameters
        }
    
    def _parse_action_declaration(self) -> Dict[str, Any]:
        """Parse an action declaration."""
        # 'action' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected action name")
        
        # Parse parameters
        parameters = []
        if self._match(TokenType.PUNCTUATION, "("):
            if not self._check(TokenType.PUNCTUATION, ")"):
                parameters = self._parse_parameter_list()
            self._consume(TokenType.PUNCTUATION, "Expected ')' after parameters", ")")
        
        # Parse body
        self._consume(TokenType.PUNCTUATION, "Expected '{' after action header", "{")
        body = self._parse_action_body()
        self._consume(TokenType.PUNCTUATION, "Expected '}' after action body", "}")
        
        return {
            "type": "action_declaration",
            "name": name.value,
            "parameters": parameters,
            "body": body
        }
    
    def _parse_parameter_list(self) -> List[Dict[str, Any]]:
        """Parse a list of parameters."""
        parameters = []
        
        # Parse first parameter
        parameters.append(self._parse_parameter())
        
        # Parse additional parameters
        while self._match(TokenType.PUNCTUATION, ","):
            parameters.append(self._parse_parameter())
        
        return parameters
    
    def _parse_parameter(self) -> Dict[str, Any]:
        """Parse a parameter."""
        name = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
        
        # Parse type
        self._consume(TokenType.PUNCTUATION, "Expected ':' after parameter name", ":")
        type_token = self._consume(TokenType.IDENTIFIER, "Expected parameter type")
        
        return {
            "type": "parameter",
            "name": name.value,
            "parameter_type": type_token.value
        }
    
    def _parse_action_body(self) -> List[Dict[str, Any]]:
        """Parse an action body."""
        statements = []
        
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            statements.append(self._parse_statement())
        
        return statements
    
    def _parse_statement(self) -> Dict[str, Any]:
        """Parse a statement."""
        if self._match(TokenType.KEYWORD, "if"):
            return self._parse_if_statement()
        elif self._match(TokenType.KEYWORD, "for"):
            return self._parse_for_statement()
        elif self._match(TokenType.KEYWORD, "log"):
            return self._parse_log_statement()
        elif self._match(TokenType.KEYWORD, "alert"):
            return self._parse_alert_statement()
        elif self._match(TokenType.KEYWORD, "notify"):
            return self._parse_notify_statement()
        elif self._check(TokenType.IDENTIFIER):
            return self._parse_assignment_or_call()
        else:
            token = self._current_token()
            raise Exception(f"Unexpected token in statement: {token.type.value} '{token.value}'")
    
    def _parse_if_statement(self) -> Dict[str, Any]:
        """Parse an if statement."""
        # 'if' keyword already consumed
        self._consume(TokenType.PUNCTUATION, "Expected '(' after 'if'", "(")
        condition = self._parse_expression()
        self._consume(TokenType.PUNCTUATION, "Expected ')' after condition", ")")
        
        # Parse then branch
        self._consume(TokenType.PUNCTUATION, "Expected '{' after condition", "{")
        then_branch = []
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            then_branch.append(self._parse_statement())
        self._consume(TokenType.PUNCTUATION, "Expected '}' after then branch", "}")
        
        # Parse optional else branch
        else_branch = []
        if self._match(TokenType.KEYWORD, "else"):
            if self._match(TokenType.KEYWORD, "if"):
                # This is an else-if
                else_branch = [self._parse_if_statement()]
            else:
                # This is a regular else
                self._consume(TokenType.PUNCTUATION, "Expected '{' after 'else'", "{")
                while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
                    else_branch.append(self._parse_statement())
                self._consume(TokenType.PUNCTUATION, "Expected '}' after else branch", "}")
        
        return {
            "type": "if_statement",
            "condition": condition,
            "then_branch": then_branch,
            "else_branch": else_branch
        }
    
    def _parse_for_statement(self) -> Dict[str, Any]:
        """Parse a for statement."""
        # 'for' keyword already consumed
        self._consume(TokenType.PUNCTUATION, "Expected '(' after 'for'", "(")
        variable = self._consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        self._consume(TokenType.KEYWORD, "Expected 'in' after variable name", "in")
        
        # Parse iterable
        iterable = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ')' after iterable", ")")
        
        # Parse body
        self._consume(TokenType.PUNCTUATION, "Expected '{' after for header", "{")
        body = []
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            body.append(self._parse_statement())
        self._consume(TokenType.PUNCTUATION, "Expected '}' after for body", "}")
        
        return {
            "type": "for_statement",
            "variable": variable,
            "iterable": iterable,
            "body": body
        }
    
    def _parse_log_statement(self) -> Dict[str, Any]:
        """Parse a log statement."""
        # 'log' keyword already consumed
        self._consume(TokenType.PUNCTUATION, "Expected '(' after 'log'", "(")
        message = self._parse_expression()
        
        # Parse optional level
        level = None
        if self._match(TokenType.PUNCTUATION, ","):
            level = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ')' after log arguments", ")")
        self._consume(TokenType.PUNCTUATION, "Expected ';' after log statement", ";")
        
        return {
            "type": "log_statement",
            "message": message,
            "level": level
        }
    
    def _parse_alert_statement(self) -> Dict[str, Any]:
        """Parse an alert statement."""
        # 'alert' keyword already consumed
        self._consume(TokenType.PUNCTUATION, "Expected '(' after 'alert'", "(")
        message = self._parse_expression()
        
        # Parse optional severity
        severity = None
        if self._match(TokenType.PUNCTUATION, ","):
            severity = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ')' after alert arguments", ")")
        self._consume(TokenType.PUNCTUATION, "Expected ';' after alert statement", ";")
        
        return {
            "type": "alert_statement",
            "message": message,
            "severity": severity
        }
    
    def _parse_notify_statement(self) -> Dict[str, Any]:
        """Parse a notify statement."""
        # 'notify' keyword already consumed
        self._consume(TokenType.PUNCTUATION, "Expected '(' after 'notify'", "(")
        target = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ',' after notify target", ",")
        message = self._parse_expression()
        
        # Parse optional data
        data = None
        if self._match(TokenType.PUNCTUATION, ","):
            data = self._parse_expression()
        
        self._consume(TokenType.PUNCTUATION, "Expected ')' after notify arguments", ")")
        self._consume(TokenType.PUNCTUATION, "Expected ';' after notify statement", ";")
        
        return {
            "type": "notify_statement",
            "target": target,
            "message": message,
            "data": data
        }
    
    def _parse_assignment_or_call(self) -> Dict[str, Any]:
        """Parse an assignment or function call."""
        name = self._consume(TokenType.IDENTIFIER, "Expected identifier")
        
        # Check if this is a function call
        if self._check(TokenType.PUNCTUATION, "("):
            return self._parse_function_call(name.value)
        
        # This is an assignment
        self._consume(TokenType.OPERATOR, "Expected '=' in assignment", "=")
        value = self._parse_expression()
        self._consume(TokenType.PUNCTUATION, "Expected ';' after assignment", ";")
        
        return {
            "type": "assignment",
            "name": name.value,
            "value": value
        }
    
    def _parse_function_call(self, name: str) -> Dict[str, Any]:
        """Parse a function call."""
        self._consume(TokenType.PUNCTUATION, "Expected '(' in function call", "(")
        
        # Parse arguments
        arguments = []
        if not self._check(TokenType.PUNCTUATION, ")"):
            arguments.append(self._parse_expression())
            while self._match(TokenType.PUNCTUATION, ","):
                arguments.append(self._parse_expression())
        
        self._consume(TokenType.PUNCTUATION, "Expected ')' after arguments", ")")
        self._consume(TokenType.PUNCTUATION, "Expected ';' after function call", ";")
        
        return {
            "type": "function_call",
            "name": name,
            "arguments": arguments
        }
    
    def _parse_rule_declaration(self) -> Dict[str, Any]:
        """Parse a rule declaration."""
        # 'rule' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected rule name")
        
        self._consume(TokenType.PUNCTUATION, "Expected '{' after rule name", "{")
        
        # Parse when clause
        self._consume(TokenType.KEYWORD, "Expected 'when' in rule", "when")
        condition = self._parse_expression()
        self._consume(TokenType.PUNCTUATION, "Expected ';' after condition", ";")
        
        # Parse then clause
        self._consume(TokenType.KEYWORD, "Expected 'then' in rule", "then")
        self._consume(TokenType.PUNCTUATION, "Expected '{' after 'then'", "{")
        actions = []
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            actions.append(self._parse_statement())
        self._consume(TokenType.PUNCTUATION, "Expected '}' after actions", "}")
        
        self._consume(TokenType.PUNCTUATION, "Expected '}' after rule body", "}")
        
        return {
            "type": "rule_declaration",
            "name": name.value,
            "condition": condition,
            "actions": actions
        }
    
    def _parse_rule_reference(self) -> Dict[str, Any]:
        """Parse a rule reference in a swarm."""
        # 'rule' keyword already consumed
        name = self._consume(TokenType.IDENTIFIER, "Expected rule name")
        self._consume(TokenType.PUNCTUATION, "Expected ';' after rule reference", ";")
        
        return {
            "type": "rule_reference",
            "rule_name": name.value
        }
    
    def _parse_action_reference(self) -> Dict[str, Any]:
        """Parse an action reference."""
        name = self._consume(TokenType.IDENTIFIER, "Expected action name")
        
        # Parse arguments
        arguments = []
        if self._match(TokenType.PUNCTUATION, "("):
            if not self._check(TokenType.PUNCTUATION, ")"):
                arguments.append(self._parse_expression())
                while self._match(TokenType.PUNCTUATION, ","):
                    arguments.append(self._parse_expression())
            self._consume(TokenType.PUNCTUATION, "Expected ')' after arguments", ")")
        
        self._consume(TokenType.PUNCTUATION, "Expected ';' after action reference", ";")
        
        return {
            "type": "action_reference",
            "action_name": name.value,
            "arguments": arguments
        }
    
    def _parse_import_declaration(self) -> Dict[str, Any]:
        """Parse an import declaration."""
        # 'import' keyword already consumed
        what = self._consume(TokenType.IDENTIFIER, "Expected import name")
        
        # Parse optional 'from' clause
        source = None
        if self._match(TokenType.KEYWORD, "from"):
            source = self._consume(TokenType.STRING, "Expected source path").value
            # Remove quotes
            source = source[1:-1]
        
        self._consume(TokenType.PUNCTUATION, "Expected ';' after import declaration", ";")
        
        return {
            "type": "import_declaration",
            "what": what.value,
            "source": source
        }
    
    def _parse_config_block(self) -> Dict[str, Any]:
        """Parse a configuration block."""
        config = {}
        
        while not self._check(TokenType.PUNCTUATION, "}") and not self._is_at_end():
            key = self._consume(TokenType.IDENTIFIER, "Expected config key").value
            self._consume(TokenType.PUNCTUATION, "Expected ':' after config key", ":")
            value = self._parse_expression()
            config[key] = value
            
            # Expect comma or closing brace
            if not self._check(TokenType.PUNCTUATION, "}"):
                self._consume(TokenType.PUNCTUATION, "Expected ',' after config item", ",")
        
        self._consume(TokenType.PUNCTUATION, "Expected '}' after config block", "}")
        
        return config
    
    def _parse_expression(self) -> Dict[str, Any]:
        """Parse an expression."""
        return self._parse_logical_or()
    
    def _parse_logical_or(self) -> Dict[str, Any]:
        """Parse a logical OR expression."""
        expr = self._parse_logical_and()
        
        while self._match(TokenType.OPERATOR, "||"):
            operator = self._previous()
            right = self._parse_logical_and()
            expr = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": expr,
                "right": right
            }
        
        return expr
    
    def _parse_logical_and(self) -> Dict[str, Any]:
        """Parse a logical AND expression."""
        expr = self._parse_equality()
        
        while self._match(TokenType.OPERATOR, "&&"):
            operator = self._previous()
            right = self._parse_equality()
            expr = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": expr,
                "right": right
            }
        
        return expr
    
    def _parse_equality(self) -> Dict[str, Any]:
        """Parse an equality expression."""
        expr = self._parse_comparison()
        
        while self._match_any(TokenType.OPERATOR, ["==", "!="]):
            operator = self._previous()
            right = self._parse_comparison()
            expr = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": expr,
                "right": right
            }
        
        return expr
    
    def _parse_comparison(self) -> Dict[str, Any]:
        """Parse a comparison expression."""
        expr = self._parse_term()
        
        while self._match_any(TokenType.OPERATOR, ["<", ">", "<=", ">="]):
            operator = self._previous()
            right = self._parse_term()
            expr = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": expr,
                "right": right
            }
        
        return expr
    
    def _parse_term(self) -> Dict[str, Any]:
        """Parse a term expression."""
        expr = self._parse_factor()
        
        while self._match_any(TokenType.OPERATOR, ["+", "-"]):
            operator = self._previous()
            right = self._parse_factor()
            expr = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": expr,
                "right": right
            }
        
        return expr
    
    def _parse_factor(self) -> Dict[str, Any]:
        """Parse a factor expression."""
        expr = self._parse_unary()
        
        while self._match_any(TokenType.OPERATOR, ["*", "/"]):
            operator = self._previous()
            right = self._parse_unary()
            expr = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": expr,
                "right": right
            }
        
        return expr
    
    def _parse_unary(self) -> Dict[str, Any]:
        """Parse a unary expression."""
        if self._match_any(TokenType.OPERATOR, ["!", "-"]):
            operator = self._previous()
            right = self._parse_unary()
            return {
                "type": "unary_expression",
                "operator": operator.value,
                "right": right
            }
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Dict[str, Any]:
        """Parse a primary expression."""
        if self._match(TokenType.BOOLEAN):
            return {
                "type": "literal",
                "value": self._previous().value.lower() == "true",
                "literal_type": "boolean"
            }
        
        if self._match(TokenType.NUMBER):
            value = self._previous().value
            if "." in value:
                return {
                    "type": "literal",
                    "value": float(value),
                    "literal_type": "number"
                }
            else:
                return {
                    "type": "literal",
                    "value": int(value),
                    "literal_type": "number"
                }
        
        if self._match(TokenType.STRING):
            value = self._previous().value
            # Remove quotes
            value = value[1:-1]
            return {
                "type": "literal",
                "value": value,
                "literal_type": "string"
            }
        
        if self._match(TokenType.KEYWORD, "null"):
            return {
                "type": "literal",
                "value": None,
                "literal_type": "null"
            }
        
        if self._match(TokenType.PUNCTUATION, "("):
            expr = self._parse_expression()
            self._consume(TokenType.PUNCTUATION, "Expected ')' after expression", ")")
            return {
                "type": "grouping",
                "expression": expr
            }
        
        if self._match(TokenType.PUNCTUATION, "["):
            elements = []
            if not self._check(TokenType.PUNCTUATION, "]"):
                elements.append(self._parse_expression())
                while self._match(TokenType.PUNCTUATION, ","):
                    elements.append(self._parse_expression())
            self._consume(TokenType.PUNCTUATION, "Expected ']' after array elements", "]")
            return {
                "type": "array_literal",
                "elements": elements
            }
        
        if self._match(TokenType.PUNCTUATION, "{"):
            properties = {}
            if not self._check(TokenType.PUNCTUATION, "}"):
                key = self._consume(TokenType.STRING, "Expected string key in object literal").value
                # Remove quotes
                key = key[1:-1]
                self._consume(TokenType.PUNCTUATION, "Expected ':' after object key", ":")
                value = self._parse_expression()
                properties[key] = value
                
                while self._match(TokenType.PUNCTUATION, ","):
                    if self._check(TokenType.PUNCTUATION, "}"):
                        break
                    key = self._consume(TokenType.STRING, "Expected string key in object literal").value
                    # Remove quotes
                    key = key[1:-1]
                    self._consume(TokenType.PUNCTUATION, "Expected ':' after object key", ":")
                    value = self._parse_expression()
                    properties[key] = value
            self._consume(TokenType.PUNCTUATION, "Expected '}' after object properties", "}")
            return {
                "type": "object_literal",
                "properties": properties
            }
        
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            
            # Check for function call
            if self._match(TokenType.PUNCTUATION, "("):
                arguments = []
                if not self._check(TokenType.PUNCTUATION, ")"):
                    arguments.append(self._parse_expression())
                    while self._match(TokenType.PUNCTUATION, ","):
                        arguments.append(self._parse_expression())
                self._consume(TokenType.PUNCTUATION, "Expected ')' after arguments", ")")
                return {
                    "type": "call_expression",
                    "callee": name,
                    "arguments": arguments
                }
            
            # Check for property access
            if self._match(TokenType.PUNCTUATION, "."):
                property_name = self._consume(TokenType.IDENTIFIER, "Expected property name").value
                return {
                    "type": "property_access",
                    "object": name,
                    "property": property_name
                }
            
            # Simple variable reference
            return {
                "type": "variable_reference",
                "name": name
            }
        
        token = self._current_token()
        raise Exception(f"Unexpected token in expression: {token.type.value} '{token.value}'")
    
    # --- Helper methods ---
    
    def _current_token(self) -> Token:
        """Get the current token."""
        if self._is_at_end():
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Get the previous token."""
        return self.tokens[self.current - 1]
    
    def _advance(self) -> Token:
        """Advance to the next token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of the tokens."""
        return self._current_token().type == TokenType.EOF
    
    def _check(self, type: TokenType, value: str = None) -> bool:
        """Check if the current token matches the given type and value."""
        if self._is_at_end():
            return False
        
        token = self._current_token()
        if token.type != type:
            return False
        
        if value is not None and token.value != value:
            return False
        
        return True
    
    def _match(self, type: TokenType, value: str = None) -> bool:
        """Match the current token against the given type and value."""
        if self._check(type, value):
            self._advance()
            return True
        return False
    
    def _match_any(self, type: TokenType, values: List[str]) -> bool:
        """Match the current token against any of the given values."""
        for value in values:
            if self._match(type, value):
                return True
        return False
    
    def _consume(self, type: TokenType, message: str, value: str = None) -> Token:
        """Consume the current token if it matches, otherwise report an error."""
        if self._check(type, value):
            return self._advance()
        
        token = self._current_token()
        error = ParseError(
            message=message,
            line=token.line,
            column=token.column,
            context=self._get_context()
        )
        self.errors.append(error)
        raise Exception(message)
    
    def _synchronize(self) -> None:
        """Synchronize the parser after an error."""
        self._advance()
        
        while not self._is_at_end():
            # Synchronize at statement boundaries
            if self._previous().value == ";":
                return
            
            if self._current_token().type == TokenType.KEYWORD:
                if self._current_token().value in {"twin", "swarm", "event", "action", "rule", "import"}:
                    return
            
            self._advance()
    
    def _get_context(self) -> str:
        """Get the context around the current token for error reporting."""
        if self._is_at_end():
            return "<end of file>"
        
        token = self._current_token()
        line = token.line
        
        # Find the line in the source
        lines = self.tokens[0].value.split("\n")
        if line <= len(lines):
            return lines[line - 1]
        
        return "<unknown context>"


class DTSLValidator:
    """
    Validator for the Digital Twin Swarm Language.
    """
    
    def __init__(self):
        self.errors: List[ParseError] = []
    
    def validate(self, ast: Dict[str, Any]) -> List[ParseError]:
        """Validate a DTSL AST."""
        self.errors = []
        
        # Validate program
        if ast.get("type") != "program":
            self.errors.append(ParseError(
                message="Expected program as root node",
                line=0,
                column=0
            ))
            return self.errors
        
        # Collect declarations
        declarations = ast.get("declarations", [])
        
        # Validate declarations
        for declaration in declarations:
            self._validate_declaration(declaration)
        
        return self.errors
    
    def _validate_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate a declaration."""
        declaration_type = declaration.get("type")
        
        if declaration_type == "twin_declaration":
            self._validate_twin_declaration(declaration)
        elif declaration_type == "swarm_declaration":
            self._validate_swarm_declaration(declaration)
        elif declaration_type == "event_declaration":
            self._validate_event_declaration(declaration)
        elif declaration_type == "action_declaration":
            self._validate_action_declaration(declaration)
        elif declaration_type == "rule_declaration":
            self._validate_rule_declaration(declaration)
        elif declaration_type == "import_declaration":
            self._validate_import_declaration(declaration)
        else:
            self.errors.append(ParseError(
                message=f"Unknown declaration type: {declaration_type}",
                line=0,
                column=0
            ))
    
    def _validate_twin_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate a twin declaration."""
        # Validate name
        if not declaration.get("name"):
            self.errors.append(ParseError(
                message="Twin declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate properties
        for prop in declaration.get("properties", []):
            self._validate_property(prop)
        
        # Validate sensors
        for sensor in declaration.get("sensors", []):
            self._validate_sensor(sensor)
        
        # Validate actuators
        for actuator in declaration.get("actuators", []):
            self._validate_actuator(actuator)
        
        # Validate states
        for state in declaration.get("states", []):
            self._validate_state(state)
    
    def _validate_property(self, prop: Dict[str, Any]) -> None:
        """Validate a property declaration."""
        # Validate name
        if not prop.get("name"):
            self.errors.append(ParseError(
                message="Property declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate type
        if not prop.get("property_type"):
            self.errors.append(ParseError(
                message="Property declaration must have a type",
                line=0,
                column=0
            ))
    
    def _validate_sensor(self, sensor: Dict[str, Any]) -> None:
        """Validate a sensor declaration."""
        # Validate name
        if not sensor.get("name"):
            self.errors.append(ParseError(
                message="Sensor declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate type
        if not sensor.get("sensor_type"):
            self.errors.append(ParseError(
                message="Sensor declaration must have a type",
                line=0,
                column=0
            ))
    
    def _validate_actuator(self, actuator: Dict[str, Any]) -> None:
        """Validate an actuator declaration."""
        # Validate name
        if not actuator.get("name"):
            self.errors.append(ParseError(
                message="Actuator declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate type
        if not actuator.get("actuator_type"):
            self.errors.append(ParseError(
                message="Actuator declaration must have a type",
                line=0,
                column=0
            ))
    
    def _validate_state(self, state: Dict[str, Any]) -> None:
        """Validate a state declaration."""
        # Validate name
        if not state.get("name"):
            self.errors.append(ParseError(
                message="State declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate transitions
        for transition in state.get("transitions", []):
            self._validate_transition(transition)
    
    def _validate_transition(self, transition: Dict[str, Any]) -> None:
        """Validate a state transition."""
        # Validate target
        if not transition.get("target"):
            self.errors.append(ParseError(
                message="Transition must have a target state",
                line=0,
                column=0
            ))
    
    def _validate_swarm_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate a swarm declaration."""
        # Validate name
        if not declaration.get("name"):
            self.errors.append(ParseError(
                message="Swarm declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate twin references
        for twin_ref in declaration.get("twins", []):
            self._validate_twin_reference(twin_ref)
        
        # Validate rule references
        for rule_ref in declaration.get("rules", []):
            self._validate_rule_reference(rule_ref)
    
    def _validate_twin_reference(self, twin_ref: Dict[str, Any]) -> None:
        """Validate a twin reference."""
        # Validate twin name
        if not twin_ref.get("twin_name"):
            self.errors.append(ParseError(
                message="Twin reference must have a twin name",
                line=0,
                column=0
            ))
    
    def _validate_rule_reference(self, rule_ref: Dict[str, Any]) -> None:
        """Validate a rule reference."""
        # Validate rule name
        if not rule_ref.get("rule_name"):
            self.errors.append(ParseError(
                message="Rule reference must have a rule name",
                line=0,
                column=0
            ))
    
    def _validate_event_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate an event declaration."""
        # Validate name
        if not declaration.get("name"):
            self.errors.append(ParseError(
                message="Event declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate parameters
        for param in declaration.get("parameters", []):
            self._validate_parameter(param)
    
    def _validate_action_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate an action declaration."""
        # Validate name
        if not declaration.get("name"):
            self.errors.append(ParseError(
                message="Action declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate parameters
        for param in declaration.get("parameters", []):
            self._validate_parameter(param)
        
        # Validate body
        for statement in declaration.get("body", []):
            self._validate_statement(statement)
    
    def _validate_parameter(self, param: Dict[str, Any]) -> None:
        """Validate a parameter."""
        # Validate name
        if not param.get("name"):
            self.errors.append(ParseError(
                message="Parameter must have a name",
                line=0,
                column=0
            ))
        
        # Validate type
        if not param.get("parameter_type"):
            self.errors.append(ParseError(
                message="Parameter must have a type",
                line=0,
                column=0
            ))
    
    def _validate_statement(self, statement: Dict[str, Any]) -> None:
        """Validate a statement."""
        statement_type = statement.get("type")
        
        if statement_type == "if_statement":
            self._validate_if_statement(statement)
        elif statement_type == "for_statement":
            self._validate_for_statement(statement)
        elif statement_type == "log_statement":
            self._validate_log_statement(statement)
        elif statement_type == "alert_statement":
            self._validate_alert_statement(statement)
        elif statement_type == "notify_statement":
            self._validate_notify_statement(statement)
        elif statement_type == "assignment":
            self._validate_assignment(statement)
        elif statement_type == "function_call":
            self._validate_function_call(statement)
        else:
            self.errors.append(ParseError(
                message=f"Unknown statement type: {statement_type}",
                line=0,
                column=0
            ))
    
    def _validate_if_statement(self, statement: Dict[str, Any]) -> None:
        """Validate an if statement."""
        # Validate condition
        if "condition" not in statement:
            self.errors.append(ParseError(
                message="If statement must have a condition",
                line=0,
                column=0
            ))
        
        # Validate then branch
        for stmt in statement.get("then_branch", []):
            self._validate_statement(stmt)
        
        # Validate else branch
        for stmt in statement.get("else_branch", []):
            self._validate_statement(stmt)
    
    def _validate_for_statement(self, statement: Dict[str, Any]) -> None:
        """Validate a for statement."""
        # Validate variable
        if not statement.get("variable"):
            self.errors.append(ParseError(
                message="For statement must have a variable",
                line=0,
                column=0
            ))
        
        # Validate iterable
        if "iterable" not in statement:
            self.errors.append(ParseError(
                message="For statement must have an iterable",
                line=0,
                column=0
            ))
        
        # Validate body
        for stmt in statement.get("body", []):
            self._validate_statement(stmt)
    
    def _validate_log_statement(self, statement: Dict[str, Any]) -> None:
        """Validate a log statement."""
        # Validate message
        if "message" not in statement:
            self.errors.append(ParseError(
                message="Log statement must have a message",
                line=0,
                column=0
            ))
    
    def _validate_alert_statement(self, statement: Dict[str, Any]) -> None:
        """Validate an alert statement."""
        # Validate message
        if "message" not in statement:
            self.errors.append(ParseError(
                message="Alert statement must have a message",
                line=0,
                column=0
            ))
    
    def _validate_notify_statement(self, statement: Dict[str, Any]) -> None:
        """Validate a notify statement."""
        # Validate target
        if "target" not in statement:
            self.errors.append(ParseError(
                message="Notify statement must have a target",
                line=0,
                column=0
            ))
        
        # Validate message
        if "message" not in statement:
            self.errors.append(ParseError(
                message="Notify statement must have a message",
                line=0,
                column=0
            ))
    
    def _validate_assignment(self, statement: Dict[str, Any]) -> None:
        """Validate an assignment."""
        # Validate name
        if not statement.get("name"):
            self.errors.append(ParseError(
                message="Assignment must have a name",
                line=0,
                column=0
            ))
        
        # Validate value
        if "value" not in statement:
            self.errors.append(ParseError(
                message="Assignment must have a value",
                line=0,
                column=0
            ))
    
    def _validate_function_call(self, statement: Dict[str, Any]) -> None:
        """Validate a function call."""
        # Validate name
        if not statement.get("name"):
            self.errors.append(ParseError(
                message="Function call must have a name",
                line=0,
                column=0
            ))
    
    def _validate_rule_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate a rule declaration."""
        # Validate name
        if not declaration.get("name"):
            self.errors.append(ParseError(
                message="Rule declaration must have a name",
                line=0,
                column=0
            ))
        
        # Validate condition
        if "condition" not in declaration:
            self.errors.append(ParseError(
                message="Rule declaration must have a condition",
                line=0,
                column=0
            ))
        
        # Validate actions
        for action in declaration.get("actions", []):
            self._validate_statement(action)
    
    def _validate_import_declaration(self, declaration: Dict[str, Any]) -> None:
        """Validate an import declaration."""
        # Validate what
        if not declaration.get("what"):
            self.errors.append(ParseError(
                message="Import declaration must specify what to import",
                line=0,
                column=0
            ))


class DTSLParser:
    """
    Main class for parsing Digital Twin Swarm Language.
    """
    
    def __init__(self):
        self.parser = DTSLParser()
        self.validator = DTSLValidator()
    
    def parse(self, source: str) -> Tuple[Dict[str, Any], List[ParseError]]:
        """Parse DTSL source code."""
        # Parse the source
        ast, parse_errors = self.parser.parse(source)
        
        # If there are parse errors, return them
        if parse_errors:
            return ast, parse_errors
        
        # Validate the AST
        validation_errors = self.validator.validate(ast)
        
        return ast, validation_errors + parse_errors
    
    def parse_file(self, file_path: str) -> Tuple[Dict[str, Any], List[ParseError]]:
        """Parse DTSL from a file."""
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            return self.parse(source)
        except Exception as e:
            return {}, [ParseError(
                message=f"Error reading file: {str(e)}",
                line=0,
                column=0
            )]
"""
