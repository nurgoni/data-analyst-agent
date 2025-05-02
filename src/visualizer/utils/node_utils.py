from visualizer.state import AgentState


def create_data_summary(state: AgentState) -> str:
    """
    
    """
    summary = ""
    variables = []

    for data in state["input_data"]:
        variables.append(data.variable_name)
        summary += f"\n\nVariable: {data.variable_name}"
        summary += f"Description: {data.data_description}"

        # variables.append(data["variable_name"])
        # summary += f"\n\nVariable: {data['variable_name']}"
        # summary += f"Description: {data['data_description']}"

    if "current_variables" in state:
        remaining_vars = [v for v in state["current_variables"] if v not in variables]
        for v in remaining_vars:
            summary += f"\n\Variable: {v}"
    
    return summary
