import requests
from bs4 import BeautifulSoup


def obtener_enlaces_programas(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al acceder a la página: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    nombre_programa = (
        soup.find("header", class_="page-header")
        .find("h1").text.strip()
        if soup.find("header", class_="page-header")
        else "Desconocido"
    )

    programas = []
    for section in soup.find_all("section"):
        h1_tag = section.find("h1")
        title = h1_tag.text.strip() if h1_tag else None

        if title:
            escuchar_link_tag = section.find("a", href=True, string=lambda text: text and "Escuchar" in text)
            if escuchar_link_tag:
                escuchar_link = f"https://www.twr360.org{escuchar_link_tag['href']}"
                programas.append({"titulo": title, "escuchar_link": escuchar_link, "nombre_programa": nombre_programa})

    return programas
