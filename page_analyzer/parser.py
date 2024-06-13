from bs4 import BeautifulSoup


def parse_page(page):
    parsed_data = {}
    soup = BeautifulSoup(page, 'html.parser')
    h1 = soup.find('h1')
    parsed_data['h1'] = h1.get_text().strip() if h1 else ''
    title = soup.find('title')
    parsed_data['title'] = title.get_text().strip() if title else ''
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        parsed_data['description'] = meta_description.get('content', '').strip()
    else:
        parsed_data['description'] = ''
    return parsed_data
