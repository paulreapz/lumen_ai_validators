
from dotenv import load_dotenv
import textwrap
import base64
import pickle
from io import BytesIO
from PIL import Image

from e2b_code_interpreter import Sandbox
from typing import List, Tuple, Any
from .tool_validation import validate_tool_attributes
from .utils import instance_to_source, BASE_BUILTIN_MODULES, console
from .tools import Tool

load_dotenv()


class E2BExecutor:
    def __init__(self, additional_imports: List[str], tools: List[Tool]):
        self.custom_tools = {}
        self.sbx = Sandbox()  # "qywp2ctmu2q7jzprcf4j")
        # TODO: validate installing agents package or not
        # print("Installing agents package on remote executor...")
        # self.sbx.commands.run(
        #     "pip install git+https://github.com/astra_ai/astra_ai.git",
        #     timeout=300
        # )
        # print("Installation of agents package finished.")
        additional_imports = additional_imports + ["pickle5"]
        if len(additional_imports) > 0:
            execution = self.sbx.commands.run(
                "pip install " + " ".join(additional_imports)
            )
            if execution.error:
                raise Exception(f"Error installing dependencies: {execution.error}")
            else:
                console.print(f"Installation of {additional_imports} succeeded!")

        tool_codes = []
        for tool in tools:
            validate_tool_attributes(tool.__class__, check_imports=False)
            tool_code = instance_to_source(tool, base_cls=Tool)
            tool_code = tool_code.replace("from astra_ai.tools import Tool", "")
            tool_code += f"\n{tool.name} = {tool.__class__.__name__}()\n"
            tool_codes.append(tool_code)

        tool_definition_code = "\n".join(
            [f"import {module}" for module in BASE_BUILTIN_MODULES]
        )
        tool_definition_code += textwrap.dedent("""
        class Tool:
            def __call__(self, *args, **kwargs):
                return self.forward(*args, **kwargs)

            def forward(self, *args, **kwargs):
                pass # to be implemented in child class
        """)
        tool_definition_code += "\n\n".join(tool_codes)

        tool_definition_execution = self.run_code_raise_errors(tool_definition_code)
        console.print(tool_definition_execution.logs)

    def run_code_raise_errors(self, code: str):
        execution = self.sbx.run_code(
            code,
        )
        if execution.error:
            execution_logs = "\n".join([str(log) for log in execution.logs.stdout])
            logs = execution_logs
            logs += "Executing code yielded an error:"
            logs += execution.error.name
            logs += execution.error.value
            logs += execution.error.traceback
            raise ValueError(logs)
        return execution

    def __call__(self, code_action: str, additional_args: dict) -> Tuple[Any, Any]:
        if len(additional_args) > 0:
            # Pickle additional_args to server
            import tempfile

            with tempfile.NamedTemporaryFile() as f:
                pickle.dump(additional_args, f)
                f.flush()
                with open(f.name, "rb") as file:
                    self.sbx.files.write("/home/state.pkl", file)
            remote_unloading_code = """import pickle
import os
print("File path", os.path.getsize('/home/state.pkl'))
with open('/home/state.pkl', 'rb') as f:
    pickle_dict = pickle.load(f)
locals().update({key: value for key, value in pickle_dict.items()})
"""
            execution = self.run_code_raise_errors(remote_unloading_code)
            execution_logs = "\n".join([str(log) for log in execution.logs.stdout])
            console.print(execution_logs)

        execution = self.run_code_raise_errors(code_action)
        execution_logs = "\n".join([str(log) for log in execution.logs.stdout])
        if not execution.results:
            return None, execution_logs
        else:
            for result in execution.results:
                if result.is_main_result:
                    for attribute_name in ["jpeg", "png"]:
                        if getattr(result, attribute_name) is not None:
                            image_output = getattr(result, attribute_name)
                            decoded_bytes = base64.b64decode(
                                image_output.encode("utf-8")
                            )
                            return Image.open(BytesIO(decoded_bytes)), execution_logs
                    for attribute_name in [
                        "chart",
                        "data",
                        "html",
                        "javascript",
                        "json",
                        "latex",
                        "markdown",
                        "pdf",
                        "svg",
                        "text",
                    ]:
                        if getattr(result, attribute_name) is not None:
                            return getattr(result, attribute_name), execution_logs
            raise ValueError("No main result returned by executor!")


__all__ = ["E2BExecutor"]
