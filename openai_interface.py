from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from icecream import ic
import os
import time

class OpenAIAssistant:
    def __init__(self, assistant_id, model="gpt-4-1106-preview"):
        load_dotenv()
        self.apikey = os.getenv('OPENAI_API_KEY')
        
        self.client = OpenAI(api_key=self.apikey)
        self.assistant_id = assistant_id
        self.model = model

    def create_thread(self):
        # Create a new thread
        ic()
        thread = self.client.beta.threads.create()
        return thread.id

    def add_message(self, thread_id, role, content):
        # Add a message to the thread
        ic()
        ic(thread_id, role, content)
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
        
    async def handle_message(self, thread_id, content):
        if not thread_id:
            thread_id = self.create_thread()
        ic()
        self.add_message(thread_id, "user", content)
        return await self.run_assistant(thread_id), thread_id

    async def run_assistant(self, thread_id):
        # Initiate a run on the thread
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )
        run_id = run.id  # Store the run_id

        # Check the run status periodically
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run_status.status == 'completed':
                break
            await asyncio.sleep(1)

        # Retrieve the thread to get messages
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        ic(messages)

        # Filter the assistant's responses for this run and sort by creation time
        assistant_responses = [msg for msg in messages.data if msg.role == "assistant" and msg.run_id == run_id]
        sorted_responses = sorted(assistant_responses, key=lambda msg: msg.created_at)

        # Extract text values from sorted responses
        return [response.content[0].text.value for response in sorted_responses if isinstance(response.content, list) and response.content]

