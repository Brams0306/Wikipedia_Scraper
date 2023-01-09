import requests
from bs4 import BeautifulSoup
from requests import Session
import bs4
import re
from functools import lru_cache
from urllib3.exceptions import NewConnectionError
import json
request_result = requests.get('https://country-leaders.onrender.com/status')
print(request_result.status_code)
wiki_page = BeautifulSoup(request_result.text,"html.parser")
print(wiki_page.prettify())
cookie_url = "https://country-leaders.onrender.com/cookie"
req = requests.get(cookie_url)
cookies = req.cookies
print(cookies)
url = "https://country-leaders.onrender.com/"
country_url = "https://country-leaders.onrender.com/countries"
req2 = requests.get(country_url, cookies=cookies)
countries = req2.json()
print(req.status_code, countries)
leaders_url = "http://country-leaders.onrender.com/leaders"
parameters = {'country': countries[0]} 
req3 = requests.get(leaders_url, cookies=cookies, params=parameters)
print(req3.status_code)
print(req3.json())
def get_leaders():

    cookie_url = "http://country-leaders.onrender.com/cookie"
    countries_url = "http://country-leaders.onrender.com/countries"
    leaders_url = "http://country-leaders.onrender.com/leaders"
    req = requests.get(cookie_url)
    cookies = req.cookies
    req2 = requests.get(countries_url, cookies=cookies)
    countries = req2.json()
    
    leaders_per_country = {}
    
    for country in countries:
        parameters = {'country': country}
        req3 = requests.get(leaders_url, cookies=cookies, params=parameters)
        leaders_per_country[country] = req3.json()
    
    return leaders_per_country

leaders = get_leaders()
print(leaders)

def get_first_paragraph(wikipedia_url):
    req4 = requests.get(wikipedia_url)
    soup = bs4.BeautifulSoup(req4.text, "html.parser")
    paragraphs = soup.find_all('p')
    for paragraph in paragraphs:
        if paragraph.find_all('b'):
            #removing parenthese and what is between them
            first_paragraph = re.sub(" \([^()]+\)", '', paragraph.text)
            #removing url link
            first_paragraph = re.sub("(?P<url>https?://[^\s]+)", '', first_paragraph)
            break
    return first_paragraph

macron_url = 'https://fr.wikipedia.org/wiki/Emmanuel_Macron'
putin_url = "https://ru.wikipedia.org/wiki/%D0%9F%D1%83%D1%82%D0%B8%D0%BD,_%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B8%D1%87"

print(get_first_paragraph(macron_url))
print(get_first_paragraph(putin_url))


# Use lru_cache to cache the results of get_first_paragraph
@lru_cache(maxsize=None)
def get_first_paragraph(wikipedia_url):
    # Make a GET request to the provided url
    response = requests.get(wikipedia_url)

    # If the status code is not 200 (OK), return an empty string
    if response.status_code != 200:
        return ""

    # Get the HTML content of the page
    html_content = response.text

    # Find the first paragraph element in the HTML content
    paragraph_start = html_content.find("<p>")
    paragraph_end = html_content.find("</p>", paragraph_start)
    paragraph_html = html_content[paragraph_start:paragraph_end]

    # Strip the HTML tags from the paragraph and return the result
    return paragraph_html.replace("<p>", "").replace("</p>", "")

def get_leaders():
    leaders_per_country = {}

    # Make a GET request to the API to get the list of leaders
    response = requests.get("https://country-leaders.onrender.com/leaders")
    

    # If the status code is not 200 (OK), return an empty dictionary
    if response.status_code != 200:
        return {}

    # Get the list of leaders from the response
    leaders = response.json()

    # Create a session to use for all requests to Wikipedia
    session = requests.Session()

    # Loop through the leaders and get the first paragraph of their Wikipedia page
    for leader in leaders:
        # Get the Wikipedia url for the leader
        wikipedia_url = leader["wikipedia_url"]

        # Get the first paragraph of the Wikipedia page
        first_paragraph = get_first_paragraph(wikipedia_url, session)

        # Update the leader's dictionary with the first paragraph
        leader["first_paragraph"] = first_paragraph

        # Add the leader to the leaders_per_country dictionary
        country = leader["country"]
        if country not in leaders_per_country:
            leaders_per_country[country] = []
        leaders_per_country[country].append(leader)

    return leaders_per_country

def save(leaders_per_country):
    # Convert the leaders_per_country dictionary to a JSON string
    leaders_json = json.dumps(leaders_per_country)

    # Write the JSON string to the leaders.json file
    with open("leaders.json", "w") as f:
        f.write(leaders_json)

def read():
    # Read the contents of the leaders.json file
    with open("leaders.json", "r") as f:
        leaders_json = f.read()

    # Convert the JSON string back to a dictionary
    leaders_per_country = json.loads(leaders_json)

    return leaders_per_country

# Save the leaders data to the leaders.json file
save(get_leaders())

# Read the leaders data from the leaders.json file
leaders_per_country = read()

# Print the leaders data
print(leaders_per_country)


