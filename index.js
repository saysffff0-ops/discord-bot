const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

// لما يشتغل البوت
client.once('ready', () => {
  console.log(`✅ Logged in as ${client.user.tag}`);
});

// أوامر بسيطة
client.on('messageCreate', message => {
  if (message.author.bot) return;

  if (message.content === 'ping') {
    message.reply('🏓 pong!');
  }

  if (message.content === 'مرحبا') {
    message.reply('هلا والله 👋');
  }
});

// حط التوكن هنا 👇
client.login('YOUR_BOT_TOKEN');