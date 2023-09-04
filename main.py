import asyncio
import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(intents=intents)

sent_halkarz = []

# burakozcan01

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    scrape_data.start()

async def fetch_data(url):
    response = requests.get(url)
    return response.text

# burakozcan01

def check_for_new_halkarz(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    halka_arz_list = soup.find('ul', class_='halka-arz-list')
    li_items = halka_arz_list.find_all('li')

    latest_halkarz = []

    for li in li_items:
        new_div = li.find('div', class_='il-new')
        if new_div:
            company_name = li.find('h3', class_='il-halka-arz-sirket').text.strip()
            company_url = li.find('a', href=True)['href']
            date = li.find('span', class_='il-halka-arz-tarihi').text.strip()

            halkarz_info = {
                'Şirket': company_name,
                'Tarih': date,
                'Detaylar': company_url
            }

            if halkarz_info not in sent_halkarz:
                latest_halkarz.append(halkarz_info)
                sent_halkarz.append(halkarz_info)

    return latest_halkarz

# burakozcan01

@tasks.loop(minutes=1)
async def scrape_data():
    url = 'https://halkarz.com/'
    html_content = await fetch_data(url)
    latest_halkarz = check_for_new_halkarz(html_content)
    channel_id = KANALID  # Kanal ID'sini buraya ekleyin
    channel = bot.get_channel(channel_id)

    if latest_halkarz:
        for halkarz in latest_halkarz:
            message = f"Yeni bir halka arz geldi!\n"
            message += f'Şirket: {halkarz["Şirket"]}\nTarih: {halkarz["Tarih"]}\nDetaylar için [buraya tıklayın]({halkarz["Detaylar"]})\n\n'
            await channel.send(message)

# burakozcan01

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.start('TOKEN'))  # Discord bot tokeninizi buraya ekleyin