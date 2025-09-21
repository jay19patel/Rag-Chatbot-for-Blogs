
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings

from dotenv import load_dotenv
load_dotenv()
import os

mistral_api_key = os.getenv("MISTRAL_API_KEY")



llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.0,
        max_retries=2
    )



output = llm.invoke("Write a poem about a robot learning to love.")
print(output)