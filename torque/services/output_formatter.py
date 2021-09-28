import json
import sys
from typing import Any

import tabulate
from colorama import Style

from torque.parsers.global_input_parser import GlobalInputParser


class OutputFormatter:
    def __init__(self, global_input_parser: GlobalInputParser):
        self.global_input_parser = global_input_parser

    def styled_text(self, style, message, newline):
        if not self.global_input_parser.output_json:
            if message:
                sys.stdout.write(style + message)
                sys.stdout.write(Style.RESET_ALL)
            if newline:
                sys.stdout.write("\n")

    def yield_output(self, success: bool, output: Any):
        if not output:
            return

        output_str = self.format_output(output)

        if success:
            sys.stdout.write(output_str)
            sys.stdout.write("\n")
        else:
            sys.stderr.write(output_str)
            sys.stderr.write("\n")

    def format_output(self, output: Any) -> str:
        if isinstance(output, str):
            return output
        elif isinstance(output, list):
            return self.format_list(output)
        else:
            return self.format_object(output)

    def format_list(self, output: list):
        if self.global_input_parser.output_json:
            return self.format_json_list(output)
        else:
            return self.format_table(output)

    def format_object(self, output):
        if self.global_input_parser.output_json:
            return self.format_json_object(output)
        else:
            return self.format_object_default(output)

    def format_json_list(self, output: list) -> str:
        return json.dumps(output, default=lambda x: x.json_serialize(), indent=True)

    def format_json_object(self, output: Any) -> str:
        return json.dumps(output, default=lambda x: x.json_serialize(), indent=True)

    def format_table(self, output: list) -> str:
        result_table = []
        for line in output:
            result_table.append(line.json_serialize() if callable(getattr(line, "json_serialize", None)) else line)
            # TODO: json_serialize must be replaced

        return tabulate.tabulate(result_table, headers="keys")

    def format_object_default(self, output: Any) -> str:
        pass
