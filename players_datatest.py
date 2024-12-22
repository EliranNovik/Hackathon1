import requests

url = "https://nba-api-free-data.p.rapidapi.com/nba-player-listing/v1/data"

querystring = {"id":"22"}

headers = {
	"x-rapidapi-key": "ae0694e32amshc4b1e2887309c8bp19703fjsnd35e15ab28f1",
	"x-rapidapi-host": "nba-api-free-data.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())