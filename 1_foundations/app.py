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
import time
from datetime import datetime


# Load environment variables
load_dotenv(override=True)

# Check if required environment variables are set
def check_env_vars():
    required_vars = ['OPENAI_API_KEY']  # Only OpenAI API key is required
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {missing_vars}")
        print("Please set these in your .env file or HuggingFace secrets")
        return False
    return True

def push(text):
    # Only push if credentials are available
    if not (os.getenv("PUSHOVER_TOKEN") and os.getenv("PUSHOVER_USER")):
        print(f"Push notification (credentials not available): {text}")
        return
    
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_TOKEN"),
                "user": os.getenv("PUSHOVER_USER"),
                "message": text,
            }
        )
    except Exception as e:
        print(f"Failed to send push notification: {e}")


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"🎉 New connection! {name} ({email}) - {notes}")
    return {"recorded": "ok", "message": "Thanks for connecting! I'll be in touch soon."}

def record_unknown_question(question):
    push(f"🤔 Interesting question I couldn't answer: {question}")
    return {"recorded": "ok", "message": "That's a great question! I'll research this and get back to you."}

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

def create_welcome_message():
    """Create a personalized welcome message"""
    return """👋 **Welcome! I'm Monideep Chakraborti**

I'm a Product Manager passionate about building intelligent technology that makes search, communication, and learning more accessible and inclusive.

**What I do:**
• 🏥 Lead biomedical search modernization at NCBI/NIH (6M+ daily users)
• 🎯 Build AI-powered speech accessibility tools
• 🧠 Design GenAI applications for learning and decision-making
• 💡 Bridge product strategy with technical execution

**Ask me about:**
• My work at NIH and biomedical search
• Speech accessibility and ASR systems
• Product management in AI/ML
• GenAI applications and prompt engineering
• My side projects and research interests

Let's connect and explore how we can build something amazing together! 🚀"""

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
        
        # Load and process documents with error handling
        try:
            reader = PdfReader("me/linkedin.pdf")
            self.linkedin = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    self.linkedin += text
            print("✅ LinkedIn PDF loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load LinkedIn PDF: {e}")
            self.linkedin = "Experienced Product Manager with expertise in AI/ML, biomedical search, and speech accessibility."
                
        try:
            with open("me/summary.txt", "r", encoding="utf-8") as f:
                self.summary = f.read()
            print("✅ Summary file loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load summary file: {e}")
            self.summary = "I'm a Product Manager focused on building technology that makes search, communication, and learning more intelligent and inclusive."
            
        # Create vector store for RAG (only if API key is available)
        self.vectorstore = None
        if os.getenv("OPENAI_API_KEY"):
            try:
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
                print("✅ Vector store created successfully")
            except Exception as e:
                print(f"⚠️ Failed to create vector store: {e}")
                print("Continuing without RAG functionality")
        else:
            print("⚠️ OpenAI API key not found. Continuing without RAG functionality")

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
        
        # Get relevant context from vector store (if available)
        if self.vectorstore:
            relevant_context = get_relevant_context(message, self.vectorstore)
            enhanced_message = f"""Context from knowledge base:
{relevant_context}

User question: {message}"""
        else:
            # Fallback without RAG
            enhanced_message = message
            print("Using fallback mode without RAG")
        
        print(f"Enhanced message with context: {enhanced_message[:200]}...")  # Print first 200 chars
        
        # Convert history to the format expected by OpenAI
        messages = [{"role": "system", "content": self.system_prompt()}]
        
        # Add conversation history
        for msg in history:
            if isinstance(msg, list) and len(msg) == 2:
                # Old format: [user_msg, assistant_msg]
                if msg[0]:  # User message
                    messages.append({"role": "user", "content": msg[0]})
                if msg[1]:  # Assistant message
                    messages.append({"role": "assistant", "content": msg[1]})
            elif isinstance(msg, dict):
                # New format: {"role": "user", "content": "..."}
                messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": enhanced_message})
        
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
    

def create_custom_theme():
    """Create a custom theme for the app"""
    return gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="teal",
        neutral_hue="slate",
        radius_size="lg",
        font=["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        font_mono=["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
    )

def create_header():
    """Create a custom header component"""
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1 style="color: #1e40af; margin: 0; font-size: 2.5em; font-weight: 700;">
                    🚀 Monideep Chakraborti
                </h1>
                <p style="color: #64748b; margin: 10px 0; font-size: 1.2em;">
                    Product Manager | AI Enthusiast | Biomedical Search Innovator
                </p>
                <div style="display: flex; justify-content: center; gap: 20px; margin-top: 15px;">
                    <span style="background: #dbeafe; color: #1e40af; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(30, 64, 175, 0.1);">
                        🏥 NIH/NCBI
                    </span>
                    <span style="background: #ecfdf5; color: #059669; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(5, 150, 105, 0.1);">
                        🤖 AI/ML
                    </span>
                    <span style="background: #fef3c7; color: #d97706; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(217, 119, 6, 0.1);">
                        🎯 Product
                    </span>
                </div>
            </div>
            """)

def create_footer():
    """Create a custom footer component"""
    return gr.HTML("""
    <div style="text-align: center; padding: 20px; color: #64748b; font-size: 0.9em;">
        <p>💡 Built with Gradio & OpenAI | 🔗 Let's connect and build something amazing!</p>
        <p>📧 <a href="mailto:monideep@example.com" style="color: #1e40af;">monideep@example.com</a> | 
        💼 <a href="https://linkedin.com/in/monideep" style="color: #1e40af;">LinkedIn</a></p>
    </div>
    """)

def get_css(is_dark=False):
    """Get CSS based on dark/light mode"""
    if is_dark:
        return """
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
            background: #1a1a1a !important;
            color: #ffffff !important;
        }
        .chat-message {
            border-radius: 15px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        .user-message {
            background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
            color: white !important;
            border: 1px solid #3b82f6 !important;
        }
        .assistant-message {
            background: linear-gradient(135deg, #2d3748, #4a5568) !important;
            border: 1px solid #4a5568 !important;
            color: #e2e8f0 !important;
        }
        .card {
            background: #2d3748 !important;
            border: 1px solid #4a5568 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        .quick-btn {
            background: #4a5568 !important;
            color: #e2e8f0 !important;
            border: 1px solid #718096 !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            margin: 5px !important;
            transition: all 0.3s ease !important;
        }
        .quick-btn:hover {
            background: #2d3748 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
        }
        .header-dark {
            background: linear-gradient(135deg, #1a202c, #2d3748) !important;
            border-radius: 12px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        .welcome-card {
            background: linear-gradient(135deg, #2d3748, #4a5568) !important;
            border: 1px solid #4a5568 !important;
            border-radius: 12px !important;
            padding: 25px !important;
            margin: 15px 0 !important;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4) !important;
        }
        """
    else:
        return """
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
            background: #ffffff !important;
        }
        .chat-message {
            border-radius: 15px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        .user-message {
            background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
            color: white !important;
            border: 1px solid #3b82f6 !important;
        }
        .assistant-message {
            background: linear-gradient(135deg, #f8fafc, #e2e8f0) !important;
            border: 1px solid #e2e8f0 !important;
            color: #1a202c !important;
        }
        .card {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        .quick-btn {
            background: #f8fafc !important;
            color: #1a202c !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            margin: 5px !important;
            transition: all 0.3s ease !important;
        }
        .quick-btn:hover {
            background: #e2e8f0 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        }
        .header-light {
            background: linear-gradient(135deg, #f8fafc, #e2e8f0) !important;
            border-radius: 12px !important;
            margin: 10px 0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        .welcome-card {
            background: linear-gradient(135deg, #ffffff, #f8fafc) !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 25px !important;
            margin: 15px 0 !important;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1) !important;
        }
        """

def toggle_theme(is_dark):
    """Toggle between dark and light themes"""
    return get_css(is_dark)

if __name__ == "__main__":
    # Check environment variables
    check_env_vars()
    
    try:
        me = Monideep()
        print("✅ Monideep class initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Monideep: {e}")
        # Create a fallback version
        class FallbackMonideep:
            def __init__(self):
                self.name = "Monideep Chakraborti"
                self.summary = "Product Manager focused on building technology that makes search, communication, and learning more intelligent and inclusive."
                self.linkedin = "Experienced Product Manager with expertise in AI/ML, biomedical search, and speech accessibility."
                self.vectorstore = None
                self.openai = OpenAI()
            
            def chat(self, message, history):
                try:
                    # Simple fallback response
                    return f"Hi! I'm {self.name}. I'm a Product Manager passionate about AI and technology. I'm currently experiencing some technical difficulties, but I'd love to connect! Please reach out to me directly."
                except Exception as e:
                    return f"Thanks for your message! I'm currently experiencing some technical difficulties. Please reach out to me directly at monideep@example.com"
            
            def system_prompt(self):
                return f"You are {self.name}, a Product Manager. Be professional and engaging."
        
        me = FallbackMonideep()
        print("⚠️ Using fallback mode due to initialization error")
    
    # Create the custom theme
    theme = create_custom_theme()
    
    # Create the interface
    with gr.Blocks(theme=theme, title="Monideep Chakraborti - AI Career Chat") as demo:
        
        # Theme toggle
        with gr.Row():
            with gr.Column(scale=1):
                theme_toggle = gr.Checkbox(
                    label="🌙 Dark Mode", 
                    value=False,
                    container=False,
                    scale=0
                )
        
        # CSS state
        css_state = gr.State(get_css(False))
        
        # Header
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="header-light" id="header">
                    <div style="text-align: center; padding: 20px;">
                        <h1 style="color: #1e40af; margin: 0; font-size: 2.5em; font-weight: 700;">
                            🚀 Monideep Chakraborti
                        </h1>
                        <p style="color: #64748b; margin: 10px 0; font-size: 1.2em;">
                            Product Manager | AI Enthusiast | Biomedical Search Innovator
                        </p>
                        <div style="display: flex; justify-content: center; gap: 20px; margin-top: 15px;">
                            <span style="background: #dbeafe; color: #1e40af; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(30, 64, 175, 0.1);">
                                🏥 NIH/NCBI
                            </span>
                            <span style="background: #ecfdf5; color: #059669; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(5, 150, 105, 0.1);">
                                🤖 AI/ML
                            </span>
                            <span style="background: #fef3c7; color: #d97706; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 4px rgba(217, 119, 6, 0.1);">
                                🎯 Product
                            </span>
                        </div>
                    </div>
                </div>
                """)
        
        # Welcome message in a card
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(f"""
                <div class="welcome-card" id="welcome-card">
                    <div style="text-align: center;">
                        <h2 style="color: #1e40af; margin-bottom: 15px;">👋 Welcome! I'm Monideep Chakraborti</h2>
                        <p style="color: #64748b; margin-bottom: 15px; font-size: 1.1em;">
                            I'm a Product Manager passionate about building intelligent technology that makes search, communication, and learning more accessible and inclusive.
                        </p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                            <div style="text-align: left;">
                                <h3 style="color: #1e40af; margin-bottom: 10px;">🎯 What I do:</h3>
                                <ul style="color: #64748b; margin: 0; padding-left: 20px;">
                                    <li>🏥 Lead biomedical search at NCBI/NIH</li>
                                    <li>🎯 Build AI-powered speech tools</li>
                                    <li>🧠 Design GenAI applications</li>
                                    <li>💡 Bridge product & technical execution</li>
                                </ul>
                            </div>
                            <div style="text-align: left;">
                                <h3 style="color: #1e40af; margin-bottom: 10px;">💬 Ask me about:</h3>
                                <ul style="color: #64748b; margin: 0; padding-left: 20px;">
                                    <li>🏥 NIH and biomedical search</li>
                                    <li>🎤 Speech accessibility & ASR</li>
                                    <li>🤖 Product management in AI/ML</li>
                                    <li>🚀 GenAI applications</li>
                                </ul>
                            </div>
                        </div>
                        <p style="color: #1e40af; font-weight: 600; margin-top: 20px;">
                            Let's connect and explore how we can build something amazing together! 🚀
                        </p>
                    </div>
                </div>
                """)
        
        # Chat interface in a card
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="card">')
                chatbot = gr.Chatbot(
                    label="💬 Chat with Monideep",
                    height=500,
                    show_label=True,
                    container=True,
                    avatar_images=["👤", "🚀"],
                    show_copy_button=True,
                    type="messages"
                )
                gr.HTML('</div>')
        
        # Input area in a card
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="card">')
                with gr.Row():
                    with gr.Column(scale=4):
                        msg = gr.Textbox(
                            label="💭 Ask me anything about my work, experience, or interests!",
                            placeholder="e.g., Tell me about your work at NIH, or What AI projects are you working on?",
                            lines=2,
                            max_lines=4,
                            show_label=True,
                        )
                    with gr.Column(scale=1):
                        submit_btn = gr.Button("🚀 Send", variant="primary", size="lg")
                        clear_btn = gr.Button("🗑️ Clear", variant="secondary", size="lg")
                gr.HTML('</div>')
        
        # Quick action buttons in a card
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="card">')
                gr.Markdown("**⚡ Quick Questions:**")
                with gr.Row():
                    quick_btn1 = gr.Button("🏥 NIH Work", size="sm", variant="outline", elem_classes=["quick-btn"])
                    quick_btn2 = gr.Button("🤖 AI Projects", size="sm", variant="outline", elem_classes=["quick-btn"])
                    quick_btn3 = gr.Button("🎯 Product Experience", size="sm", variant="outline", elem_classes=["quick-btn"])
                    quick_btn4 = gr.Button("💼 Connect", size="sm", variant="outline", elem_classes=["quick-btn"])
                gr.HTML('</div>')
        
        # Examples in a card
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML('<div class="card">')
                gr.Examples(
                    examples=[
                        "What are you working on at NIH/NCBI?",
                        "Tell me about your speech accessibility projects",
                        "How do you approach product management in AI/ML?",
                        "What GenAI applications are you most excited about?",
                        "Can you share some of your side projects?",
                        "I'd like to connect! What's the best way to reach you?"
                    ],
                    inputs=msg,
                    label="💡 Example Questions"
                )
                gr.HTML('</div>')
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #64748b; font-size: 0.9em;">
            <p>💡 Built with Gradio & OpenAI | 🔗 Let's connect and build something amazing!</p>
            <p>📧 <a href="mailto:monideep@example.com" style="color: #1e40af;">monideep@example.com</a> | 
            💼 <a href="https://linkedin.com/in/monideep" style="color: #1e40af;">LinkedIn</a></p>
        </div>
        """)
        
        # Event handlers
        def respond(message, history):
            if not message.strip():
                return history, ""
            
            # Add typing indicator
            history.append({"role": "user", "content": message})
            yield history, ""
            
            # Get response - pass the history as is, let the chat function handle conversion
            response = me.chat(message, history[:-1])  # Exclude the current message
            history.append({"role": "assistant", "content": response})
            yield history, ""
        
        def update_theme(is_dark):
            css = get_css(is_dark)
            return css
        
        # Connect components
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        submit_btn.click(respond, [msg, chatbot], [chatbot, msg])
        clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])
        theme_toggle.change(update_theme, [theme_toggle], [css_state])
        
        # Quick buttons
        quick_btn1.click(lambda: "What are you working on at NIH/NCBI?", outputs=msg)
        quick_btn2.click(lambda: "Tell me about your AI and machine learning projects", outputs=msg)
        quick_btn3.click(lambda: "How do you approach product management in AI/ML?", outputs=msg)
        quick_btn4.click(lambda: "I'd like to connect! What's the best way to reach you?", outputs=msg)
    
    # Launch the app
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=7863,
        show_error=True
    )
    