import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import logging
import yaml
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

sent_halkarz_file = config['sent_halkarz_file']
sent_halkarz = []

if os.path.exists(sent_halkarz_file):
    with open(sent_halkarz_file, 'r') as file:
        sent_halkarz = json.load(file)

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                logging.error(f"Failed to fetch data: HTTP {response.status}")
                return None

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

async def send_message(webhook_url, message):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, adapter=discord.AsyncWebhookAdapter(session))
        await webhook.send(message)

async def scrape_data():
    url = config['scrape_url']
    try:
        html_content = await fetch_data(url)
        if html_content:
            latest_halkarz = check_for_new_halkarz(html_content)
            webhook_url = config['webhook_url']

            if latest_halkarz:
                for halkarz in latest_halkarz:
                    message = (
                        f"Yeni bir halka arz geldi!\n"
                        f'Şirket: {halkarz["Şirket"]}\n'
                        f'Tarih: {halkarz["Tarih"]}\n'
                        f'Detaylar için [buraya tıklayın]({halkarz["Detaylar"]})\n\n'
                    )
                    await send_message(webhook_url, message)
                with open(sent_halkarz_file, 'w') as file:
                    json.dump(sent_halkarz, file)
    except Exception as e:
        logging.error(f"Error during scraping: {e}")

async def main():
    while True:
        await scrape_data()
        await asyncio.sleep(config['check_interval'])

if __name__ == "__main__":
    asyncio.run(main())
