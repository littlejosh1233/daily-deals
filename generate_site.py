import feedparser
import re
from bs4 import BeautifulSoup
import warnings
from bs4 import MarkupResemblesLocatorWarning
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# --- CONFIGURATION ---
AFFILIATE_TAG = "your_amazon_tag-20"
RSS_FEED_URL = "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&searchin=first&auto_subscribe=1&rss=1"

def parse_price(text):
    """Extract price from text (e.g. '$149.99' -> '149.99')."""
    match = re.search(r'\$?(\d+(?:\.\d{2})?)', text)
    if match:
        return match.group(1)
    return "0.00"

def get_live_deals():
    """Fetches real deals from an RSS feed and prepares them for the template."""
    print(f"Fetching live deals from {RSS_FEED_URL}...")
    feed = feedparser.parse(RSS_FEED_URL)
    
    deals = []
    
    # Grab the top 12 deals to populate our grid
    for entry in feed.entries[:12]:
        # Parse the HTML snippet in the RSS feed to find the image
        soup = BeautifulSoup(entry.summary, 'html.parser')
        
        # Slickdeals puts images in various formats in their RSS feed
        image_url = "https://via.placeholder.com/300x200?text=Top+Deal"
        img_tag = soup.find('img')
        
        if img_tag:
            # Try different attributes that might contain the real image URL
            if img_tag.get('src') and not 'attachment.php' in img_tag.get('src'):
                 image_url = img_tag.get('src')
            elif img_tag.get('data-original'):
                 image_url = img_tag.get('data-original')
            elif img_tag.parent and img_tag.parent.name == 'a' and img_tag.parent.get('href') and ('.jpg' in img_tag.parent.get('href') or '.png' in img_tag.parent.get('href')):
                 # Sometimes the image is linked wrapping a smaller thumbnail
                 image_url = img_tag.parent.get('href')
                 
        # Ensure it's an absolute URL
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        elif image_url.startswith('/'):
            image_url = 'https://slickdeals.net' + image_url
            
        # Clean up slickdeals tracking redirect if possible to reveal original URL
        link = entry.link
        if "amazon.com" in link:
             # Basic injection. A real app would parse the URL params properly
             link = f"{link}&tag={AFFILIATE_TAG}" if "?" in link else f"{link}?tag={AFFILIATE_TAG}"
             
        deal = {
            "title": entry.title,
            "image_url": image_url,
            "deal_price": parse_price(entry.title),
            "original_price": "", 
            "discount_percent": "", 
            "url": link
        }
        deals.append(deal)
        
    return deals

def build_site():
    print("Initializing site generator...")
    
    deals_data = get_live_deals()
    
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')

    print(f"Rendering {len(deals_data)} live deals into HTML...")
    html_output = template.render(
        date_generated=datetime.now().strftime("%B %d, %Y, %I:%M %p"),
        deals=deals_data,
        affiliate_tag=AFFILIATE_TAG
    )

    if not os.path.exists('docs'):
        os.makedirs('docs')
        
    output_filename = 'docs/index.html'
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"Successfully generated static site: {output_filename}")

if __name__ == "__main__":
    build_site()
