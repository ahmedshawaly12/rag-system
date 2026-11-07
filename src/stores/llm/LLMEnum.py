from enum import Enum


class LLMEnum(Enum):
    OPENAI = 'OPENAI'
    COHERE = 'COHERE'

class OpenAIEnum(Enum):
    USER='user'
    SYSTEM='system'
    ASSISTANT='assistant'

class CohereEnum(Enum):
    USER='user'

    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeEnum(Enum):
    DOCUMENT = 'document'
    QUERY = 'query'