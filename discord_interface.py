import discord
from openai_interface import OpenAIAssistant
import os
from dotenv import load_dotenv
from icecream import ic

class DiscordInterface:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
        self.assistant = OpenAIAssistant(assistant_id=self.assistant_id)
        
        intents = discord.Intents.default()
        intents.messages = True  # Adjust this based on your needs
        intents.message_content = True
        intents.guild_messages = True
        intents.dm_messages = True

        self.client = discord.Client(intents=intents)

    async def on_ready(self):
        print(f'{self.client.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.client.user:
            return

        user_name = message.author.nick or message.author.name  # Get nickname if available, else username
        if self.client.user in message.mentions and isinstance(message.channel, discord.TextChannel):
            async with message.channel.typing():  # Show typing indicator
                responses, thread_id = await self.assistant.handle_message(None, user_name, message.content)
                thread = await message.create_thread(name=thread_id)
                for response in responses:
                    await thread.send(response)
        elif isinstance(message.channel, discord.Thread) and message.channel.name.startswith("thread_"):
            async with message.channel.typing():  # Show typing indicator
                responses, _ = await self.assistant.handle_message(message.channel.name, user_name, message.content)
                for response in responses:
                    await message.channel.send(response)

    def run(self):
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.client.run(self.token)

if __name__ == "__main__":
    bot = DiscordInterface()
    bot.run()
