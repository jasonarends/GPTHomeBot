import discord
from openai_interface import OpenAIAssistant
import os
from dotenv import load_dotenv
from icecream import ic
from utils import DatabaseManager, Utils

class DiscordInterface:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.assistant_ids = self.build_assistant_mapping()
        #self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        #self.assistant = OpenAIAssistant(assistant_id=self.assistant_id)
        
        intents = discord.Intents.default()
        intents.messages = True  # Adjust this based on your needs
        intents.message_content = True
        intents.guild_messages = True
        intents.dm_messages = True

        self.client = discord.Client(intents=intents)
        self.db_manager = DatabaseManager("discord_users.sqlite3")
    
    def build_assistant_mapping(self):
        mapping = {}
        for key, value in os.environ.items():
            if key.startswith("OPENAI_ASST_ID_"):
                channel_id = key.split("_")[-1] # extract the channel id
                mapping[channel_id] = value
        ic(mapping)
        return mapping

    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')
        

    async def on_message(self, message: discord.Message):
        if message.author == self.client.user:
            return

        user_name = message.author.name  # Get nickname if available, else username
        user_id = str(message.author.id)
        if isinstance(message.channel, discord.Thread):
            parent_channel_id = str(message.channel.parent_id)
        else:
            parent_channel_id = str(message.channel.id)
            
        #channel_id = str(message.channel.id)
        assistant_id = self.assistant_ids.get(parent_channel_id, os.getenv('OPENAI_ASST_ID_DEFAULT'))
        self.assistant = OpenAIAssistant(assistant_id = assistant_id)
        ic(message, user_name, user_id, parent_channel_id, assistant_id)
        
        # For DMs
        if isinstance(message.channel, discord.DMChannel):
            thread_id = self.db_manager.get_thread_id(user_id)
            if not thread_id:
                responses, thread_id = await self.assistant.handle_message(thread_id, user_name, message.content)
                self.db_manager.set_thread_id(user_id, thread_id)
            else:
                responses, _ = await self.assistant.handle_message(thread_id, user_name, message.content)
            for response in responses:
                for part in Utils.split_messages(response):
                    await message.channel.send(part)
                
        elif self.client.user in message.mentions and isinstance(message.channel, discord.TextChannel):
            async with message.channel.typing():  # Show typing indicator
                responses, thread_id = await self.assistant.handle_message(None, user_name, message.content)
                thread = await message.create_thread(name=thread_id)
                for response in responses:
                    for part in Utils.split_messages(response):
                        await thread.send(part)
        elif isinstance(message.channel, discord.Thread) and message.channel.name.startswith("thread_"):
            async with message.channel.typing():  # Show typing indicator
                responses, _ = await self.assistant.handle_message(message.channel.name, user_name, message.content)
                for response in responses:
                    for part in Utils.split_messages(response):
                        await message.channel.send(part)

    def run(self):
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.client.run(self.token)

if __name__ == "__main__":
    bot = DiscordInterface()
    bot.run()
