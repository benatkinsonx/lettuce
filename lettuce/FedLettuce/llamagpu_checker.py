import os
os.environ["LLAMA_CPP_LIB"] = "/home/apyba3/llama.cpp/build/bin/libllama.so"

from llama_cpp import Llama

llm = Llama(
    model_path="/mnt/LxData/llama.cpp/models/meta-llama2/llama-2-7b-chat/ggml-model-q4_0.bin",
    n_gpu_layers=28,
    n_threads=6,
    n_ctx=3584,
    n_batch=512,
    verbose=True,
)
