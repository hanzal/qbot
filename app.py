import requests
from textblob import TextBlob
from pprint import pprint

while True:
    question = input('Enter the question: \n')
    if question == "close":
        break
    blob = TextBlob(question)
    nouns = []
    noun_phrases=[]
    for n in blob.noun_phrases:
        noun_phrases.append(n[0])
    for i in blob.tags:
        if i[1]=='NN':
            nouns.append(i[0])

    #print(nouns)
    #print(len (nouns))
    if len(nouns) == 1:
        search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
            'wbsearchentities&search='+nouns[0]+'&language=en&format=json')
        search_json = search_resp.json()
        #print(search_json['search'][0]['description'])
        a=search_json['search'][0]['id']
        #print (a)
        entity_resp = requests.get('https://www.wikidata.org/w/api.php?'
            'action=wbgetentities&ids='+ a +'&format=json&languages=en')
        entity_json = entity_resp.json()
        #pprint(entity_json)
        print(entity_json['entities'][a]['descriptions']['en']['value'])


    else:
        property_ids = []
        search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
            'wbsearchentities&search='+nouns[0]+'&language=en&format=json&type=property')
        search_json = search_resp.json()

        for p in search_json['search']:
            property_ids.append(p['id'])
        #print(property_ids)
        answer_fetched = False
        answer = ''
        search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
            'wbsearchentities&search='+nouns[1]+'&language=en&format=json')
        search_json = search_resp.json()
        #pprint (search_json)
        for s in search_json['search']:
            entity_resp = requests.get('https://www.wikidata.org/w/api.php?'
                'action=wbgetentities&ids='+ s['id'] +'&format=json&languages=en')
            entity_json = entity_resp.json()
            #pprint(entity_json)
            for p in property_ids:
                if entity_json['entities'][s['id']]['claims'].get(p,None):
                    property_value = entity_json['entities'][s['id']]['claims'][p][0]
                    pprint(property_value)
                    property_value_id = property_value['mainsnak']['datavalue']['value']['id']
                    answer_resp = requests.get('https://www.wikidata.org/w/api.php?'
                        'action=wbgetentities&ids='+property_value_id+'&format=json&languages=en')
                    answer_json = answer_resp.json()
                    #pprint(answer_json)
                    answer = answer_json['entities'][property_value_id]['labels']['en']['value']
                    descr=answer_json['entities'][property_value_id]['descriptions']['en']['value']
                    answer_fetched = True
                    break
            if answer_fetched:
                break

        if answer_fetched:
            # print(descr)
            print('Answer : ',answer)

        else:
            print('Cant find the answer')
