import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session
from app.models import Question, Prompt, Option

from app.services.openai_service import generate_questions
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import create_retrieval_chain
#from langchain_chroma import Chroma
from langchain.docstore.document import Document

import os 
from dotenv import load_dotenv

load_dotenv()


HELICONE_API_KEY = os.getenv("HELICONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_kwargs={
      "extra_headers":{
        "Helicone-Auth": f"Bearer {HELICONE_API_KEY}"
      }
    },
    openai_api_base="https://oai.helicone.ai/v1",
)


def find_similar_questions(query_embedding, limit, db: Session):
    k = 5
    similarity_threshold = 0.85
    query = db.query(Question, Question.embedding.cosine_distance(query_embedding)
            .label("distance")).filter(Question.embedding.cosine_distance(query_embedding) < similarity_threshold).order_by("distance").limit(k).all()
    
    return query


def get_all_questions(db: Session):
    return db.query(Question).all()

def get_questions_by_prompt_id(prompt_id: str, db: Session):
    return db.query(Question).filter(Question.prompt_id == prompt_id).all()

def create_question(prompt_id: str, user_id: str, question_text: str, db: Session):
    new_question = Question(
        prompt_id=prompt_id,
        user_id=user_id,
        question_text=question_text,
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

def get_question_by_id(question_id: int, db: Session):
    return db.query(Question).filter(Question.id == question_id).first()

def update_question(question, question_data, db: Session):
    for key, value in question_data.items():
        if value is not None:
            setattr(question, key, value)
    db.commit()
    db.refresh(question)
    return question

def delete_question(question, db: Session):
    db.delete(question)
    db.commit()
    return question

def check_prompt_exists(prompt_id: str, db: Session):
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()

from langchain_community.vectorstores import FAISS
def generate_new_questions(prompt: str, lang: str, db: Session):
    prompt_id = db.query(Prompt).filter(Prompt.text == prompt).first().id
    # #Chroma
    # docs = load_documents(prompt_id,db)
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # splits = text_splitter.split_documents(docs)
    
    # db_rag = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    # retriever = db_rag.as_retriever()

    # # FAAIS
    documents = load_documents(prompt_id,db)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    db_rag = FAISS.from_documents(docs, embeddings)
    retriever = db_rag.as_retriever()

    system_prompts = {
        "es": ( 
            "Eres una IA especializada en crear preguntas educativas únicas y efectivas, diseñadas para facilitar el aprendizaje profundo y la retención. Tu tarea es generar preguntas originales sobre el tema dado, evitando estrictamente cualquier superposición con el contexto proporcionado. Sigue estas pautas meticulosamente para asegurar preguntas de alta calidad, ideales para el aprendizaje de repetición espaciada, similar a las tarjetas de Anki:\n\n"

            "1. **Requisitos de contenido:**\n"
            "   - No crees preguntas que puedan responderse directamente usando el contenido proporcionado en el contexto. Enfócate en probar la comprensión y aplicación del conocimiento más allá del material dado.\n"
            "   - Prioriza preguntas que exploren nuevas áreas, perspectivas o dimensiones del tema que no estén cubiertas en el contexto. Esto asegura una experiencia de aprendizaje más amplia y profunda.\n"
            "   - Asegura una variedad de tipos de preguntas y niveles de dificultad para proporcionar una comprensión integral del tema y atender a diferentes etapas de aprendizaje.\n"
            "   - Evita repetir información, frases o conceptos encontrados en el contexto. Cada pregunta debe introducir nuevas ideas o detalles que fomenten el pensamiento crítico y el recuerdo.\n"
            "   - Investiga y utiliza temas relacionados al contexto principal para formular preguntas que amplíen el conocimiento del estudiante y establezcan conexiones interdisciplinarias.\n\n"

            "2. **Tipos de preguntas:**\n"
            "   - **Factual:** Prueba el conocimiento de hechos o datos específicos y verificables no mencionados en el contexto. Estas preguntas ayudan a reforzar la memoria de detalles clave.\n"
            "   - **Conceptual:** Prueba la comprensión de teorías o ideas abstractas más allá del contexto. Estas preguntas animan a los estudiantes a pensar sobre los principios y conceptos subyacentes.\n"
            "   - **Basada en aplicaciones:** Requiere aplicar conocimientos a situaciones nuevas o hipotéticas, distintas a las del contexto. Esto ayuda a los estudiantes a transferir conocimientos a nuevas situaciones.\n"
            "   - **Analítica:** Implica desglosar información para entender relaciones y estructuras subyacentes no cubiertas en el contexto. Esto promueve una comprensión más profunda y un análisis crítico.\n"
            "   - **Comparación y contraste:** Destaca similitudes y diferencias entre conceptos o eventos no directamente comparados en el contexto. Este tipo de pregunta fomenta el pensamiento comparativo y la síntesis.\n"
            "   - **Causa y efecto:** Explora relaciones causales ausentes del contexto. Estas preguntas ayudan a los estudiantes a entender las consecuencias y conexiones entre diferentes factores.\n"
            "   - **Inferencia:** Requiere hacer inferencias basadas en la información proporcionada o conocimientos más allá del contexto. Estas preguntas prueban la capacidad de sacar conclusiones a partir de datos incompletos.\n"
            "   - **Predictiva:** Pide predecir resultados basados en datos o escenarios no cubiertos directamente en el contexto. Esto fomenta el pensamiento prospectivo y la aplicación de conocimientos.\n"
            "   - **Evaluación:** Implica juzgar la calidad, validez o relevancia de ciertos argumentos, teorías o evidencias más allá del contexto. Este tipo de pregunta desarrolla habilidades de evaluación crítica.\n"
            "   - **Síntesis:** Combina diferentes ideas o información para formar una nueva comprensión no mencionada directamente en el contexto. Esto fomenta la integración de diversos conceptos.\n"
            "   - **Resolución de problemas:** Plantea problemas que requieren soluciones prácticas o teóricas no discutidas en el contexto. Estas preguntas prueban la capacidad de aplicar conocimientos en escenarios del mundo real.\n"
            "   - **Excepción:** Identifica elementos que no pertenecen a un grupo o categoría dada, asegurándose de que no estén cubiertos por el contexto. Este tipo de pregunta prueba la comprensión de categorías y clasificaciones.\n"
            "   - **Mejor respuesta:** Aunque múltiples opciones pueden ser correctas, elige la mejor según criterios específicos no mencionados en el contexto. Esto fomenta la comprensión matizada y la toma de decisiones.\n\n"

            "3. **Formato de pregunta:**\n"
            "   Q: [Texto de pregunta claro y conciso, no relacionado con el contexto]\n"
            "   A: [Opción A - plausible, pero incorrecta]\n"
            "   B: [Opción B - plausible, pero incorrecta]\n"
            "   C: [Opción C - plausible, pero incorrecta]\n"
            "   D: [Opción D - la respuesta correcta]\n"
            "   CR: [Letra de la respuesta correcta]\n"
            "   Difficulty: [1 (Fácil), 2 (Medio), 3 (Difícil)]\n\n"

            "4. **Aseguramiento de calidad:**\n"
            "   - Asegúrate de que todas las opciones de respuesta sean plausibles y desafíen las habilidades de pensamiento crítico del estudiante. Evita distractores demasiado obvios.\n"
            "   - Evita ambigüedades y asegúrate de que solo una opción sea inequívocamente correcta. La claridad es crucial para un aprendizaje efectivo.\n"
            "   - Ajusta el nivel de dificultad para que coincida con el conocimiento y las habilidades del público objetivo, proporcionando una experiencia de aprendizaje equilibrada.\n\n"

            "5. **Verificación final:**\n"
            "   - Revisa cada pregunta para asegurarte de que no se superponga con el contenido del contexto de ninguna manera. Confirma que cada pregunta aporte una perspectiva nueva y única.\n"
            "   - Asegúrate de que cada pregunta proporcione una oportunidad de aprendizaje distinta, contribuyendo a una comprensión más profunda del tema. Prioriza preguntas que promuevan el recuerdo activo y la repetición espaciada.\n"
            "   - Verifica que las preguntas abarquen una amplia gama de subtemas y perspectivas relacionadas con el tema principal.\n\n"

            "6. **Investigación y expansión temática:**\n"
            "   - Antes de formular las preguntas, realiza una breve investigación sobre temas relacionados al contexto principal. Identifica conceptos, teorías o aplicaciones afines que puedan enriquecer el conjunto de preguntas.\n"
            "   - Utiliza esta información adicional para crear preguntas que exploren conexiones entre el tema principal y áreas relacionadas, fomentando un aprendizaje más amplio y contextualizado.\n"
            "   - Considera incluir preguntas que aborden tendencias actuales, debates contemporáneos o desarrollos recientes en el campo de estudio.\n\n"

            "Contexto:\n{context}\n\n"
            "Genera el número especificado de preguntas, asegurándote de que sean completamente originales y no se superpongan con el contexto proporcionado. Cada pregunta debe ser distinta, perspicaz y diseñada para mejorar la retención a largo plazo y la comprensión del tema, aprovechando la investigación adicional y la expansión temática para ofrecer un conjunto de preguntas más rico y diverso."
        ),
        "en": (
                "You are an AI specialized in creating unique and effective educational questions designed to facilitate deep learning and retention. Your task is to generate original questions on the given topic, strictly avoiding any overlap with the provided context. Follow these guidelines meticulously to ensure high-quality questions, ideal for spaced repetition learning, similar to Anki cards:\n\n"

                "1. **Content Requirements:**\n"
                "   - Do not create questions that can be answered directly using the content provided in the context. Focus on testing understanding and application of knowledge beyond the given material.\n"
                "   - Prioritize questions that explore new areas, perspectives, or dimensions of the topic not covered in the context. This ensures a broader and deeper learning experience.\n"
                "   - Ensure a variety of question types and difficulty levels to provide a comprehensive understanding of the topic and cater to different stages of learning.\n"
                "   - Avoid repeating information, phrases, or concepts found in the context. Each question should introduce new ideas or details that encourage critical thinking and recall.\n"
                "   - Research and use topics related to the main context to formulate questions that expand the student's knowledge and establish interdisciplinary connections.\n\n"

                "2. **Types of Questions:**\n"
                "   - **Factual:** Test knowledge of specific, verifiable facts or data not mentioned in the context. These questions help reinforce the memory of key details.\n"
                "   - **Conceptual:** Test understanding of theories or abstract ideas beyond the context. These questions encourage students to think about underlying principles and concepts.\n"
                "   - **Application-based:** Require applying knowledge to new or hypothetical situations different from those in the context. This helps students transfer knowledge to new situations.\n"
                "   - **Analytical:** Involve breaking down information to understand underlying relationships and structures not covered in the context. This promotes deeper understanding and critical analysis.\n"
                "   - **Comparison and Contrast:** Highlight similarities and differences between concepts or events not directly compared in the context. This type of question fosters comparative thinking and synthesis.\n"
                "   - **Cause and Effect:** Explore causal relationships absent from the context. These questions help students understand the consequences and connections between different factors.\n"
                "   - **Inference:** Require making inferences based on provided information or knowledge beyond the context. These questions test the ability to draw conclusions from incomplete data.\n"
                "   - **Predictive:** Ask to predict outcomes based on data or scenarios not directly covered in the context. This fosters forward-thinking and application of knowledge.\n"
                "   - **Evaluation:** Involve judging the quality, validity, or relevance of certain arguments, theories, or evidence beyond the context. This type of question develops critical evaluation skills.\n"
                "   - **Synthesis:** Combine different ideas or information to form a new understanding not directly mentioned in the context. This encourages the integration of diverse concepts.\n"
                "   - **Problem-solving:** Pose problems requiring practical or theoretical solutions not discussed in the context. These questions test the ability to apply knowledge in real-world scenarios.\n"
                "   - **Exception:** Identify elements that do not belong to a given group or category, ensuring they are not covered by the context. This type of question tests understanding of categories and classifications.\n"
                "   - **Best Answer:** Although multiple options may be correct, choose the best one according to specific criteria not mentioned in the context. This fosters nuanced understanding and decision-making.\n\n"

                "3. **Question Format:**\n"
                "   Q: [Clear and concise question text, unrelated to the context]\n"
                "   A: [Option A - plausible, but incorrect]\n"
                "   B: [Option B - plausible, but incorrect]\n"
                "   C: [Option C - plausible, but incorrect]\n"
                "   D: [Option D - the correct answer]\n"
                "   CR: [Letter of the correct answer]\n"
                "   Difficulty: [1 (Easy), 2 (Medium), 3 (Hard)]\n\n"

                "4. **Quality Assurance:**\n"
                "   - Ensure all answer options are plausible and challenge the student's critical thinking skills. Avoid overly obvious distractors.\n"
                "   - Avoid ambiguities and ensure that only one option is unequivocally correct. Clarity is crucial for effective learning.\n"
                "   - Adjust the difficulty level to match the target audience's knowledge and skills, providing a balanced learning experience.\n\n"

                "5. **Final Verification:**\n"
                "   - Review each question to ensure there is no overlap with the context in any way. Confirm that each question offers a new and unique perspective.\n"
                "   - Ensure each question provides a distinct learning opportunity, contributing to a deeper understanding of the topic. Prioritize questions that promote active recall and spaced repetition.\n"
                "   - Verify that the questions cover a broad range of subtopics and perspectives related to the main topic.\n\n"

                "6. **Research and Thematic Expansion:**\n"
                "   - Before formulating questions, conduct brief research on topics related to the main context. Identify concepts, theories, or applications that can enrich the set of questions.\n"
                "   - Use this additional information to create questions that explore connections between the main topic and related areas, fostering broader and more contextualized learning.\n"
                "   - Consider including questions that address current trends, contemporary debates, or recent developments in the field of study.\n\n"

                "Context:\n{context}\n\n"
                "Generate the specified number of questions, ensuring they are completely original and do not overlap with the provided context. Each question should be distinct, insightful, and designed to enhance long-term retention and understanding of the topic, leveraging additional research and thematic expansion to offer a richer and more diverse set of questions."
        )
    }
    system_prompt = system_prompts.get(lang, system_prompts["en"]) 

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({
    "input": (
        f"Please, generate 10 questions about this topic. "
        f"Distribute the questions evenly across difficulty levels: 1 (Easy), 2 (Medium), 3 (Hard). "
        f"The topic is: {prompt}"
    )
    })

    generated_questions = parse_questions(response["answer"])
    questions = []
    similarity_threshold = 0.15  # Ajusta este valor según necesites

    for q in generated_questions:

        # FAAIS
        ca = db_rag.similarity_search_with_score(q["question_text"])

        #Chroma
        #ca = db_rag.similarity_search_with_relevance_scores(q["question_text"])
        most_similar_score = ca[0][1] 
        print("Score-----", most_similar_score)
        if most_similar_score > similarity_threshold:
            question = Question(question_text=q["question_text"], difficulty=q["difficulty"])
            options_items = q["options"]
            for i in options_items:
                is_correct = i["is_correct"]
                text = i["text"]
                option = Option(option_text=text, is_correct_answer=is_correct)
                question.options.append(option)
            questions.append(question)
        else:
            print(f"Pregunta descartada por alta similitud (score: {most_similar_score}):")
            print(q["question_text"])
            print(q["options"])
    
    docs_total = db_rag.index.ntotal

    while docs_total >= 1:
        db_rag.delete([db_rag.index_to_docstore_id[0]])
        docs_total = db_rag.index.ntotal
        print("count after:", docs_total)


    return questions

def parse_questions(text: str) -> list[dict]:
    questions = []
    pattern = r'Q: (.*?)\nA: (.*?)\nB: (.*?)\nC: (.*?)\nD: (.*?)\nCR: (.*?)\nDifficulty: ([1-3])(?=\n\nQ:|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        question, answer_a, answer_b, answer_c, answer_d, correct_answer, difficulty = [item.strip() for item in match]
        
        # Validación de respuestas válidas
        correct_answer = correct_answer.upper()
        if correct_answer not in {'A', 'B', 'C', 'D'}:
            continue  # Ignorar si la respuesta correcta no es válida
        
        # Validación y conversión de la dificultad a entero
        try:
            difficulty = int(difficulty)
        except ValueError:
            continue  # Ignorar si la dificultad no es un número válido
        
        options = [
            {"text": answer_a, "is_correct": correct_answer == 'A'},
            {"text": answer_b, "is_correct": correct_answer == 'B'},
            {"text": answer_c, "is_correct": correct_answer == 'C'},
            {"text": answer_d, "is_correct": correct_answer == 'D'}
        ]
        
        questions.append({
            "question_text": question,
            "options": options,
            "difficulty": difficulty
        })
    
    return questions



def generate_and_save_new_questions(topic: str, prompt_id: int, lang:str, db: Session):
    # Generar nuevas preguntas
    new_questions = generate_new_questions(topic, lang, db)
    
    # Asignar el prompt_id y añadir cada pregunta a la sesión de la base de datos
    for q in new_questions:
        q.prompt_id = prompt_id
        db.add(q)
    
    # Confirmar los cambios en la base de datos
    db.commit()
    
    return new_questions

# CHROMA
# def load_documents(prompt_id: int,db: Session):
#     contents = db.query(Question).filter(Question.prompt_id == prompt_id).all()
#     if len(contents) > 0:
#         docs = [
#             Document(
#                 page_content=f"{content.question_text}",
#                 metadata={"id": content.id}
#             )
#             for content in contents
#         ]
#         return docs

#     else:
#         print("DOCUMENTOS ESTA")
#         docs = [
#             Document(
#                 page_content=f"Document 1",
#                 metadata={"id": 1}
#             ),
#                         Document(
#                 page_content=f"Document 2",
#                 metadata={"id": 2}
#             ),
#                         Document(
#                 page_content=f"Document 3",
#                 metadata={"id": 3}
#             ),
#                         Document(
#                 page_content=f"Document 4",
#                 metadata={"id": 4}
#             ),            Document(
#                 page_content=f"Document 5",
#                 metadata={"id": 5}
#             )

#         ]

#         return docs
    
# FAAIS 
def load_documents(prompt_id: int,db: Session):
    contents = db.query(Question).filter(Question.prompt_id == prompt_id).all()
    if len(contents) > 0:
        docs = [
            Document(
                page_content=f"{content.question_text}",
                metadata={"page": content.id}
            )
            for content in contents
        ]
        return docs

    else:
        print("DOCUMENTOS ESTA")
        docs = [
            Document(
                page_content=f"Document 1",
                metadata={"page": 1}
            ),
                        Document(
                page_content=f"Document 2",
                metadata={"page": 2}
            ),
                        Document(
                page_content=f"Document 3",
                metadata={"page": 3}
            ),
                        Document(
                page_content=f"Document 4",
                metadata={"page": 4}
            ),            Document(
                page_content=f"Document 5",
                metadata={"page": 5}
            )

        ]

        return docs