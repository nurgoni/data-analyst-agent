import os
import sys
from io import StringIO
from typing import Tuple, Annotated

import pandas as pd

from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState


repl = PythonREPL()
persistent_vars = {}

# will remove
plotly_saving_code = """
import pickle
import uuid
import plotly

for figure in plotly_figures:
    pickle_filename = f"images/plotly_figures/pickle/{uuid.uuid4()}.pickle"
    with open(pickle_filename, 'wb') as f:
        pickle.dump(figure, f)
"""


@tool(parse_docstring=True)
def complete_python_task(
    graph_state: Annotated[dict, InjectedState],
    thought: str,
    python_code: str
) -> Tuple[str, dict]:
    """
    Completes a Python task by executing the provided code.

    Args:
        graph_state (dict): The state of the graph.
        thought (str): The thought process leading to this code.
        python_code (str): The Python code to execute.
    """
    current_vars = graph_state["current_variables"] if "current_variables" in graph_state else {}

    # will remove
    for input_dataset in graph_state["input_data"]:
        if input_dataset.variable_name not in current_vars:
            current_vars[input_dataset.variable_name] = pd.read_csv(input_dataset.data_path)
    if not os.path.exists("images/plotly_figures/pickle"):
        os.makedirs("images/plotly_figures/pickle")
    current_image_pickle_files = os.listdir("images/plotly_figures/pickle")

    try:
        # capture standard output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # execute the code and capture the result
        exec_globals = globals().copy()
        exec_globals.update(persistent_vars)
        exec_globals.update(current_vars)
        exec_globals.update({"plotly_figures": []})

        exec(python_code, exec_globals)
        persistent_vars.update({
            k:v for k, v in exec_globals.items() if k not in globals()
        })

        # get the captured output
        output = sys.stdout.getvalue()

        # restore stdout
        sys.stdout = old_stdout

        #update
        updated_state = {
            "intermediate_outputs": [{"thought": thought, "code": python_code, "output": output}],
            "current_variables": persistent_vars
        }

        # will remove
        if 'plotly_figures' in exec_globals:
            exec(plotly_saving_code, exec_globals)
            # Check if any images were created
            new_image_folder_contents = os.listdir("images/plotly_figures/pickle")
            new_image_files = [file for file in new_image_folder_contents if file not in current_image_pickle_files]
            if new_image_files:
                updated_state["output_image_paths"] = new_image_files
            
            persistent_vars["plotly_figures"] = []

        return output, updated_state

    except Exception as e:
        return str(e), {"intermediate_outputs": [{"thought": thought, "code": python_code, "output": str(e)}]}
