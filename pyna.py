import requests
import random
import asyncio
from nltk.chat.util import Chat, reflections
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import sys
import json

data = requests.get("https://billing.hutchisonports.com.mx/AppService/public/terminals").json()


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
    [r'(número|numero|telefono|teléfono)', [f"helpnumber"]]
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
                tasksKey.append(print_patter(patter))
            await asyncio.gather(*tasksKey)
        else:
            print(json.dumps({"response": "Para poder apoyarte, dime el nombre y el dato que deseas saber"}))
            
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