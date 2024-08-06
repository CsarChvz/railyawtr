import os
import openai
from dotenv import load_dotenv


load_dotenv()

# Crear el cliente de la API utilizando la clave de la API desde las variables de entorno
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_question(prompt: str, user_input: str, lang: str = 'en'):
    try:
        completion = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': f'{prompt} . Do not include the answer in the question. Generate in '{lang}' lang'},
                {'role': 'user', 'content': user_input},
            ],
            max_tokens=50
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f'Error generando la pregunta: {str(e)}'

def generate_response_options(question, num_options=3):
    try:
        completion = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    'role': 'system',
                    'content': 'Generate 3 multiple choice responses as in an exam. They must be two incorrect and one correct, with random order. Mark the correct with '--T--', this at the end of the answer. Example: [Option of response]... (--T--). Format properly for Parseo on the list. Generate in 'en' lang'
                },
                {'role': 'user', 'content': question},
            ],
            max_tokens=200,  # Aumentar si es necesario para permitir respuestas más detalladas
            temperature=0.7  # Ajustar para controlar la creatividad de las respuestas
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f'Error generando las opciones de respuesta: {str(e)}'


def check_response_option(question: str, response:str, lang:str = 'en'):

    try:
        completion = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    'role': 'system',
                    'content':f'Evaluate as if it was an exam, if the question: '{question}' has the correct answer. If it is correct, return 'True', otherwise return 'False'. Generate the response in '{lang}'.'
                },
                {'role': 'user', 'content': response},
            ],
            max_tokens=500,  # Aumentar si es necesario para permitir respuestas más detalladas
        )

        if(completion.choices[0].message.content == 'True'):
            return True
        else:
            return False
    except Exception as e:
        return f'Error generando las opciones de respuesta: {str(e)}'


def generate_embeddings(text):

        response = client.embeddings.create(
            input=text,
            model='text-embedding-ada-002'
        )
        return response.data[0].embedding

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()


def generate_questions(topic):
    model = ChatOpenAI(model='gpt-4', api_key=os.getenv('OPENAI_API_KEY'))

    template = '''
    You are a helpful system that provides 10 questions on the following topic: {topic}
    
    For each question:
    1. Ensure it is different from the others
    2. Include a difficulty label (easy, medium, hard) next to the question
    3. Provide possible responses as A), B), C)
    4. Mark the correct option with a (*)
    
    Please format your response as follows:

    1. [Difficulty] Question
       A) Option A
       B) Option B
       C) Option C (*)

    2. [Difficulty] Question
       ...

    Continue this format for all 10 questions.
    '''

    prompt = ChatPromptTemplate.from_template(template)
    
    messages = prompt.format_messages(topic=topic)
    
    parser = StrOutputParser()

    result = model.invoke(messages)
    return parser.invoke(result)

# Ejemplo de uso
# questions = generate_questions('Historia de España')
# print(questions)