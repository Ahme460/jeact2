import requests
def exchange(totle:int):
    url="https://v6.exchangerate-api.com/v6/a8337073c983fa5ad505f498/latest/USD"
    response=requests.get(url)
    data=response.json()
    convert_data=data['conversion_rates'].get('EGP')
    money_byegp=totle*convert_data
    return money_byegp
print(exchange(100))

    
    