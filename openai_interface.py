from openai import OpenAI
from openai.types.beta import Thread
from openai.types.
from dotenv import load_dotenv
import os


class OpenAIAssistant:
    def __init__(self, assistant_id, model="gpt-4-1106-preview"):
        load_dotenv()
        self.apikey = os.getenv('OPENAI_API_KEY')
        
        self.client = OpenAI(api_key=self.apikey)
        self.assistant_id = assistant_id
        self.model = model
        self.thread_id = None
        

    def create_thread(self, init_message):
        # Create a new thread
        
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        return self.thread_id

    def add_message(self, thread, role, content):
        # Add a message to the thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role=role,
            content=content
        )
        
    def handle_message(self, thread_id, content):
        if not thread_id:
            thread = self.client.beta.threads.create()
            thread_id = thread.id
            self.client.beta.threads.messages.create(thread_id=thread_id, role="user", content=content)
            response = self.run_assistant(thread_id)
        else:
            self.client.beta.threads.messages.create(thread_id=thread_id, role="user", content=content)
            response = self.run_assistant(thread_id)

        return response, thread_id


    def run_assistant(self):
        # Run the assistant on the thread
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        return run

# Example usage
# assistant = OpenAIAssistant(assistant_id='your_assistant_id')
# thread_id = assistant.create_thread()
# assistant.add_message("user", "Hello, how are you?")
# run = assistant.run_assistant()
