import ast
import json
import operator
import os
import sys
from collections.abc import Callable
from typing import cast

import openai
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

MAX_MODEL_CALLS = 6
BINARY: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate arithmetic with + - * / and parentheses.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    }
]


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return cast(float, node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_evaluate(node.operand)
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY:
        return BINARY[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    raise ValueError("unsupported expression")


def calculate(expression: str) -> str:
    try:
        value = _evaluate(ast.parse(expression.strip(), mode="eval").body)
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
        return f"error: {exc}"
    return str(int(value)) if value == int(value) else str(value)


def run_tool_call(call) -> str:
    log(f"tool call: {call.function.name} {call.function.arguments}")
    try:
        expression = json.loads(call.function.arguments)["expression"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return "error: arguments must be JSON with an expression string"
    return calculate(str(expression))


def main() -> None:
    client = openai.OpenAI()
    model = os.environ.get("BRIER_MODEL", "gpt-5")
    messages: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": os.environ["BRIER_INSTRUCTION"]}
    ]
    answer = ""
    for step in range(MAX_MODEL_CALLS):
        log(f"model call {step + 1}")
        message = (
            client.chat.completions.create(model=model, messages=messages, tools=TOOLS)
            .choices[0]
            .message
        )
        answer = message.content or answer
        if not message.tool_calls:
            break
        messages.append(
            cast(ChatCompletionMessageParam, message.model_dump(exclude_none=True))
        )
        for call in message.tool_calls:
            result = run_tool_call(call)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": result}
            )
    print(answer.strip())


if __name__ == "__main__":
    main()
