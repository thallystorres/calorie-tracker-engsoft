from pydantic import BaseModel, Field

class FlashcardSchema(BaseModel):
    frente: str = Field(description="Pergunta ou conceito")
    verso: str = Field(description="Resposta ou explicação detalhada")

class FlashcardSetResponseSchema(BaseModel):
    titulo: str
    cards: list[FlashcardSchema]

class QuizQuestionSchema(BaseModel):
    pergunta: str
    opcoes: list[str] = Field(description="Exatamente 2 opções de múltipla escolha")
    resposta_correta: str = Field(description="A opção correta exata")
    explicacao: str
  
class QuizResponseSchema(BaseModel):
    titulo: str
    questoes: list[QuizQuestionSchema]
