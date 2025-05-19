import re
from bs4 import BeautifulSoup
from loguru import logger
from sacremoses import MosesPunctNormalizer

mpn = MosesPunctNormalizer()


def normalize_text(text):
    normalized_text = mpn.normalize(text)
    change_double_quote = normalized_text.replace('"', "'")
    return change_double_quote


class HtmlCleaner:
    """Class to clean and extract content from HTML"""

    @staticmethod
    def clean_html(html):
        """Clean HTML and extract readable content"""
        try:
            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for script_or_style in soup(["script", "style", "iframe", "noscript"]):
                script_or_style.decompose()

            # Remove hidden elements
            for hidden in soup.find_all(
                attrs={"style": re.compile(r"display:\s*none")}
            ):
                hidden.decompose()

            # Remove header, footer, nav and sidebar elements
            for nav in soup.find_all(["header", "footer", "nav", "aside"]):
                nav.decompose()

            # Remove comment elements
            for comment in soup.find_all(
                text=lambda text: isinstance(text, str)
                and text.strip().startswith("<!--")
            ):
                comment.extract()

            # Get main content from article, main or div containers
            main_content = ""
            content_elements = soup.find_all(
                ["article", "main", "div.content", "div.post", "div.entry"]
            )

            if content_elements:
                # Use the largest content element
                largest_element = max(content_elements, key=lambda x: len(str(x)))
                main_content = largest_element.get_text(separator=" ", strip=True)
            else:
                # Fallback to body content
                main_content = (
                    soup.body.get_text(separator=" ", strip=True) if soup.body else ""
                )

            # Clean up the text
            # Replace multiple spaces with a single space
            main_content = re.sub(r"\s+", " ", main_content)
            # Remove any remaining HTML tags
            main_content = re.sub(r"<[^>]+>", "", main_content)

            return main_content
        except Exception as e:
            logger.error(f"Error cleaning HTML: {str(e)}")
            return ""

    @staticmethod
    def extract_metadata(html):
        """Extract metadata from HTML (title, description, etc.)"""
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string

            # Extract description
            description = ""
            # Try meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                description = meta_desc.get("content")
            else:
                # Try Open Graph description
                og_desc = soup.find("meta", attrs={"property": "og:description"})
                if og_desc and og_desc.get("content"):
                    description = og_desc.get("content")

            return {"title": title, "description": description}
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {"title": "", "description": ""}

    @staticmethod
    def process_page(crawled_data):
        """Process crawled page data and extract useful information"""
        try:
            html = crawled_data.get("html", "")

            # Extract content
            content = HtmlCleaner.clean_html(html)

            # Extract metadata if not already present
            metadata = {}
            if not crawled_data.get("title") or not crawled_data.get("description"):
                metadata = HtmlCleaner.extract_metadata(html)

            # Merge data
            result = {
                "url": crawled_data.get("url", ""),
                "title": normalize_text(
                    crawled_data.get("title") or metadata.get("title", "")
                ),
                "description": normalize_text(
                    crawled_data.get("description") or metadata.get("description", "")
                ),
                "content": normalize_text(content),
                "html": html,
            }

            return result
        except Exception as e:
            logger.error(f"Error processing page: {str(e)}")
            return None
