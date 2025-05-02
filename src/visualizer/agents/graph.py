from typing import List, Literal

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph

from visualizer.state import AgentState, InputData
from visualizer.utils import create_data_summary
from visualizer.chains import model
from visualizer.tools import complete_python_task


class AgentDA:
    def __init__(self):
        super().__init__()
        self.reset_chat()
        self.graph = self.create_graph()

        self.tools = [complete_python_task]
        
    def create_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node('agent', self.call_model)
        workflow.add_node('tools', self.call_tools)

        workflow.add_conditional_edges('agent', self.route_to_tools)

        workflow.add_edge('tools', 'agent')
        workflow.set_entry_point('agent')
        return workflow.compile()
    
    def call_model(self, state: AgentState) -> dict:
        """
        
        """
        current_data_template = """The following data is available:\n{data_summary}"""
        current_data_message = HumanMessage(
            content=current_data_template.format(data_summary=create_data_summary(state))
        )
        state["messages"] = [current_data_message] + state["messages"]

        llm_response = model.invoke(state)

        return {
            "messages": [llm_response],
            "intermediate_outputs": [current_data_message.content],
        }
    
    def route_to_tools(self, state: AgentState) -> Literal["tools", "__end__"]:
        """
        
        """
        if messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages in state: {state}")
        
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "__end__"
    
    def call_tools(self, state: AgentState):
        """
        
        """
        last_message = state["messages"][-1]
        tool_messages = []
        state_updates = {}

        if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
            for tc in last_message.tool_calls:
                tool_name = tc["name"]
                tool_input = tc["args"]

                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool is None:
                    raise ValueError(f"Tool {tool_name} not found")
                
                # invoke the tool with the provided input and graph_state
                result = tool.invoke({**tool_input, "graph_state": state})
                message, updates = result
                tool_messages.append(
                    ToolMessage(
                        content=str(message),
                        name=tool_name,
                        tool_call_id=tc["id"]
                    )
                )
                state_updates.update(updates)

        state_updates["messages"] = tool_messages
        return state_updates

    def user_sent_message(self, user_query, input_data: List[InputData]):
        """

        """
        starting_image_paths_set = set(sum(self.output_image_paths.values(), []))
        input_state = {
            "messages": self.chat_history + [HumanMessage(content=user_query)],
            "output_image_paths": list(starting_image_paths_set),
            "input_data": input_data,
        }

        result = self.graph.invoke(input_state, {"recursion_limit": 25})
        self.chat_history = result["messages"]
        new_image_paths = set(result["output_image_paths"]) - starting_image_paths_set
        self.output_image_paths[len(self.chat_history) - 1] = list(new_image_paths)
        if "intermediate_outputs" in result:
            self.intermediate_outputs.extend(result["intermediate_outputs"])

    def reset_chat(self):
        self.chat_history = []
        self.intermediate_outputs = []
        self.output_image_paths = {}
