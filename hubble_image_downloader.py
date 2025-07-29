import os
import requests
import re
import sys # Import sys for flushing output
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuration
# These variables can be left empty/None. The script will prompt the user for input if they are not set.
BASE_URL = "" # Example: "https://esahubble.org/images/archive/category/galaxies/page/"
BASE_DOWNLOAD_DIR = "" # Example: "hubble_images/downloaded"
START_PAGE = None  # Example: 1
END_PAGE = None    # Example: 10
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Keywords to ignore during parsing and download
# These are image IDs that are not actual galaxy images but site assets
IGNORE_KEYWORDS = [
    'zip', 'search', 'archive', 'viewall', 'feed'
]
# Regex pattern for "thumb" followed by any characters
IGNORE_REGEX_PATTERNS = [
    re.compile(r'^thumb[a-z0-9]+$')
]

# Setup session with retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=frozenset(['HEAD', 'GET']))
session.mount("https://", HTTPAdapter(max_retries=retries))

def configure_settings():
    """
    Prompts the user for configuration settings if they are not already set.
    Returns a dictionary of configured settings.
    """
    global BASE_URL, BASE_DOWNLOAD_DIR, START_PAGE, END_PAGE

    settings = {
        'BASE_URL': BASE_URL,
        'BASE_DOWNLOAD_DIR': BASE_DOWNLOAD_DIR,
        'START_PAGE': START_PAGE,
        'END_PAGE': END_PAGE,
        'HEADERS': HEADERS,
        'IGNORE_KEYWORDS': IGNORE_KEYWORDS,
        'IGNORE_REGEX_PATTERNS': IGNORE_REGEX_PATTERNS
    }

    if not settings['BASE_URL']:
        settings['BASE_URL'] = input("Enter the base URL for the image archive (e.g., https://esahubble.org/images/archive/category/galaxies/page/): ")
        if not settings['BASE_URL'].endswith('/'):
            settings['BASE_URL'] += '/'
        if not settings['BASE_URL']:
            print("[ERROR] Base URL cannot be empty. Exiting.")
            sys.exit(1) # Exit if critical config is missing

    if not settings['BASE_DOWNLOAD_DIR']:
        settings['BASE_DOWNLOAD_DIR'] = input("Enter the base download directory (e.g., hubble_images/downloaded): ")
        if not settings['BASE_DOWNLOAD_DIR']:
            print("[ERROR] Download directory cannot be empty. Exiting.")
            sys.exit(1) # Exit if critical config is missing

    if settings['START_PAGE'] is None:
        while True:
            try:
                settings['START_PAGE'] = int(input("Enter the starting page number (e.g., 1): "))
                if settings['START_PAGE'] <= 0:
                    raise ValueError
                break
            except ValueError:
                print("[ERROR] Invalid starting page. Please enter a positive integer.")

    if settings['END_PAGE'] is None:
        while True:
            try:
                settings['END_PAGE'] = int(input(f"Enter the ending page number (e.g., {settings['START_PAGE'] + 9}): "))
                if settings['END_PAGE'] < settings['START_PAGE']:
                    print("[ERROR] Ending page cannot be less than starting page.")
                else:
                    break
            except ValueError:
                print("[ERROR] Invalid ending page. Please enter an integer.")
    
    # Update global variables for convenience if running as a script directly
    BASE_URL = settings['BASE_URL']
    BASE_DOWNLOAD_DIR = settings['BASE_DOWNLOAD_DIR']
    START_PAGE = settings['START_PAGE']
    END_PAGE = settings['END_PAGE']

    return settings

def get_image_ids(page_url, headers, ignore_keywords, ignore_regex_patterns):
    """
    Extract image IDs from the given page URL using regex and filter out unwanted IDs.
    """
    print(f"[CRAWLING PAGE] {page_url}")
    try:
        response = session.get(page_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not access page {page_url}: {e}")
        return []

    matches = re.findall(r'/images/([a-z0-9]+[a-z])/', response.text, re.IGNORECASE)
    
    image_ids = []
    for img_id in set(matches):
        if img_id in ignore_keywords:
            continue
        
        is_ignored_by_regex = False
        for pattern in ignore_regex_patterns:
            if pattern.match(img_id):
                is_ignored_by_regex = True
                break
        
        if is_ignored_by_regex:
            continue
            
        image_ids.append(img_id)
            
    return image_ids

def download_image(idx, total_images_on_page, page_num, image_id, save_dir, headers):
    """
    Downloads an image with a dynamic, line-based progress bar.
    Returns (status, downloaded_size, total_size).
    """
    os.makedirs(save_dir, exist_ok=True)
    image_url = f"https://cdn.esahubble.org/archives/images/large/{image_id}.jpg"
    img_path = os.path.join(save_dir, f"{image_id}.jpg")

    base_prefix = f"[{idx}/{total_images_on_page} - Page {page_num}] {image_id}.jpg - "
    
    bar_length = 30
    fill_char = '█'
    empty_char = '-'

    if os.path.exists(img_path):
        print(f"\r{base_prefix}Skipped (already exists)".ljust(len(base_prefix) + 40))
        return 'skipped', 0, 0

    total_size = 0
    try:
        head_response = session.head(image_url, headers=headers, timeout=10)
        head_response.raise_for_status()
        total_size = int(head_response.headers.get('Content-Length', 0))
    except requests.exceptions.RequestException:
        pass
        
    downloaded_size = 0
    try:
        response = session.get(image_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        chunk_size = 8192

        with open(img_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        percentage = (downloaded_size / total_size) * 100
                        filled_chars = int(bar_length * percentage / 100)
                        bar = fill_char * filled_chars + empty_char * (bar_length - filled_chars)
                        progress_text = f"[{bar}] {percentage:.1f}% {downloaded_size / (1024*1024):.2f}/{total_size / (1024*1024):.2f}MB"
                    else:
                        bar = empty_char * bar_length
                        progress_text = f"[----------] ?% {downloaded_size / (1024*1024):.2f}MB"
                    
                    print(f"\r{base_prefix}{progress_text.ljust(bar_length + 30)}", end="", flush=True) 
        
        if total_size > 0:
            final_progress_text = f"Downloaded... {downloaded_size / (1024*1024):.2f}/{total_size / (1024*1024):.2f}MB"
        else:
            final_progress_text = f"Downloaded... {downloaded_size / (1024*1024):.2f}MB"
        
        print(f"\r{base_prefix}{final_progress_text.ljust(bar_length + 30)}\n", end="", flush=True) 
        return 'downloaded', downloaded_size, total_size
    except requests.exceptions.HTTPError as e:
        if os.path.exists(img_path):
            os.remove(img_path)
        print(f"\r{base_prefix}Not Found (404)".ljust(len(base_prefix) + bar_length + 30) + "\n", end="", flush=True) if e.response.status_code == 404 else \
              print(f"\r{base_prefix}Error (HTTP: {e.response.status_code})".ljust(len(base_prefix) + bar_length + 30) + "\n", end="", flush=True)
        return 'not_found' if e.response.status_code == 404 else 'error', downloaded_size, total_size
    except requests.exceptions.RequestException as e:
        if os.path.exists(img_path):
            os.remove(img_path)
        print(f"\r{base_prefix}Error (Request: {e})".ljust(len(base_prefix) + bar_length + 30) + "\n", end="", flush=True)
        return 'error', downloaded_size, total_size
    except Exception as e:
        if os.path.exists(img_path):
            os.remove(img_path)
        print(f"\r{base_prefix}Error (Unexpected: {e})".ljust(len(base_prefix) + bar_length + 30) + "\n", end="", flush=True)
        return 'error', downloaded_size, total_size

def process_page(page_num, settings):
    """
    Processes a single page: gets image IDs and attempts to download them.
    Returns (downloaded_count_on_page, failed_image_ids_on_page).
    """
    page_url = f"{settings['BASE_URL']}{page_num}/"
    save_dir = os.path.join(settings['BASE_DOWNLOAD_DIR'], str(page_num))
    image_ids = get_image_ids(page_url, settings['HEADERS'], settings['IGNORE_KEYWORDS'], settings['IGNORE_REGEX_PATTERNS'])

    print(f"[INFO] Found {len(image_ids)} images on page {page_num}")
    
    downloaded_count_on_page = 0
    failed_image_ids_on_page = []

    for idx, image_id in enumerate(image_ids, start=1):
        status, _, _ = download_image(idx, len(image_ids), page_num, image_id, save_dir, settings['HEADERS'])
        
        if status == 'downloaded':
            downloaded_count_on_page += 1
        elif status == 'not_found' or status == 'error':
            failed_image_ids_on_page.append(image_id)
    
    print(f"[PAGE DONE] Page {page_num} complete. Total on page: {downloaded_count_on_page}")
    
    if failed_image_ids_on_page:
        print(f"[FAILED ON PAGE {page_num}] The following images failed to download or were not found:")
        for img_id in failed_image_ids_on_page:
            print(f"  - {img_id}.jpg")
    
    return downloaded_count_on_page, failed_image_ids_on_page

def generate_final_report(total_downloaded_count, all_failed_downloads):
    """
    Prints the final summary report of all downloads.
    """
    print(f"\n[COMPLETED] Downloaded {total_downloaded_count} images in total.")

    any_failed = any(all_failed_downloads[pg] for pg in all_failed_downloads)
    if any_failed:
        print("\n[SUMMARY OF ALL FAILED DOWNLOADS]")
        for pg, ids in all_failed_downloads.items():
            if ids:
                print(f"\nPage {pg} failed images:")
                for img_id in ids:
                    print(f"{img_id}.jpg")
    else:
        print("\nAll images downloaded successfully.")

def main():
    """
    Main function to run the Hubble image crawler.
    """
    settings = configure_settings()

    total_downloaded_count = 0
    all_failed_downloads = {}

    for page_num in range(settings['START_PAGE'], settings['END_PAGE'] + 1):
        downloaded_on_page, failed_on_page = process_page(page_num, settings)
        total_downloaded_count += downloaded_on_page
        all_failed_downloads[page_num] = failed_on_page

    generate_final_report(total_downloaded_count, all_failed_downloads)

if __name__ == "__main__":
    main()
