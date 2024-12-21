import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import json
import logging
import yaml
import os
import sys
import discord
from discord import AsyncWebhookAdapter, Webhook
from typing import List, Dict, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

class HalkarzScraper:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.validate_config()
        self.sent_halkarz_file = self.config['sent_halkarz_file']
        self.sent_halkarz = self.load_sent_halkarz()
        self.session: Optional[ClientSession] = None

    def load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as file:
                config = yaml.safe_load(file)
                logging.info("Configuration loaded successfully.")
                return config
        except FileNotFoundError:
            logging.critical(f"Configuration file '{path}' not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.critical(f"Error parsing the configuration file: {e}")
            sys.exit(1)

    def validate_config(self):
        required_keys = ['sent_halkarz_file', 'scrape_url', 'webhook_url', 'check_interval']
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            logging.critical(f"Missing required configuration keys: {', '.join(missing_keys)}")
            sys.exit(1)
        # Optionally, validate types and formats of config values here

    def load_sent_halkarz(self) -> Set[str]:
        if os.path.exists(self.sent_halkarz_file):
            try:
                with open(self.sent_halkarz_file, 'r') as file:
                    data = json.load(file)
                    sent_set = set(data)
                    logging.info(f"Loaded {len(sent_set)} previously sent halka arz entries.")
                    return sent_set
            except json.JSONDecodeError:
                logging.warning(f"Sent halkarz file '{self.sent_halkarz_file}' is corrupted. Starting fresh.")
                return set()
            except Exception as e:
                logging.error(f"Error loading sent halkarz file: {e}")
                return set()
        else:
            logging.info(f"Sent halkarz file '{self.sent_halkarz_file}' does not exist. Starting fresh.")
            return set()

    async def fetch_data(self, url: str) -> Optional[str]:
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    logging.info(f"Successfully fetched data from {url}")
                    return await response.text()
                else:
                    logging.error(f"Failed to fetch data: HTTP {response.status}")
                    return None
        except aiohttp.ClientError as e:
            logging.error(f"HTTP request failed: {e}")
            return None

    def check_for_new_halkarz(self, html_content: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        halka_arz_list = soup.find('ul', class_='halka-arz-list')
        
        if not halka_arz_list:
            logging.warning("Halka arz listesi bulunamadı.")
            return []

        li_items = halka_arz_list.find_all('li')
        latest_halkarz = []

        for li in li_items:
            new_div = li.find('div', class_='il-new')
            if new_div:
                company_name_tag = li.find('h3', class_='il-halka-arz-sirket')
                company_url_tag = li.find('a', href=True)
                date_tag = li.find('span', class_='il-halka-arz-tarihi')
                
                if not (company_name_tag and company_url_tag and date_tag):
                    logging.warning("Bir halka arz öğesi eksik bilgi içeriyor.")
                    continue

                company_name = company_name_tag.get_text(strip=True)
                company_url = company_url_tag['href']
                date = date_tag.get_text(strip=True)

                unique_key = f"{company_name}_{date}"
                if unique_key not in self.sent_halkarz:
                    halkarz_info = {
                        'Şirket': company_name,
                        'Tarih': date,
                        'Detaylar': company_url
                    }
                    latest_halkarz.append(halkarz_info)
                    self.sent_halkarz.add(unique_key)
                    logging.info(f"Yeni halka arz bulundu: {unique_key}")

        return latest_halkarz

    async def send_message(self, webhook_url: str, message: str):
        try:
            webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(self.session))
            await webhook.send(message, username="Halka Arz Bot")
            logging.info("Mesaj başarıyla gönderildi.")
        except discord.DiscordWebhookException as e:
            logging.error(f"Failed to send message via webhook: {e}")
        except Exception as e:
            logging.error(f"Unexpected error when sending message: {e}")

    async def scrape_data(self):
        url = self.config['scrape_url']
        html_content = await self.fetch_data(url)
        if html_content:
            latest_halkarz = self.check_for_new_halkarz(html_content)
            webhook_url = self.config['webhook_url']

            if latest_halkarz:
                for halkarz in latest_halkarz:
                    message = (
                        f"**Yeni Bir Halka Arz Geldi!**\n"
                        f"**Şirket:** {halkarz['Şirket']}\n"
                        f"**Tarih:** {halkarz['Tarih']}\n"
                        f"**Detaylar için [buraya tıklayın]({halkarz['Detaylar']})**\n\n"
                    )
                    await self.send_message(webhook_url, message)
                self.save_sent_halkarz()

    def save_sent_halkarz(self):
        try:
            with open(self.sent_halkarz_file, 'w') as file:
                json.dump(list(self.sent_halkarz), file, ensure_ascii=False, indent=4)
                logging.info(f"Sent halka arz bilgileri '{self.sent_halkarz_file}' dosyasına kaydedildi.")
        except Exception as e:
            logging.error(f"Failed to save sent halka arz info: {e}")

    async def run(self):
        self.session = aiohttp.ClientSession()
        logging.info("Scraper başlatıldı.")
        try:
            while True:
                await self.scrape_data()
                await asyncio.sleep(self.config['check_interval'])
        except asyncio.CancelledError:
            logging.info("Scraper durduruluyor...")
        finally:
            await self.session.close()
            self.save_sent_halkarz()
            logging.info("Scraper başarıyla kapatıldı.")

def main():
    scraper = HalkarzScraper('config.yaml')
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(scraper.run())
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Kullanıcı tarafından durduruldu.")
    finally:
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        logging.info("Program sonlandırıldı.")

if __name__ == "__main__":
    main()
