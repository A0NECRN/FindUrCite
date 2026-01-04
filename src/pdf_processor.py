import os
import requests
import fitz  # PyMuPDF
import hashlib

class PDFProcessor:
    def __init__(self, download_dir="downloads"):
        self.set_download_dir(download_dir)

    def set_download_dir(self, new_dir):
        """Update the download directory."""
        self.download_dir = new_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def _get_filename(self, url):
        """Generate a filename from the URL hash."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.download_dir, f"{url_hash}.pdf")

    def download_pdf(self, url):
        """
        Download PDF from a URL.
        Returns the local file path if successful, None otherwise.
        """
        if not url:
            return None
            
        # Handle arXiv abstract URLs -> PDF URLs
        if "arxiv.org/abs/" in url:
            url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")
            if not url.endswith(".pdf"):
                url += ".pdf"
        
        local_path = self._get_filename(url)
        
        # Return existing file if already downloaded
        if os.path.exists(local_path):
            return local_path

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return local_path
            else:
                print(f"Failed to download PDF from {url}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading PDF from {url}: {e}")
            return None

    def extract_text(self, pdf_path, max_pages=None):
        """
        Extract text from a local PDF file.
        max_pages: Limit the number of pages to read (e.g., first 10 pages).
        """
        if not pdf_path or not os.path.exists(pdf_path):
            return ""

        try:
            doc = fitz.open(pdf_path)
            text_content = []
            
            num_pages = len(doc)
            if max_pages:
                num_pages = min(num_pages, max_pages)

            for i in range(num_pages):
                page = doc.load_page(i)
                text = page.get_text()
                text_content.append(f"--- Page {i+1} ---\n{text}")
            
            return "\n".join(text_content)
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return ""
        finally:
            if 'doc' in locals():
                doc.close()

    def clean_up(self):
        """Remove all downloaded files."""
        if os.path.exists(self.download_dir):
            for f in os.listdir(self.download_dir):
                os.remove(os.path.join(self.download_dir, f))
