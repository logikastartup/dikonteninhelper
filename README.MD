# Dikontenin Helper

A web application for crawling, extracting, and managing content from web pages with a clean, modern interface.

## Features

- **Web-based Interface**: Intuitive dashboard for managing crawls
- **Powerful Crawling**: Extract content using Selenium WebDriver
- **Content Extraction**: Clean and extract main content from web pages
- **Smart Caching**: Configurable caching to avoid re-crawls
- **Search & Filter**: Quickly find crawled pages by URL or title
- **Bulk Operations**: Select and copy multiple pages at once
- **RESTful API**: Programmatic access to all functionality
- **Responsive Design**: Works on desktop and tablet devices

## Requirements

- Python 3.12+
- Chrome or Firefox browser
- Required Python packages (see requirements.txt)
- Google Chrome (for Selenium WebDriver)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd dikonteninhelper
   python -m venv .venv
   pip install -r requirements.txt
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Unix/Linux/MacOS
   ```

3. Configure the application by editing `config.ini` if needed.

4. Run the application:
   ```bash
   python main_gui.py
   ```

## Usage

This will:
1. Start the FastAPI server
2. Open the web interface in your default browser
3. Display the server status in the GUI

The web interface allows you to:

1. **Crawl New URLs**
   - Enter a URL in the input field
   - Click "Crawl" to start the crawling process
   - View the status and results in the interface

2. **Search and Filter**
   - Search crawled pages by URL or title
   - Filter results by date range
   - Sort results by different columns

3. **View Content**
   - Click on any result to view the full extracted content
   - Expand/collapse content sections
   - Copy content to clipboard in JSON format

# Configuration

Edit `config.ini` to customize the application behavior:

```ini
[server]
host = 127.0.0.1  # Server host
port = 4477       # Server port

[storage]
save_folder = data              # Folder to store data files
database_path = data/crawled_data.db  # SQLite database path

[crawler]
browser_timeout = 60   # Selenium browser timeout in seconds
skip_crawl_time = 60    # Days before recrawling a URL
sleep_time = 3          # Wait time for page loading
browser_path =          # Optional: Path to Chrome/Firefox binary
```

## Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the application:
   ```bash
   python main_gui.py
   ```

3. Access the web interface at: http://localhost:8000

## License

MIT License

## Support

For support, please open an issue in the repository.