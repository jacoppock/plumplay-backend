import logging
import sys

from base import settings
from llama_index.core import Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

client = settings.ASYNC_AZURE_GPT_CLIENT

llm = AzureOpenAI(
    model=settings.AZURE_OPENAI_MODEL_NAME,
    deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_API_BASE,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)

embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name=settings.AZURE_OPENAI_EMBEDDING_MODEL_NAME,
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_API_BASE,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)

Settings.llm = llm
Settings.embed_model = embed_model
