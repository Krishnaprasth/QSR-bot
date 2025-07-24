import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class LLMHandler:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.2)
        self.prompt = PromptTemplate(
            input_variables=["question","context"],
            template="""You are a QSR performance expert.
Given the following context from sales data:
{context}
Answer the question: {question}"""
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate_answer(self, question: str, contexts: list):
        context_text = "\n---\n".join(contexts)
        output = self.chain.run(question=question, context=context_text)
        return output.strip()
