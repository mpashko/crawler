import csv
from urllib.parse import urljoin

import click
import requests
from bs4 import BeautifulSoup
from requests import PreparedRequest

BASE_URL = 'http://www.olx.ua'


def get_soup(response):
    return BeautifulSoup(response.text, 'lxml')


def get_links_on_page(page_link):
    response = requests.get(page_link)
    soup = get_soup(response)
    offers = soup.find_all('div', class_='offer-wrapper')
    links = []
    for offer in offers:
        details_tag = offer.find('a', class_='detailsLink')
        details_link = details_tag.attrs['href']
        links.append(details_link)
    return links

import json
json.loads()

def write_to_csv_file(filename, links):
    with open(filename, mode='w') as f:
        header = ['Title', 'Offer From', 'Seller', 'Condition', 'Price', 'URL']
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        with click.progressbar(links, label='Process offers') as bar:
            for link in bar:
                process_offer(writer, link)


def process_offer(writer, offer_link):
    response = requests.get(offer_link)
    soup = get_soup(response)

    title_tag = soup.find('h1')
    title = title_tag.text.strip()

    price_tag = soup.find('strong', class_='pricelabel__value')

    offer_type_tags = soup.find_all('a', class_='offer-details__param')
    offer_from_tag, condition_tag = None, None
    for type_tag in offer_type_tags:
        details_item_tag = type_tag.find('span', class_='offer-details__name')
        details_item = details_item_tag.text
        if details_item == 'Объявление от':
            offer_from_tag = type_tag.find('strong', class_='offer-details__value')

        if details_item == 'Состояние':
            condition_tag = type_tag.find('strong', class_='offer-details__value')

    seller_tag = soup.find('div', class_='userbox__seller-name')

    writer.writerow({
        'Title': title,
        # offer_from_tag.text if offer_from_tag is not None else None
        'Offer From': offer_from_tag and offer_from_tag.text,
        'Seller': seller_tag.text,
        'Condition': condition_tag and condition_tag.text,
        'Price': price_tag.text,
        'URL': offer_link
    })


@click.command()
@click.argument('query', type=str)
@click.argument('pages', type=int)
@click.option('-city', type=str, default='kiev')
def main(query, pages, city):
    city_url = urljoin(BASE_URL, city + '/')
    url = urljoin(city_url, f'q-{query}')

    response = requests.get(url)
    soup = get_soup(response)
    electronics_tag = soup.find('a', attrs={'data-id': '37'})
    electronics_link = electronics_tag.attrs['href']

    response = requests.get(electronics_link)
    soup = get_soup(response)
    accessories_tag = soup.find('a', attrs={'data-id': '44'})
    accessories_link = accessories_tag.attrs['href']

    response = requests.get(accessories_link)
    soup = get_soup(response)
    phones_tag = soup.find('a', attrs={'data-id': '85'})
    phones_link = phones_tag.attrs['href']

    links = []
    req = PreparedRequest()

    for page_number in range(pages):
        req.prepare_url(phones_link, params={'page': page_number + 1})
        page_links = get_links_on_page(req.url)
        links.extend(page_links)

    filename = f'{query}.csv'
    write_to_csv_file(filename, links)


if __name__ == '__main__':
    main()
