import requests

# Where USD is the base currency you want to use
url = 'https://v6.exchangerate-api.com/v6/a8337073c983fa5ad505f498/latest/USD'

# Making our request
response = requests.get(url)
data = response.json()

# Your JSON object
print (data)