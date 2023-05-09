import requests
from bs4 import BeautifulSoup
import pandas as pd

players = 10000
url = f"https://www.yottachess.com/morePlayers?players={players}"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'stable'})
    rows = table.find_all('tr')

    data = []
    for row in rows:
        columns = row.find_all('td')
        if len(columns) > 0:
            rank = columns[0].text.strip()
            name = columns[1].text.strip()
            rating = columns[2].text.strip()
            country_img = columns[3].find('img')
            country = " ".join(country_img['alt'].split()[1:]).upper() if country_img else ''
            elo_classical = columns[4].text.strip()
            elo_rapid = columns[5].text.strip()
            elo_blitz = columns[6].text.strip()
            year = columns[7].text.strip()
            games = columns[8].text.strip()
            data.append([rank, name, rating, country, elo_classical, elo_rapid, elo_blitz, year, games])
            
    # Create a pandas dataframe
    df = pd.DataFrame(data, columns=["Rank", "Name", "Rating", "Country", "Elo Classical", "Elo Rapid", "Elo Blitz", "Year", "Games"])
    
    # Save the dataframe to CSV
    df.to_csv("players.csv", index=False)
    
    print("Data saved to players.csv")
    
else:
    print(f"Error: {response.status_code}")
