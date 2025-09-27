from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_mistralai import MistralAIEmbeddings
from app.config import settings



client = MongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
collection = db[settings.COLLECTION_NAME]

embeddings_model = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=settings.MISTRAL_API_KEY
)

vector_store = MongoDBAtlasVectorSearch(
    embedding=embeddings_model,
    collection=collection,
    index_name=settings.ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)