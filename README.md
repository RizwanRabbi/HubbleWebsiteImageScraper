Hubble Website Image Crawler/Scraper
This Python script efficiently downloads images from the ESA Hubble Space Telescope's official website. It handles existing files, retries failed downloads, filters out non-image assets, and provides a dynamic progress bar. The script is modular, user-friendly, and prompts for configuration if not pre-set.

Features
Batch Downloads: Crawls and downloads images from a specified range of archive pages.

Resume Downloads: Skips already downloaded images.

Error Handling: Retries network requests and manages HTTP errors.

Smart Filtering: Ignores website assets (e.g., zip.jpg, thumbXXXX.jpg).

Live Progress: Shows real-time download progress with a visual bar and size.

Organized Output: Saves images into page-numbered subdirectories.

Interactive Setup: Prompts for BASE_URL, BASE_DOWNLOAD_DIR, START_PAGE, and END_PAGE if unset.

Failure Reports: Lists failed or missing images per page.

Getting Started
Prerequisites
Python 3

requests library (pip install requests)

Configuration
Edit the hubble_image_downloader.py file to set these variables, or leave them empty to be prompted at runtime:

BASE_URL: Base URL for the image archive category (e.g., https://esahubble.org/images/archive/category/galaxies/page/).

BASE_DOWNLOAD_DIR: Root directory for saved images (e.g., hubble_images/downloaded).

START_PAGE: Starting page number (inclusive).

END_PAGE: Ending page number (inclusive).

HEADERS: HTTP headers (e.g., {"User-Agent": "..."}).

# Configuration
BASE_URL = "" # Example: "https://esahubble.org/images/archive/category/galaxies/page/"
BASE_DOWNLOAD_DIR = "" # Example: "hubble_images/downloaded"
START_PAGE = None  # Example: 1
END_PAGE = None    # Example: 10
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

Running the Script
python hubble_image_downloader.py

The script will prompt for configurations if needed, then start crawling and downloading.

Output Example
[CRAWLING PAGE] https://esahubble.org/images/archive/category/galaxies/page/2/
[INFO] Found 51 images on page 2
[1/51 - Page 2] potw2420a.jpg - [██████████████████████████████] 100.0% 7.68/7.68MB
[2/51 - Page 2] potw2401a.jpg - [██████████████████████████████] 100.0% 4.42/4.42MB
[3/51 - Page 2] potw2351a.jpg - [██████████████████████████████] 100.0% 4.74/4.74MB
[4/51 - Page 2] potw2348a.jpg - Skipped (already exists)
[5/51 - Page 2] potw2345a.jpg - [██████████████████████████████] 100.0% 1.15/1.15MB
...
[PAGE DONE] Page 2 complete. Total on page: 48
[FAILED ON PAGE 2] The following images failed to download or were not found:
  - example_failed_1.jpg
  - example_failed_2.jpg
[CRAWLING PAGE] https://esahubble.org/images/archive/category/galaxies/page/3/
[INFO] Found 57 images on page 3
...
[COMPLETED] Downloaded 105 images in total.

[SUMMARY OF ALL FAILED DOWNLOADS]

Page 2 failed images:
  example_failed_1.jpg
  example_failed_2.jpg

All images downloaded successfully.

Contributing
Feel free to fork this repository, open issues, or submit pull requests.

License
This project is open source and available under the MIT License.
