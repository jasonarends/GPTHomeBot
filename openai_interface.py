from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from icecream import ic
import os
import time
from datetime import datetime
from assistant_functions import AssistantFunctions

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
        
    async def handle_message(self, thread_id, user_name, content):
        # Modified to include user_name
        if not thread_id:
            thread_id = self.create_thread()
        # Include time and user's name or nickname in the content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content_with_name = f"{timestamp} - {user_name}: {content}"
        self.add_message(thread_id, "user", content_with_name)
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
            status = run_status.status
            if status == 'completed':
                break
            elif status == 'requires_action':
                # Handle required actions for function calls
                tool_outputs = self.handle_function_calls(run_status.required_action.submit_tool_outputs.tool_calls)
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
            elif status in ['expired', 'cancelled', 'failed']:
                # Handle expired, cancelled, and failed runs
                # Log the error or take appropriate action
                break
            elif status in ['queued', 'in_progress']:
                # Continue waiting
                await asyncio.sleep(1)
            else:
                # Handle unexpected statuses
                # Log the issue or take corrective action
                break

        # Retrieve the thread to get messages
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        #ic(messages)

        # Filter the assistant's responses for this run and sort by creation time
        assistant_responses = [msg for msg in messages.data if msg.role == "assistant" and msg.run_id == run_id]
        sorted_responses = sorted(assistant_responses, key=lambda msg: msg.created_at)

        # Extract text values from sorted responses
        return [response.content[0].text.value for response in sorted_responses if isinstance(response.content, list) and response.content]

    def handle_function_calls(self, tool_calls):
        tool_outputs = []
        ic(tool_calls)
        for call in tool_calls:
            function_name = call.function.name
            arguments = call.function.arguments
            if hasattr(AssistantFunctions, function_name):
                function = getattr(AssistantFunctions, function_name)
                output = function(arguments)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output,
                })
        ic(tool_outputs)
        return tool_outputs
