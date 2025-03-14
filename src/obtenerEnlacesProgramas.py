import requests
from bs4 import BeautifulSoup


def obtener_enlaces_programas(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        programas = []

        header_tag = soup.find('header', class_='page-header')
        if header_tag:
            h1_tag = header_tag.find('h1')
            nombre_programa = h1_tag.text.strip() if h1_tag else None

        sections = soup.find_all('section')
        for section in sections:
            h1_tag = section.find('h1')
            title = h1_tag.text.strip() if h1_tag else None

            if title:
                escuchar_link_tag = section.find('a', href=True, string=lambda text: text and "Escuchar" in text)
                escuchar_link = f"https://www.twr360.org{escuchar_link_tag['href']}" if escuchar_link_tag else None

                if escuchar_link:
                    programas.append(
                        {"titulo": title, "escuchar_link": escuchar_link, "nombre_programa": nombre_programa})

        return programas
    else:
        print(f"Error al acceder a la página: {response.status_code}")
        return []
