from smolagents import CodeAgent, HfApiModel

model_id = "meta-llama/Llama-3.3-70B-Instruct"

model = HfApiModel(model_id=model_id, token="<YOUR_HUGGINGFACEHUB_API_TOKEN>")
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

agent.run(
    "Could you give me the 118th number in the Fibonacci sequence?",
)