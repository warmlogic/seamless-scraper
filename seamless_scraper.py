'''
Web scraper to pull restaurants and addresses from Seamless.

Seamless uses JavaScript, so we need Selenium. Example:
https://medium.freecodecamp.org/better-web-scraping-in-python-with-selenium-beautiful-soup-and-pandas-d6390592e251

Requirements:

1. pip install pandas selenium

2. FireFox Driver:
- Option 1: Install Homebrew and run this command on macOS to use Selenium as FireFox: brew install geckodriver
- Option 2: Download Firefox macOS geckodriver 0.24.0 and put in PATH https://github.com/mozilla/geckodriver/releases

Then open the Terminal and run this script: python seamless_scraper.py
'''

import json
import pandas as pd

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

# constants
base_url_first = 'https://www.seamless.com/browse/ny-nyc'
base_url_page = f'{base_url_first}?pageNum='
MAX_PAGES = 527


def add_restaurants_dict(names, addresses, restaurants_dict=None):
    if restaurants_dict is None:
        restaurants_dict = {}
    for name, address in zip(names, addresses):
        try:
            restaurants_dict[name.text] = address.text
        except KeyError as e:
            continue
    return restaurants_dict


def add_restaurants_list(names, addresses, restaurants_list=None):
    if restaurants_list is None:
        restaurants_list = []
    for name, address in zip(names, addresses):
        restaurants_list.append({
            'name': name.text,
            'address': address.text,
        })
    return restaurants_list


if __name__ == '__main__':
    # create a new Firefox session
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)

    # initialize
    restaurants_list = []
    restaurants_dict = {}
    counter = 0
    failed_pages_list = []

    while True and counter < MAX_PAGES:
        counter += 1

        if counter == 1:
            driver.get(base_url_first)
        else:
            driver.get(f'{base_url_page}{counter}')

        names = driver.find_elements_by_xpath("//h5[contains(@class, 'u-text-ellipsis')]")

        # # alternatives
        # names = driver.find_elements_by_xpath("//div[contains(@class, 's-card-title undefined')]")
        # addresses = driver.find_elements_by_class_name('restaurantCard-search-address')

        if len(names) > 0:
            addresses = driver.find_elements_by_xpath("//div[contains(@class, 'restaurantCard-search-address')]")
            print(f'Page counter {counter}, found {len(names)} restaurant names, {len(addresses)} addresses')

            if len(names) == len(addresses):
                restaurants_list = add_restaurants_list(names, addresses, restaurants_list)
                restaurants_dict = add_restaurants_dict(names, addresses, restaurants_dict)
                print(f'\tTotal restaurants found so far: {len(restaurants_list)}')
            else:
                print(f'\t!!! Page failed. Different number of restaurant names and addresses.')
                failed_pages_list.append({
                    'counter': counter,
                    'reason': f'different lengths: {len(names)} names {len(addresses)} addresses',
                })
                continue
        else:
            print(f'!!! Page failed. Page counter {counter}, found {len(names)} restaurant names.')
            failed_pages_list.append({
                'counter': counter,
                'reason': f'{len(names)} names',
            })

    # end the Selenium browser session
    driver.quit()

    # if storing as list of dictionaries
    print(f'Total number of restaurants (list): {len(restaurants_list)}')
    if len(restaurants_list) > 0:
        df_rest = pd.DataFrame(data=restaurants_list)
        df_rest.to_csv('restaurants_nyc.csv', index=False)

    # if storing as one dictionary
    print(f'Total number of restaurants (dict): {len(restaurants_dict)}')
    if len(restaurants_dict) > 0:
        with open('restaurants_nyc.json', 'w') as fp:
            json.dump(restaurants_dict, fp)
    else:
        print('No restaurants found')

    # failed pages (list of dictionaries)
    print(f'Total number of failed pages: {len(failed_pages_list)}')
    if len(failed_pages_list) > 0:
        df_fail = pd.DataFrame(data=failed_pages_list)
        df_fail.to_csv('failed_pages.csv', index=False)
    else:
        print('No failed pages')
