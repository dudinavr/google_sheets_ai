from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from openai import OpenAI
from .settings import settings


class GoogleSheetAI:
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo", temperature: float = 0.0, is_stream: bool = False):

        self.client = ChatOpenAI(
            model_name=model_name,
            max_tokens=2048,
            temperature=temperature,
            openai_api_key=api_key,
            streaming=is_stream
        )
        self.prompt_template = ChatPromptTemplate.from_template(
            "Данные таблицы:\n{table_data}\n\n"
            "Вопрос: {question}\n"
            "Ответь строго на основе таблицы. Если ответа нет — скажи 'Нет информации'. "
            "Отвечай строго в рамках данных, которые есть в таблице и по ссылка, представленнм в таблице."
            "Для поиска информации используй только ссылки, приведенные в таблице."
            "НЕ используй дополнительные источники"
        )
        self.openai_client = OpenAI(api_key=settings.OPENAI_KEY)

    async def answer_question(self, question: str, table_data: str) -> str:
        prompt = self.prompt_template.format_prompt(
            table_data=table_data,
            question=question
        )
        response = await self.client.ainvoke([HumanMessage(content=prompt.to_string())])
        return response.content.strip()

    async def stream_answer_question(self, question: str, table_data: str):
        chain = self.prompt_template | self.client

        async for chunk in chain.astream({"table_data": table_data, "question": question}):
            if chunk.content:
                yield chunk.content

