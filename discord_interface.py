import discord
import os
import datetime
from icecream import ic
from dotenv import load_dotenv

class DiscordInterface:
    """
    Handles interactions with Discord.
    """

    def __init__(self, assistant):
        """
        Initializes the Discord bot.
        """
        load_dotenv()
        self.token = os.getenv('DISCORD_BOT_TOKEN')

        # Set up Intents
        intents = discord.Intents.default()
        
        intents.messages = True  # Adjust this based on your needs
        intents.message_content = True
        intents.guild_messages = True
        intents.dm_messages = True

        self.client = discord.Client(intents=intents)
        self.assistant = assistant

    async def on_ready(self):
        """
        Called when the bot is ready to start.
        """
        print(f'{self.client.user} has connected to Discord!')

    async def on_message(self, message):
        """
        Handles incoming messages.
        """
        if message.author == self.client.user:
            return

        # Debugging: Print the message content
        ic(message)
        ic(message.content)
        ic(message.mentions)

        # Improved mention detection
        if self.client.user in message.mentions and isinstance(message.channel, discord.TextChannel):
            response, thread_id = self.assistant.handle_message(None, message.content)
            thread = await message.create_thread(name=thread_id)
            await thread.send(response)
            # Create a unique thread name
            #timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            #thread_name = f"GPT Chat - {timestamp}"
            #thread = await message.create_thread(name=thread_name)
            #await thread.send(f"Thread started in response to {message.author.display_name}'s mention.")

        # Respond to messages in threads started by the bot
        elif isinstance(message.channel, discord.Thread) and message.channel.name.startswith("thread_"):
            response, _ = self.assistant.handle_message(message.channel.name, message.content)
            await message.channel.send(response)

    def run(self):
        """
        Starts the Discord bot.
        """
        self.client.event(self.on_ready)
        self.client.event(self.on_message)
        self.client.run(self.token)

if __name__ == "__main__":
    bot = DiscordInterface()
    bot.run()
