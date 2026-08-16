from ..LLMInterface import LLMInterface
from ..LLMEnum import CohereEnum, DocumentTypeEnum

import cohere
import logging


class CohereProvider(LLMInterface):

    def __init__(self, api_key: str,
                 default_input_max_characters: int=1000, 
                 default_generation_max_output_tokens: int=1000, 
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens= default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.genertion_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.ClientV2(api_key=self.api_key)

        self.logger = logging.getLogger(__name__)



    def set_generation_model(self, model_id: str):
        self.genertion_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history:list=[], 
                      max_output_tokens: int=None, temperature: float=None):
        if not self.client:
            self.logger.error('Cohere Client was not set')
            return None

        if not self.genertion_model_id:
            self.logger.error('Cohere generation model id was not set')
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(prompt=prompt, role=CohereEnum.USER.value)
        )

        response = self.client.chat(
            model=self.genertion_model_id,
            messages=chat_history,
            temperature=temperature,
            max_tokens= max_output_tokens
        )

        # res.message.content[0].text

        if not response or not response.message or not response.message.content or len(response.message.content) == 0:
            self.logger.error("Error while generation text using Cohere")
            return None

        return response.message.content[0].text

        
    def embed_text(self, text: str, document_type: str):
        if not self.client:
            self.logger.error("Cohere Client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Cohere Embedding model_id was not set")
            return None


        input_type = CohereEnum.DOCUMENT.value

        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CohereEnum.QUERY.value


        response = self.client.embed(
            texts=text if isinstance(text, list) else [text],
            model = self.embedding_model_id,
            input_type=input_type,
            embedding_types=['float'],
            output_dimension=self.embedding_size
        )

        # res.embeddings.float

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while creating Embedding using Cohere")
            return None

        return response.embeddings.float

        

    def construct_prompt(self, prompt: str, role: str):
        return {
            'role': role,
            'content': self.process_text(prompt)

        }


