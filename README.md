
# Hubble Image Scraper

A no-fuss tool to grab Hubble images from the ESA website. No more right-click-save nonsense.

It scrapes images only from pages that start with `https://esahubble.org/images/`. The images are saved in `.jpg` format, organized by page number, and the script skips any files you’ve already downloaded.

Works well for grabbing galaxies, nebulae, or other catagories they've posted.

---

## How to Use It

### 1. Requirements

You'll need these first:

```bash
pip install requests beautifulsoup4
```

---

### 2. Configure the Script

```python
BASE_URL = ""  # Example: "https://esahubble.org/images/archive/category/galaxies/page/"
BASE_DOWNLOAD_DIR = ""  # Example: "hubble_images/galaxes"
START_PAGE = None  # Example: 1
END_PAGE = None    # Example: 10 
```

You can:

- Set stuff up in the script 
- Or run it and fill in when asked

---

### 3. Run the Script

```bash
python hubble_image_downloader.py
```

---

## Example Output

```text
[CRAWLING PAGE] https://esahubble.org/images/archive/category/galaxies/page/2/
[INFO] Found 51 images on page 2
[1/51 - Page 2] potw2420a.jpg - 100% 7.68MB
[4/51 - Page 2] potw2348a.jpg - Skipped (already exists)
...
[COMPLETED] Downloaded 105 images in total.
```

---

## What It Does

- ✅ Bulk downloads Hubble pics  
- 🔁 Skips stuff you've already got  
- 🚫 Ignores thumbnails and junk  
- 📂 Organizes by page (for your sanity)  
- 📶 Retries if your net flakes out  
- 📊 Shows progress so you know it's not frozen  

---

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).
