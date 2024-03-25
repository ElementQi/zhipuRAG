from zhipuai import ZhipuAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from typing import Optional, List, Mapping, Any
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from llama_index.core import SimpleDirectoryReader, SummaryIndex
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.memory import ChatMemoryBuffer
from zhipuai import ZhipuAI



class metaInfo():
    def __init__(self):
        self.chat_engine = None
        self.file_list = None


class ZhipuLLM(CustomLLM):
    model: str = Field(default="glm-4", description="The ZhipuAI model to use.")
    api_key: str = Field(description="API Key for ZhipuAI.")
    _client: Any = PrivateAttr()

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4",
        **kwargs: Any,
    ) -> None:
        self._client = ZhipuAI(api_key=api_key)
        super().__init__(model=model, api_key=api_key,**kwargs)
        
    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        # 假设智谱API的context_window和num_output，根据实际API调整
        return LLMMetadata(
            context_window=4096,
            num_output=1,
            model_name=self.model,
        )

    @llm_completion_callback()
    def complete(
            self, prompt: str, **kwargs: Any
        ) -> CompletionResponse:
            # 根据需要实现此方法，或提供简单的占位实现
            # 如果智谱API支持直接的文本生成，这里可以调用那个接口
        kwargs.pop('formatted', None)
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )

        # 假设响应结构为 response.choices[0].message 包含生成的文本
        generated_text = response.choices[0].message.content
        
        # 返回格式化的响应
        # print(generated_text)
        return CompletionResponse(text=generated_text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        # 该方法模拟stream_complete行为，但智谱API可能不支持流式响应
        # 这里简单地返回一个完成的响应
        yield self.complete(prompt, **kwargs)

if __name__ == '__main__':
    api_key = 'c4c4e674dc0188c72905331159284fXXX'

    # define our LLM
    Settings.llm = ZhipuLLM(api_key)

    # define embed model

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Load the data
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)

    memory = ChatMemoryBuffer.from_defaults(token_limit=4096)

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

    response = chat_engine.chat("What did Paul Graham do growing up")

    print(response)