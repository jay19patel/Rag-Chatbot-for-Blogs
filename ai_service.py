
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from schema import Blog
from dotenv import load_dotenv
load_dotenv()
import os
import json

mistral_api_key = os.getenv("MISTRAL_API_KEY")

parser = PydanticOutputParser(pydantic_object=Blog)

PROMPT = """
You are an expert content writer who creates simple, easy-to-understand blog posts.
Create a comprehensive yet accessible blog post based on the following topic/prompt.

Generate content that follows this exact JSON structure:
{schema}

Writing Style Requirements:
- Use SIMPLE language that anyone can understand
- Write in a conversational, friendly tone
- Explain technical concepts in plain English
- Use short sentences and paragraphs for better readability
- Include practical examples and real-world applications
- Make content engaging and relatable

Content Structure Requirements:
- Generate a SEO-friendly slug from the title (lowercase, hyphens instead of spaces)
- Write a compelling but simple title and subtitle
- Create an engaging excerpt (2-3 sentences that clearly explain what the reader will learn)
- Find and include a relevant image URL from Unsplash that relates to the topic
- The content field MUST include:
  * introduction: Write a simple, welcoming introduction (2-3 paragraphs) that explains what the topic is about and why it matters
  * sections: Include multiple easy-to-understand sections with varied types:
    - Use "text" sections for explanations with simple examples
    - Use "bullets" sections for easy-to-scan lists of key points
    - Use "code" sections only when absolutely necessary, with clear explanations
    - Each section should have a clear, descriptive title
  * conclusion: Write a practical conclusion (2-3 paragraphs) that summarizes key takeaways and gives actionable next steps
- Add relevant, popular tags that people would search for
- Set appropriate category
- Calculate realistic read time based on content length (typically 200 words per minute)
- Set views=0, likes=0

Image Guidelines:
- Use Unsplash URLs in format: https://images.unsplash.com/photo-[photo-id]?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80
- Choose images that directly relate to the topic
- Prefer images that are visually appealing and professional

CRITICAL:
1. The content field must have ALL THREE required fields: introduction, sections, AND conclusion
2. Keep language simple and avoid jargon
3. Include a relevant Unsplash image
4. Make content practical and actionable

Topic/Prompt: {text}

Return only the JSON response that matches the schema above.
"""

prompt = PromptTemplate(
    template=PROMPT,
    input_variables=["text"],
    partial_variables={"schema": parser.get_format_instructions()}
)

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.7,
    max_retries=2
)

def generate_blog(user_prompt):
    chain = prompt | llm | parser
    result = chain.invoke({"text": user_prompt})
    return result

def save_blog_to_json(blog_data, filename=None):
    if filename is None:
        filename = f"blog_{blog_data.slug}.json"

    # Use mode='json' to serialize HttpUrl and other custom types properly
    blog_dict = blog_data.model_dump(mode='json')

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(blog_dict, f, indent=2, ensure_ascii=False)

    return filename

def main():
    user_input = input("Enter your blog topic/prompt: ")

    print("Generating blog...")
    try:
        blog = generate_blog(user_input)
        print("Blog generated successfully!")
        print("\nGenerated Blog JSON:")
        print(json.dumps(blog.model_dump(mode='json'), indent=2))

        filename = save_blog_to_json(blog)
        print(f"\nBlog saved to: {filename}")

    except Exception as e:
        print(f"Error generating blog: {e}")

if __name__ == "__main__":
    main()