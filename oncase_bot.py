import json
import pandas as pd
import os
import requests

from flask import Flask, request, Response

## constants
TOKEN = '5927225837:AAE6gF_bqErAUkkSwJlLgGKsJ_I_52MfGHE'
#
## bot info
#https://api.telegram.org/bot5927225837:AAE6gF_bqErAUkkSwJlLgGKsJ_I_52MfGHE/getMe
#
## get updates
#https://api.telegram.org/bot5927225837:AAE6gF_bqErAUkkSwJlLgGKsJ_I_52MfGHE/getUpdates
#
## Webhook
#https://api.telegram.org/bot5927225837:AAE6gF_bqErAUkkSwJlLgGKsJ_I_52MfGHE/setWebhook?url=https://rossmann-bot-e3t3.onrender.com
#
## send message
#https://api.telegram.org/bot5927225837:AAE6gF_bqErAUkkSwJlLgGKsJ_I_52MfGHE/sendMessage?chat_id=1633133118&text=Hi Zangs

def send_message(chat_id, text):
    # send message
    url = 'https://api.telegram.org/bot{}/'.format(TOKEN)
    url = url + 'sendMessage?chat_id={}'.format(chat_id)
    r = requests.post(url, json={'text': text})
    print('Status Code: {}'.format(r.status_code))

    return None 

def load_dataset(product_id):

    # loading test dataset
    df_test = pd.read_csv('datasets/time_series_data.csv')
    df_test['nota_data_emissao'] =  pd.to_datetime(df_test['nota_data_emissao'], format='%Y%m%d')
    df_test = df_test[df_test['nota_data_emissao'] >= '2021-09-02']

    # choose product for prediction
    df_test = df_test[df_test['produto_descricao'] == product_id]

    if not df_test.empty:
        
        # convert Dataframe to json
        data = json.dumps(df_test.to_dict(orient='records'), default = str)
    else:
        data = 'error'

    return data

def predict(data):
    # API Call
    url = 'https://oncase-prediction.onrender.com/oncase/predict'
    header = {'Content-type': 'application/json' }
    data = data
    r = requests.post(url, data = data, headers = header)
    print('Status Code {}'.format(r.status_code))

    d1 = pd.DataFrame(r.json(), columns = r.json()[0].keys())

    return d1

def parse_message(message):
    chat_id = message['message']['chat']['id']
    product_id = message['message']['text']

    product_id = product_id.replace('/', '')

    try:
        product_id = str(product_id)
    
    except ValueError:
        
        product_id = 'error'
  
    return chat_id, product_id

# API initialize
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.get_json()

        chat_id, product_id = parse_message(message)

        if store_id != 'error':
            # loading data
            data = load_dataset(product_id)
            
            if data != 'error':
                # predict
                d1 = predict(data)

                # calculation
                d2 = d1[['produto_descricao', 'prediction']].groupby('produto_descricao').sum().reset_index()
                
                # send message
                msg = 'The Product ID {} demand prediction is {:,.0f} in the next 4 weeks'.format(d2.loc[i, 'produto_descricao'], d2.loc[i, 'prediction'])

                send_message(chat_id, msg)
                return Response('Ok', status = 200)
                
            else:
                send_message(chat_id, 'Unavailable Product')
                return Response('Ok', status = 200)
        else:
            send_message(chat_id, 'Invalid Product ID')
            return Response('Ok', status = 200)
    else:
        return '<h1> Oncase Telegram BOT </h1>'

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port = port)
