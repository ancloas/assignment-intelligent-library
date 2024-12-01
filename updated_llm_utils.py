from langchain.llms import BaseLLM
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from typing import Union, List, Dict

load_dotenv()  # Ensure your API keys are loaded from environment variables

class CustomHuggingFaceLLM(BaseLLM):
    """
    Custom LLM that interfaces with Hugging Face Inference API asynchronously.
    Inherits from Langchain's BaseLLM class.
    """
    def __init__(self, model_name: str, api_key_env_var: str = "HUGGINGFACE_API_KEY"):
        """
        Initializes the model with the HuggingFace API key and model name.
        """
        super().__init__()  # This is necessary for Pydantic model initialization        
        self.model_name = model_name
        self.api_key = os.getenv(api_key_env_var)
        if not self.api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env_var}")
        self.client = InferenceClient(api_key=self.api_key)

    async def _generate(self, prompt: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """
        Generates a response using Hugging Face's InferenceClient.
        """
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list) and all(isinstance(msg, dict) for msg in prompt):
            messages = prompt
        else:
            raise ValueError("Prompt must be a string or a list of message dictionaries.")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get('temperature', 0.5),
                max_tokens=kwargs.get('max_tokens', 2048),
                top_p=kwargs.get('top_p', 0.9)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error while generating response: {e}")

    def _llm_type(self):
        return 'custom'
# Testing the custom LLM in Langchain
async def test_custom_llm():
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    hf_model = CustomHuggingFaceLLM(model_name=model_name)

    string_prompt = "List five fruits."
    try:
        response = await hf_model.agenerate(string_prompt)
        print("Response from string prompt:", response)
    except Exception as e:
        print("Error:", e)


# Run the test
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_custom_llm())
