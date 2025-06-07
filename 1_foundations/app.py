from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import numpy as np


load_dotenv(override=True)

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}

def evaluate_response(question, response):
    """Evaluate the quality and relevance of the response"""
    print("\n=== Evaluation Debug ===")
    print(f"Evaluating response for question: {question}")
    evaluation_prompt = f"""
    Question: {question}
    Response: {response}
    
    Please evaluate this response on a scale of 1-10 for:
    1. Relevance to the question
    2. Professionalism
    3. Completeness
    4. Clarity
    
    Provide a brief explanation for each score.
    """
    
    client = OpenAI()
    evaluation = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": evaluation_prompt}]
    )
    print(f"Evaluation result: {evaluation.choices[0].message.content[:200]}...")  # Print first 200 chars
    return evaluation.choices[0].message.content

def get_relevant_context(question, vectorstore):
    """Retrieve relevant context from the vector store"""
    print("\n=== RAG Debug ===")
    print(f"Searching for context for question: {question}")
    docs = vectorstore.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    print(f"Found relevant context: {context[:200]}...")  # Print first 200 chars
    return context

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            }
            ,
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

evaluate_response_json = {
    "name": "evaluate_response",
    "description": "Evaluate the quality and relevance of a response to a question",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The original question"
            },
            "response": {
                "type": "string",
                "description": "The response to evaluate"
            }
        },
        "required": ["question", "response"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": evaluate_response_json}
]


class Monideep:

    def __init__(self):
        self.openai = OpenAI()
        self.name = "Monideep Chakraborti"
        
        # Load and process documents
        reader = PdfReader("me/linkedin.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
                
        with open("me/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()
            
        # Create vector store for RAG
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Combine all text sources
        all_text = f"{self.summary}\n\n{self.linkedin}"
        texts = self.text_splitter.split_text(all_text)
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.from_texts(texts, embeddings)

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            
            if tool_name == "evaluate_response":
                result = evaluate_response(**arguments)
            else:
                tool = globals().get(tool_name)
                result = tool(**arguments) if tool else {}
                
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results
    
    def system_prompt(self):
        system_prompt = f"""You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. \
After providing a response, use the evaluate_response tool to evaluate the quality of your response."""

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        print("\n=== Chat Debug ===")
        print(f"Processing new message: {message}")
        
        # Get relevant context from vector store
        relevant_context = get_relevant_context(message, self.vectorstore)
        
        # Add context to the message
        enhanced_message = f"""Context from knowledge base:
{relevant_context}

User question: {message}"""
        
        print(f"Enhanced message with context: {enhanced_message[:200]}...")  # Print first 200 chars
        
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": enhanced_message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                print(f"Tool calls requested: {[tool.function.name for tool in tool_calls]}")
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
                print(f"Final response: {response.choices[0].message.content[:200]}...")  # Print first 200 chars
                
        return response.choices[0].message.content
    

if __name__ == "__main__":
    me = Monideep()
    demo = gr.ChatInterface(
        me.chat,
        title="Chat with Monideep",
        description="Ask me about my professional experience, skills, and background.",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="blue",
            neutral_hue="slate",
            radius_size="md",
            font=["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        ),
        examples=[
            "What are your technical skills?",
            "Tell me about your work experience",
            "How can we connect?",
            "What projects have you worked on?"
        ]
    )
    
    # For local development
    # demo.launch()
    
    # For embedding in Replit
    demo.launch(share=True)
    