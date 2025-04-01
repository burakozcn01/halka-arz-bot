import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import json
import logging
import yaml
import os
import sys
from typing import List, Dict, Optional, Set

logging.basicConfig(
    level=logging.WARNING,
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
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.critical(f"Configuration file '{path}' not found.")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.critical(f"Error parsing the configuration file: {e}")
            sys.exit(1)

    def validate_config(self):
        required_keys = ['sent_halkarz_file', 'scrape_url', 'check_interval']
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            logging.critical(f"Missing required configuration keys: {', '.join(missing_keys)}")
            sys.exit(1)

    def load_sent_halkarz(self) -> Set[str]:
        if os.path.exists(self.sent_halkarz_file):
            try:
                with open(self.sent_halkarz_file, 'r') as file:
                    data = json.load(file)
                    return set(data)
            except (json.JSONDecodeError, Exception):
                return set()
        else:
            return set()

    async def fetch_data(self, url: str) -> Optional[str]:
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Failed to fetch data: HTTP {response.status}")
                    return None
        except aiohttp.ClientError as e:
            logging.error(f"HTTP request failed: {e}")
            return None

    def parse_halkarz_data(self, html_content: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        halka_arz_list = soup.find('ul', class_='halka-arz-list')
        
        if not halka_arz_list:
            return []

        li_items = halka_arz_list.find_all('li')
        all_halkarz = []
        
        for li in li_items:
            company_name_tag = li.find('h3', class_='il-halka-arz-sirket')
            date_tag = li.find('span', class_='il-halka-arz-tarihi')
            company_url_tag = li.find('article').find('a', href=True)
            
            if not (company_name_tag and company_url_tag and date_tag):
                continue

            company_name = company_name_tag.get_text(strip=True)
            company_url = company_url_tag['href']
            date = date_tag.get_text(strip=True)
            
            unique_key = f"{company_name}_{date}"
            
            halkarz_info = {
                'Şirket': company_name,
                'Tarih': date,
                'Detaylar': company_url,
                'UniqueKey': unique_key
            }
            all_halkarz.append(halkarz_info)
        
        return all_halkarz

    def print_to_terminal(self, message: str):
        print("\n" + "="*50)
        print(message)
        print("="*50 + "\n")

    def print_halkarz(self, halkarz: Dict[str, str], is_new: bool = False):
        prefix = "**YENİ**" if is_new else ""
        print(f"{prefix} {halkarz['Şirket']} - {halkarz['Tarih']}")

    async def scrape_data(self, first_run: bool = False) -> int:
        url = self.config['scrape_url']
        html_content = await self.fetch_data(url)
        if not html_content:
            return 0

        all_halkarz = self.parse_halkarz_data(html_content)
        new_halkarz = []
        
        if first_run:
            print("\nMevcut Halka Arzlar:")
            print("="*60)
            for idx, halkarz in enumerate(all_halkarz, 1):
                print(f"{idx}. {halkarz['Şirket']} - {halkarz['Tarih']}")
                self.sent_halkarz.add(halkarz['UniqueKey'])
            print("="*60)
        else:
            for halkarz in all_halkarz:
                if halkarz['UniqueKey'] not in self.sent_halkarz:
                    new_halkarz.append(halkarz)
                    self.sent_halkarz.add(halkarz['UniqueKey'])
            
            if new_halkarz:
                for halkarz in new_halkarz:
                    message = (
                        f"**Yeni Bir Halka Arz Geldi!**\n"
                        f"**Şirket:** {halkarz['Şirket']}\n"
                        f"**Tarih:** {halkarz['Tarih']}\n"
                        f"**Detaylar için:** {halkarz['Detaylar']}\n\n"
                    )
                    self.print_to_terminal(message)
        
        self.save_sent_halkarz()
        return len(all_halkarz)

    def save_sent_halkarz(self):
        try:
            with open(self.sent_halkarz_file, 'w') as file:
                json.dump(list(self.sent_halkarz), file, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Failed to save sent halka arz info: {e}")

    async def run(self):
        self.session = aiohttp.ClientSession()
        
        print("\n" + "="*60)
        print("   HALKA ARZ TAKİP SİSTEMİ BAŞLATILDI")
        print("   Düzenli aralıklarla yeni halka arzlar kontrol ediliyor...")
        print("   (Programdan çıkmak için Ctrl+C tuşlarına basın)")
        print("="*60 + "\n")
        
        print("İlk veri taraması yapılıyor, lütfen bekleyin...")
        count = await self.scrape_data(first_run=True)
        print(f"Tarama tamamlandı. {count} halka arz kaydedildi.")
        print(f"Takip devam ediyor... Her {self.config['check_interval']} saniyede bir yenileniyor.\n")
        
        try:
            kontrol_sayaci = 0
            while True:
                await asyncio.sleep(self.config['check_interval'])
                
                kontrol_sayaci += 1
                print(f"Yeni halka arzlar kontrol ediliyor... ({kontrol_sayaci}. kontrol)")
                await self.scrape_data(first_run=False)
                
                if kontrol_sayaci % 10 == 0:
                    html_content = await self.fetch_data(self.config['scrape_url'])
                    if html_content:
                        all_halkarz = self.parse_halkarz_data(html_content)
                        print("\nMevcut tüm halka arzlar listesi:")
                        print("-" * 60)
                        for idx, halkarz in enumerate(all_halkarz, 1):
                            print(f"{idx}. {halkarz['Şirket']} - {halkarz['Tarih']}")
                        print("-" * 60)
                
                print(f"Toplam kayıtlı halka arz sayısı: {len(self.sent_halkarz)}\n")
        except asyncio.CancelledError:
            pass
        finally:
            await self.session.close()
            self.save_sent_halkarz()

def create_default_config():
    config_file = 'config.yaml'
    example_config = {
        'sent_halkarz_file': 'sent_halkarz.json',
        'scrape_url': 'https://halkarz.com/',
        'check_interval': 300  # 5 dakika
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(example_config, f, default_flow_style=False)
    
    print(f"'{config_file}' dosyası bulunamadı. Örnek bir konfigürasyon dosyası oluşturuldu.")
    print("Lütfen dosyayı kontrol edip gerekli düzenlemeleri yapın ve programı tekrar çalıştırın.")

async def run_scraper(scraper):
    try:
        await scraper.run()
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından sonlandırıldı.")

def main():
    config_file = 'config.yaml'
    if not os.path.exists(config_file):
        create_default_config()
        return
    
    scraper = HalkarzScraper(config_file)
    
    if sys.version_info >= (3, 10):
        asyncio.run(run_scraper(scraper))
    else:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(run_scraper(scraper))
        except KeyboardInterrupt:
            print("\nProgram kullanıcı tarafından sonlandırıldı.")
        finally:
            pending = asyncio.all_tasks(loop=loop)
            for task in pending:
                task.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()

if __name__ == "__main__":
    main()
