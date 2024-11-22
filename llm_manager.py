from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
from typing import Union, List, Dict

# Load environment variables
load_dotenv()

class HuggingFaceModel:
    """
    Utility class to interact with Hugging Face Inference API.
    """
    def __init__(self, model_name: str, api_key_env_var: str = "Huggingface_api_key"):
        """
        Initialize the Hugging Face model utility.
        Args:
            model_name (str): Name of the Hugging Face model to use.
            api_key_env_var (str): Environment variable containing the API key.
        """
        self.model_name = model_name
        self.api_key = os.getenv(api_key_env_var)
        if not self.api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env_var}")
        self.client = InferenceClient(api_key=self.api_key)

    def generate_response(
        self, 
        prompt: Union[str, List[Dict[str, str]]], 
        temperature: float = 0.5, 
        max_tokens: int = 2048, 
        top_p: float = 0.9
    ) -> str:
        """
        Generate a response from the Hugging Face model.
        Args:
            prompt (Union[str, List[Dict[str, str]]]): Input prompt as a string or a message list.
                - String: A simple query, e.g., "What is AI?"
                - Message list: List of dictionaries with roles and content, e.g.,
                  [{"role": "user", "content": "Tell me about AI."}]
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the output.
            top_p (float): Top-p (nucleus) sampling parameter.
        Returns:
            str: Model's response.
        """
        if isinstance(prompt, str):
            # Convert string prompt to message format
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list) and all(isinstance(msg, dict) for msg in prompt):
            # Ensure the message format is correct
            messages = prompt
        else:
            raise ValueError("Prompt must be a string or a list of message dictionaries.")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error while generating response: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize the model utility
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    hf_model = HuggingFaceModel(model_name=model_name)

    # Example 1: Using a string prompt
    string_prompt = "List five fruits."
    try:
        response = hf_model.generate_response(string_prompt)
        print("Response from string prompt:", response)
    except RuntimeError as e:
        print(e)

    # Example 2: Using a message-format prompt
    message_prompt = [
        {"role": "system", "content": "You are an assistant that lists fruits."},
        {"role": "user", "content": "Can you name five fruits for me?"}
    ]
    try:
        response = hf_model.generate_response(message_prompt)
        print("Response from message prompt:", response)
    except RuntimeError as e:
        print(e)
