import requests
def exchange(totle:int):
    url="https://v6.exchangerate-api.com/v6/a8337073c983fa5ad505f498/latest/USD"
    response=requests.get(url)
    data=response.json()
    convert_data=data['conversion_rates'].get('EGP')
    money_byegp=totle*convert_data
    return money_byegp
print(exchange(100))

    

url = "https://bantayga.wtf/register"

# البيانات التي سيتم إرسالها في طلب POST
data = {
    "first_name": "dsfdsa",
    "username": "dsaffdstr",
    "email": "ahmeoon1234@gmail.com",
    "password": "ahmeoon1234@gmail.com",
    "password2": "ahmeoon1234@gmail.com",
    "country": "Egypt",
    "currence": "Egp"
}

# إرسال طلب POST
response = requests.post(url, json=data)

# طباعة استجابة السيرفر
print("Status Code:", response.status_code)

try:
    # محاولة تحليل الاستجابة كـ JSON
    response_json = response.json()
    print("Response Body:", response_json)
except requests.exceptions.JSONDecodeError:
    # إذا فشل التحليل، طباعة نص الاستجابة
    print("Response Body (not JSON):", response.text)