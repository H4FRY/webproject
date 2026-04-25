from llama_cpp import Llama

llm = Llama(
    model_path="models/model.gguf",
    n_ctx=4096,
    n_threads=8,
    verbose=False,
)