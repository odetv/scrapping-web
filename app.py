import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import urljoin

# Daftar URL yang akan di-scrape
urls_to_scrape = [
    "https://undiksha.ac.id/tentang-undiksha/",
    "https://undiksha.ac.id/pmb/"
]

def fetch_page(url):
    response = requests.get(url)
    return response.text

def extract_links_and_text(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    text = soup.get_text(separator='\n', strip=True)
    
    # Mengambil semua tautan
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith(base_url):  # Hanya ambil link yang menuju ke domain yang sama
            links.append(full_url)
    
    return text, links

def clean_text(text):
    text = text.replace('\u200b', '')  # Menghapus karakter invisible
    text = text.replace('\n', ' ')  # Mengganti newline dengan spasi
    text = text.replace('\r', '')  # Menghapus carriage return
    text = text.replace('  ', ' ')  # Menghapus spasi ganda
    return text

def save_text_and_links_to_pdf(texts_and_links, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 40
    max_width = width - 2 * margin
    line_height = 14
    y_position = height - margin

    def draw_text(canvas, text, x, y, max_width):
        text_lines = []
        words = text.split(' ')
        line = ''
        for word in words:
            test_line = f"{line} {word}".strip()
            width = canvas.stringWidth(test_line, "Helvetica", 12)
            if width <= max_width:
                line = test_line
            else:
                text_lines.append(line)
                line = word
        if line:
            text_lines.append(line)
        return text_lines

    for text, links in texts_and_links:
        cleaned_text = clean_text(text)
        lines = draw_text(c, cleaned_text, margin, y_position, max_width)
        for line in lines:
            c.drawString(margin, y_position, line)
            y_position -= line_height
            if y_position < margin:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - margin

        # Menambahkan tautan
        if links:
            c.drawString(margin, y_position, "Links found:")
            y_position -= line_height
            for link in links:
                link_line = f"- {link}"
                c.drawString(margin, y_position, link_line)
                y_position -= line_height
                if y_position < margin:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = height - margin

    c.save()

# Mengambil konten dari URL yang ditentukan
texts_and_links = []
for url in urls_to_scrape:
    html_content = fetch_page(url)
    page_text, page_links = extract_links_and_text(html_content, url)
    texts_and_links.append((page_text, page_links))

    # Mengambil konten dari halaman yang ditautkan
    for link in page_links:
        page_html = fetch_page(link)
        linked_page_text, linked_page_links = extract_links_and_text(page_html, url)
        texts_and_links.append((linked_page_text, linked_page_links))

# Menyimpan hasil scrape ke dalam file PDF
pdf_filename = "output.pdf"
save_text_and_links_to_pdf(texts_and_links, pdf_filename)

print(f"Scraping selesai. Hasil disimpan di {pdf_filename}")
