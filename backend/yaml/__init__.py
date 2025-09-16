from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class YAMLError(Exception):
    pass


def safe_load(text: str) -> Any:
    parser = _YAMLParser(text)
    return parser.parse()


def safe_dump(data: Any) -> str:  # pragma: no cover - util no usado
    if isinstance(data, dict):
        lines: List[str] = []
        for key, value in data.items():
            dumped = safe_dump(value)
            if "\n" in dumped:
                indented = "\n".join("  " + line if line else "" for line in dumped.splitlines())
                lines.append(f"{key}:\n{indented}")
            else:
                lines.append(f"{key}: {dumped}")
        return "\n".join(lines)
    if isinstance(data, list):
        return "\n".join(f"- {safe_dump(item)}" for item in data)
    if isinstance(data, str):
        if any(ch in data for ch in [":", "-", "#", "\n"]):
            return f'"{data}"'
        return data
    if isinstance(data, bool):
        return "true" if data else "false"
    if data is None:
        return "null"
    return str(data)


@dataclass
class _Context:
    indent: int
    container: Any
    key: Optional[str] = None


class _YAMLParser:
    def __init__(self, text: str) -> None:
        self.lines = text.splitlines()
        self.index = 0
        self.length = len(self.lines)

    def parse(self) -> Any:
        root: Dict[str, Any] = {}
        stack: List[_Context] = [_Context(indent=-1, container=root)]

        while self.index < self.length:
            raw_line = self.lines[self.index]
            self.index += 1
            if not raw_line.strip() or raw_line.strip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            content = raw_line.strip()

            while stack and indent <= stack[-1].indent:
                stack.pop()
            if not stack:
                raise YAMLError(f"Indentación inválida en línea: {raw_line}")
            parent = stack[-1]

            if content.startswith("- "):
                self._handle_list_item(content[2:], indent, parent, stack)
            else:
                self._handle_mapping(content, indent, parent, stack)

        return stack[0].container

    def _handle_mapping(self, content: str, indent: int, parent: _Context, stack: List[_Context]) -> None:
        if ":" not in content:
            raise YAMLError(f"Entrada de mapeo inválida: {content}")
        key, value = content.split(":", 1)
        key = key.strip()
        value = value.strip()
        container = parent.container
        if not isinstance(container, dict):
            raise YAMLError("Se esperaba un diccionario para asignar clave")

        if value == "|":
            block_value = self._consume_block(indent)
            container[key] = block_value
            return
        if value == "":
            next_line = self._peek_non_empty()
            if next_line and next_line.strip().startswith("- "):
                new_container: Any = []
            else:
                new_container = {}
            container[key] = new_container
            stack.append(_Context(indent=indent, container=new_container, key=key))
            return

        container[key] = _parse_scalar(value)

    def _handle_list_item(self, value_text: str, indent: int, parent: _Context, stack: List[_Context]) -> None:
        container = parent.container
        if not isinstance(container, list):
            if isinstance(container, dict) and parent.key and isinstance(container[parent.key], dict):
                container[parent.key] = [container[parent.key]]
                container = container[parent.key]
            else:
                raise YAMLError("Se esperaba una lista")
        if value_text == "":
            item: Any = {}
            container.append(item)
            stack.append(_Context(indent=indent, container=item))
            return
        if ":" in value_text:
            key, rest = value_text.split(":", 1)
            key = key.strip()
            rest = rest.strip()
            item = {key: _parse_scalar(rest)} if rest else {key: {}}
            container.append(item)
            stack.append(_Context(indent=indent, container=item))
            if rest == "":
                stack.append(_Context(indent=indent + 2, container=item[key]))
            return
        container.append(_parse_scalar(value_text))

    def _consume_block(self, parent_indent: int) -> str:
        block_lines: List[str] = []
        block_indent: Optional[int] = None
        while self.index < self.length:
            raw_line = self.lines[self.index]
            peek_indent = len(raw_line) - len(raw_line.lstrip(" "))
            if raw_line.strip() == "":
                block_lines.append("")
                self.index += 1
                continue
            if peek_indent <= parent_indent:
                break
            if block_indent is None:
                block_indent = peek_indent
            block_lines.append(raw_line[block_indent:])
            self.index += 1
        while block_lines and block_lines[-1] == "":
            block_lines.pop()
        return "\n".join(block_lines)

    def _peek_non_empty(self) -> Optional[str]:
        pos = self.index
        while pos < self.length:
            line = self.lines[pos]
            if line.strip():
                return line
            pos += 1
        return None


def _parse_scalar(value: str) -> Any:
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    try:
        if value.startswith("0") and value != "0" and not value.startswith("0."):
            raise ValueError
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    if (value.startswith("\"") and value.endswith("\"")) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value
