import requests
import random
import asyncio
from nltk.chat.util import Chat, reflections
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
import json
import os
import re 



data = requests.get("https://billing.hutchisonports.com.mx/AppService/public/terminals")

if data.status_code == 200:
    with open('terminals.json', 'w') as file:
        file.write(data.text)
else:
    if os.path.exists('terminals.json'):
        with open('terminals.json', 'r') as file:
            data = json.load(file)
    else :
        print("Una disculpa, datos de la página no disponibles por el momento")
        sys.exit()

data = data.json()

dataFAQ = requests.get("https://billing.hutchisonports.com.mx/AppService/public/faqinfolist")

if dataFAQ.status_code == 200:
    with open('FAQ.json', 'w') as file:
        file.write(dataFAQ.text)
else:
    if os.path.exists('FAQ.json'):
        with open('FAQ.json', 'r') as file:
            dataFAQ = json.load(file)
    else :
        print("Una disculpa, datos de la página no disponibles por el momento")
        sys.exit()

dataFAQ = dataFAQ.json()

      


stop_words = set(stopwords.words('spanish'))

possible_responses = {
    "address" :  [
        'La dirección de {0} es {1}',
        'La ubicación de {0} es {1}',
        'El domicilio de {0} es {1}'
    ],
    "helpnumber" :  [
        'Puedes contactar a {0} con el número {1}',
        'Puedes contactar a {0} con el teléfono {1}',
        'El número de {0} es {1}',
        'El teléfono de {0} es {1}'
    ],
    "helpmail" :  [
        'Puedes contactar a {0} con el email {1}',
        'Puedes contactar a {0} con el correo electrónico {1}',
        'El correo electrónico de {0} es {1}',
        'El email de {0} es {1}'
    ],
    "helpname" :  [
        'El nombre oficial de {0} es {1}',
        '{0} se le conoce como {1}'
    ],
    "lat" :  [
        'La latitud de {0} es {1}',
        '{1} Es la latitud de {0}'
    ],
    "long" :  [
        'La longitud de {0} es {1}',
        '{1} Es la longitud de {0}'
    ]
}

# Extraer información relevante para el chatbot
locations = {place['name'].lower(): place for place in data['Body']}

def getPatter(patter):
    return random.choice(possible_responses[patter])



# Definir patrones y respuestas para el chatbot
patterns = [
    [r'ayuda', ['Puedo ayudarte a consultar datos de HutchisonPorts ¿En qué lugar necesitas asistencia?']],
    [r'(dirección|direccion|ubicación|ubicacion)', [f"address"]],
    [r'(número|numero|telefono|teléfono)', [f"helpnumber"]],
    [r'(email|correo)', [f"helpmail"]],
    [r'latitud', [f"lat"]],
    [r'longitud', [f"long"]],
]

patterns += [
    [r'Hola|Hi|Hey', ['¡Hola! ¿Cómo puedo ayudarte hoy?']],
    [r'Adiós|Bye|Hasta luego|Chao', ['¡Adiós! Que tengas un excelente día.']],
    [r'(buenas|Buenas) noches', ['¡Buenas noches! ¿Necesitas algo más antes de dormir?']],
    [r'(buenos|Buenos|buenas|Buenas) (dias|días|tardes)', ['¡Buenos %2! ¿En qué puedo asistirte hoy?','¡Buenas %2! ¿Cómo puedo ayudarte?']],
]




respPatter = []
respKeys = []

chat = Chat(patterns, reflections)

async def async_patter(toke):
    tasks = []
    resp = chat.respond(toke)
    if resp:
        respPatter.append(resp)
    else:
        tasks.append(async_data(toke))
    await asyncio.gather(*tasks)


async def async_data(token):
    for key, value in locations.items():
        if token in key and token not in "hutchison ports":
            if key not in respKeys:
                respKeys.append(key)
            break



async def print_patter(patter):
    for key in respKeys:
        response = getPatter(patter).format(key, locations[key][patter])
        print(json.dumps({"response": response}))
        
        


# Crear el chatbot
async def chatbot(user_input):
    tasks = []
    
    flag = True
    
    tokens = word_tokenize(user_input.lower())
    tokens_filtrados = [word for word in tokens if word not in stop_words]
    
    if len(tokens_filtrados)>0:
        for toke in tokens_filtrados:
            tasks.append(async_patter(toke))
    
    await asyncio.gather(*tasks)
        
        
        

    if len(respPatter)>0:
        flag = False
        
        if len(respKeys) > 0:
            tasksKey = []
            for patter in respPatter:
                if len(patter.split())==1:
                    tasksKey.append(print_patter(patter))
                else:
                    print(json.dumps({"response": patter}))
            await asyncio.gather(*tasksKey)
        else:
            if "{0}" not in respPatter[0]:
                print(json.dumps({"response": "Para poder apoyarte, dime el nombre y el dato que deseas saber"}))
            else :
                print(json.dumps({"response": respPatter[0]}))
            
    if flag:
        
        resp = chat.respond(user_input.lower())
        if resp:
            print(json.dumps({"response": resp}))
        else:
            print(json.dumps({"response": "No he entendido tu pregunta"}))



# Ejecutar el chatbot
if __name__ == "__main__":
    
    sys.stdin.reconfigure(encoding='utf-8')
    for line in sys.stdin:
        input_data = json.loads(line.strip())
        prompt = input_data.get("prompt")
        #chatbot(prompt)
        asyncio.run(chatbot(prompt))

