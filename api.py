import os
import configparser
from fastapi import FastAPI, HTTPException, Query, Request, Form, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from selenium_crawler import SeleniumCrawler
from html_cleaner import HtmlCleaner
from database import (
    init_db,
    save_crawled_page,
    get_crawled_page,
    should_recrawl,
    get_session,
    CrawledPage,
)

# Read configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Create app
app = FastAPI(
    title="Dikontenin Helper",
    description="API for crawling and processing web pages",
    version="1.0.0",
)

# Setup templates directory for web interface
# For PyInstaller, we need to handle different path scenarios
template_dirs = [
    "templates",  # Standard relative path when running as script
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),  # Absolute path
]

# If running as PyInstaller bundle
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Add PyInstaller specific paths
    template_dirs.extend([
        os.path.join(sys._MEIPASS, "templates"),
        os.path.join(os.path.dirname(sys.executable), "templates"),
        os.path.join(os.path.dirname(sys.executable), "_internal", "templates"),
    ])

# Find the first valid template directory
template_dir = None
for dir_path in template_dirs:
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        template_dir = dir_path
        logger.info(f"Found templates at: {template_dir}")
        break

if not template_dir:
    logger.warning("No valid templates directory found! Using default path.")
    template_dir = "templates"

templates = Jinja2Templates(directory=template_dir)

# Create a directory for static files if it doesn't exist
static_dirs = [
    "static",  # Standard relative path
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),  # Absolute path
]

# If running as PyInstaller bundle
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Add PyInstaller specific paths
    static_dirs.extend([
        os.path.join(sys._MEIPASS, "static"),
        os.path.join(os.path.dirname(sys.executable), "static"),
        os.path.join(os.path.dirname(sys.executable), "_internal", "static"),
    ])

# Find the first valid static directory
static_dir = None
for dir_path in static_dirs:
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        static_dir = dir_path
        logger.info(f"Found static files at: {static_dir}")
        break

if not static_dir:
    logger.warning("No valid static directory found! Creating default path.")
    static_dir = "static"
    os.makedirs(static_dir, exist_ok=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize database
init_db()

# Initialize crawler
crawler = SeleniumCrawler()


# Models
class UrlRequest(BaseModel):
    url: HttpUrl


class CrawlResponse(BaseModel):
    """Response model for crawl API"""

    url: str
    title: str
    description: str
    content: str
    success: bool
    message: Optional[str] = None


class PageIdsRequest(BaseModel):
    """Request model for page IDs"""

    ids: List[int]


# Status tracking
is_server_running = True


# Web interface endpoints
@app.get("/", response_class=HTMLResponse)
async def home_page(
    request: Request,
    url: str = None,
    title: str = None,
    page: int = 1,
    per_page: int = 9,
):
    """Home page with search interface and pagination"""
    session = get_session()
    try:
        query = session.query(CrawledPage)

        # Apply filters if provided
        if url:
            query = query.filter(CrawledPage.url.ilike(f"%{url}%"))
        if title:
            query = query.filter(CrawledPage.title.ilike(f"%{title}%"))

        # Get total count for pagination
        total_count = query.count()

        # Calculate pagination values
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        offset = (page - 1) * per_page

        # Execute query with pagination
        pages = (
            query.order_by(CrawledPage.last_crawled_at.desc())
            .offset(offset)
            .limit(per_page)
            .all()
        )

        # Convert to dictionaries for template
        page_dicts = [p.to_dict() for p in pages]

        # Render template with pagination data
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "pages": page_dicts,
                "url": url,
                "title": title,
                "server_running": is_server_running,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "has_prev": page > 1,
                    "has_next": page < total_pages,
                },
            },
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        # Still render the template but with error message
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"Database error: {str(e)}",
                "pages": [],
                "server_running": is_server_running,
            },
        )
    finally:
        session.close()


@app.get("/api")
async def read_root():
    """API root endpoint"""
    return {"message": "Dikontenin Helper API is running"}


# Form submission handler for browser interface
@app.post("/crawl")
async def crawl_form_url(request: Request, url: str = Form(...)):
    """Crawl a URL submitted via the web form and return JSON response"""
    session = get_session()
    try:
        # Check if URL already exists in database and is still fresh
        page = get_crawled_page(url)

        if page and not should_recrawl(page.last_crawled_at):
            # URL already crawled and data is still fresh
            logger.info(
                f"URL {url} already crawled and data is still fresh. Returning cached data."
            )

            # Return JSON with cached flag and data
            return {
                "success": True,
                "cached": True,
                "message": f"URL {url} already crawled and data is still fresh.",
                "url": page.url,
                "title": page.title,
                "description": page.description,
                "content": page.content,
                "last_crawled_at": page.last_crawled_at.isoformat()
                if page.last_crawled_at
                else None,
            }

        # Create a URL request and pass to the API handler
        url_request = UrlRequest(url=url)
        result = await crawl_api_url(url_request)

        # Return JSON response with success flag
        return {
            "success": True,
            "cached": False,
            "message": "URL successfully crawled",
            "url": url,
            "title": result.get("title", ""),
            "description": result.get("description", ""),
            "content": result.get("content", ""),
        }
    except Exception as e:
        # Handle errors and return error message as JSON
        logger.error(f"Error crawling URL: {str(e)}")
        return {"success": False, "message": f"Error crawling URL: {str(e)}"}
    finally:
        session.close()


@app.post("/api/crawl", response_model=CrawlResponse)
async def crawl_api_url(request: UrlRequest):
    """Crawl a URL and return the processed content"""
    url = str(request.url)

    try:
        # Check if URL is already crawled and still fresh
        if not should_recrawl(url):
            logger.info(
                f"URL {url} already crawled and data is still fresh. Returning cached data."
            )
            cached_data = get_crawled_page(url)
            if cached_data:
                return {
                    **cached_data,
                    "success": True,
                    "message": "Retrieved from cache",
                }

        # Crawl URL
        logger.info(f"Crawling URL: {url}")
        crawled_data = crawler.crawl_url(url)

        if not crawled_data:
            raise HTTPException(status_code=500, detail="Failed to crawl URL")

        # Process the page
        processed_data = HtmlCleaner.process_page(crawled_data)

        if not processed_data:
            raise HTTPException(
                status_code=500, detail="Failed to process page content"
            )

        # Save to database
        save_crawled_page(
            url=processed_data["url"],
            title=processed_data["title"],
            description=processed_data["description"],
            content=processed_data["content"],
            html=processed_data["html"],
        )

        # Return response
        return {
            "url": processed_data["url"],
            "title": processed_data["title"],
            "description": processed_data["description"],
            "content": processed_data["content"],
            "success": True,
            "message": "Successfully crawled and processed URL",
        }

    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "url": url,
                "title": "",
                "description": "",
                "content": "",
                "success": False,
                "message": f"Error: {str(e)}",
            },
        )


@app.get("/api/status")
async def get_status():
    """Get the status of the API"""
    try:
        return {
            "status": "ok",
            "message": "API is running",
            "server_running": is_server_running,
        }
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return JSONResponse(
            status_code=500, content={"status": "error", "message": f"Error: {str(e)}"}
        )


@app.get("/api/pages")
async def get_pages(url: str = None, title: str = None):
    """Get all crawled pages with optional filtering"""
    session = get_session()
    try:
        query = session.query(CrawledPage)

        # Apply filters if provided
        if url:
            query = query.filter(CrawledPage.url.ilike(f"%{url}%"))
        if title:
            query = query.filter(CrawledPage.title.ilike(f"%{title}%"))

        # Get results
        pages = query.order_by(CrawledPage.last_crawled_at.desc()).all()
        results = [p.to_dict() for p in pages]

        return {"success": True, "count": len(results), "pages": results}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Database error: {str(e)}"},
        )
    finally:
        session.close()


# Get clean JSON data for specified page IDs
@app.post("/api/get-clean-json")
async def get_clean_json(request: PageIdsRequest):
    """
    Get clean, normalized JSON data for the specified page IDs.
    This endpoint retrieves pages by their IDs, cleans the content,
    and returns properly formatted JSON.
    """
    try:
        # Initialize result list
        result = []

        # Get database session
        session = get_session()

        # Query database for requested pages
        for page_id in request.ids:
            page = session.query(CrawledPage).filter(CrawledPage.id == page_id).first()

            if page:
                # Convert to dictionary (without HTML)
                page_data = {
                    "url": page.url,
                    "title": page.title,
                    "description": page.description,
                    "content": page.content.strip() if page.content else "",
                }

                # Clean and normalize the content
                if page_data["content"]:
                    # Remove excessive whitespace
                    page_data["content"] = " ".join(page_data["content"].split())

                result.append(page_data)

        # Close session
        session.close()

        # Return clean JSON data
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error getting clean JSON data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error getting data: {str(e)}"},
        )


# API endpoint to close Chrome and clean up resources
@app.get("/api/shutdown")
async def api_shutdown():
    """API endpoint to close Chrome and return success status"""
    try:
        logger.info("Shutdown request received, closing browser...")
        crawler.close_browser()
        return {"success": True, "message": "Browser and resources closed successfully"}
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        return {"success": False, "message": f"Error during shutdown: {str(e)}"}


# Handle application shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when shutting down"""
    logger.info("Shutting down application, closing browser...")
    crawler.close_browser()
    logger.info("API shutting down, resources cleaned up.")
