from fastapi import FastAPI, HTTPException
from typing import List
import os
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, SummaryIndex
from llama_index.core import Settings
from typing import Optional, List, Mapping, Any
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from zhipuLLM import ZhipuLLM, metaInfo



app = FastAPI()
now_model = metaInfo()


#######################################################################################################
    
# init zhipu
api_key = 'c4c4e674dc0188c72905331159284fXXX'

Settings.llm = ZhipuLLM(api_key)

# define embed model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

#######################################################################################################


@app.post("/creat-engine")
def create_engine(file_list: List):
    documents = ["data/"+name for name in file_list]
    index = VectorStoreIndex.from_documents(documents)
    memory = ChatMemoryBuffer.from_defaults(token_limit=3900)

    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context",
        memory=memory,
        llm=Settings.llm,
        context_prompt=(
            "You are a chatbot, able to have normal interactions, as well as talk"
            " about an essay discussing Paul Grahams life."
            "Here are the relevant documents for the context:\n"
            "{context_str}"
            "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
        ),
        verbose=False,
    )

    now_model.chat_engine = chat_engine



class DialogueInput(BaseModel):
    message: str

@app.post("/dialogue/")
def dialogue(dialogue_input: DialogueInput):
    # 这里，应该调用你的LLM模型来处理对话

    if now_model.chat_engine is None:
        response = "还没有载入index, 请先选择index"
    else:
        response = handle_dialogue(dialogue_input.message) 
    return {"response": response}

from time import sleep

def handle_dialogue(message: str) -> str:
    # 模拟LLM模型回复
    # 在这里，你应该集成你的LLM模型
    sleep(0.5)
    response_text = now_model.chat_engine.chat(message).response
    return f"{response_text}"



@app.get("/files")
def list_files():
    try:
        files = os.listdir('data')  # 确保你的目录正确，这里假设有个名为data的目录
        return {"files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data directory not found.")

@app.post("/process-files/")
def process_files(selected_files: List[str]):
    # 在这里添加处理选中文件的逻辑
    # 例如，打印选中的文件名
    # print(selected_files)

    now_model.file_list = selected_files
    print(selected_files)

    if selected_files:

        file_loc = ["data/"+name for name in now_model.file_list]
        documents = SimpleDirectoryReader(input_files=file_loc).load_data()
        index = VectorStoreIndex.from_documents(documents)
        memory = ChatMemoryBuffer.from_defaults(token_limit=3900)

        chat_engine = index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=memory,
            llm=Settings.llm,
            context_prompt=(
                "You are a chatbot, able to have normal interactions, as well as talk"
                " about an essay discussing Paul Grahams life."
                "Here are the relevant documents for the context:\n"
                "{context_str}"
                "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
            ),
            verbose=False,
        )

        now_model.chat_engine = chat_engine

    return {"processed_files": selected_files}



app.mount("/", StaticFiles(directory="./", html=True), name="static")

