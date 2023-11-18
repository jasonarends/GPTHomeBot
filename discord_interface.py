import discord
import os
from dotenv import load_dotenv

class DiscordInterface:
    """
    Handles interactions with Discord.
    """

    def __init__(self):
        """
        Initializes the Discord bot.
        """
        load_dotenv()
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.client = discord.Client()

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

        # Respond only in threads or start a new thread
        if message.channel.type == discord.ChannelType.text and not message.is_system():
            if message.thread:
                await message.thread.send(f"Echo: {message.content}")
            else:
                thread = await message.create_thread(name=f"Thread for {message.author.display_name}")
                await thread.send(f"Echo: {message.content}")
        # Here you can integrate with ChatGPT for more complex responses

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
