import re
from abc import ABC
from dataclasses import dataclass
from typing import Callable, Any
from collections import namedtuple

from .utils import *

# fact: chatgpt is retarded

Operator = namedtuple('Operator', ['precedence', 'assoc', 'func'])

EXPRESSION_TRUE = "true"
EXPRESSION_FALSE = "false"

OTHER_TOKENS = ["(", ")", EXPRESSION_TRUE, EXPRESSION_FALSE]

OPERATORS = {
    "!":   Operator(6, "right", lambda a: not bool(a)),
    "*":   Operator(5, "left",  lambda a, b: a * b),
    "/":   Operator(5, "left",  lambda a, b: a // b),
    "+":   Operator(4, "left",  lambda a, b: a + b),
    "-":   Operator(4, "left",  lambda a, b: a - b),
    "<":   Operator(3, "left",  lambda a, b: a < b),
    ">":   Operator(3, "left",  lambda a, b: a > b),
    "<=":  Operator(3, "left",  lambda a, b: a <= b),
    ">=":  Operator(3, "left",  lambda a, b: a >= b),
    "==":  Operator(2, "left",  lambda a, b: a == b),
    "!=":  Operator(2, "left",  lambda a, b: a != b),
    "&&":  Operator(1, "left",  lambda a, b: bool(a) and bool(b)),
    "||":  Operator(0, "left",  lambda a, b: bool(a) or bool(b)),
}

def build_token_regex():
    sorted_ops = sorted(OPERATORS.keys(), key=lambda x: -len(x))
    all_tokens = sorted_ops + OTHER_TOKENS
    escaped_tokens = [re.escape(token) for token in all_tokens]
    pattern = r'\s*(' + '|'.join(escaped_tokens) + '|' + REGEX_IDENTIFIER + r')\s*'
    return re.compile(pattern)

TOKEN_REGEX = build_token_regex()

def tokenize(expression):
    tokens = TOKEN_REGEX.findall(expression)
    return [token for token in tokens if token.strip()]

def parse(tokens):
    def parse_expression(min_prec=0):
        node = parse_primary()
        while tokens:
            tok = tokens[0]
            
            if tok not in OPERATORS or OPERATORS[tok].func is None:
                break
            operator = OPERATORS[tok]
            if operator.precedence < min_prec:
                break

            tokens.pop(0)
            next_min_prec = operator.precedence + 1 if operator.assoc == "left" else operator.precedence
            rhs = parse_expression(next_min_prec)
            node = (tok, node, rhs)
        return node

    def parse_primary():
        token = tokens.pop(0)
        if token == '(':
            expr = parse_expression()
            if not tokens or tokens.pop(0) != ')':
                raise ValueError("Expected ')'")
            return expr
        elif token == '!':
            operand = parse_expression(OPERATORS['!'].precedence)
            return ('!', operand)
        elif token == EXPRESSION_TRUE:
            return True
        elif token == EXPRESSION_FALSE:
            return False
        elif token.isdigit():
            return int(token)
        else:
            return token  # variable

    return parse_expression()

def evaluate(ast, context, valuator = None):
    if isinstance(ast, (bool, int)):
        return ast
    if isinstance(ast, str):
        if valuator:
            return valuator(ast)
        
        val = context.get(ast)
        if val is None:
            raise ValueError(f"Undefined variable: {ast}")
        return val
    
    if isinstance(ast, tuple):
        if len(ast) == 2:  # unary
            op, operand = ast
            return OPERATORS[op].func(evaluate(operand, context, valuator))
        elif len(ast) == 3:  # binary
            op, left, right = ast
            return OPERATORS[op].func(evaluate(left, context, valuator), evaluate(right, context, valuator))
    
    raise ValueError(f"Invalid AST node: {ast}")

def evaluate_expression(expr, context={}, valuator: Callable[[str], Any] = None):
    tokens = tokenize(expr)
    ast = parse(tokens)
    return evaluate(ast, context, valuator)
