import requests, json, nltk, pattern.en
from nltk import tree
from pprint import pprint
while True:
    question = raw_input('Enter the question: \n')
    if question == "close":
        break

    t = pattern.en.tag(question)
    # grammar = r"""NP: {<JJ.*>+$} """
    # grammar = r"""NP: {<JJ.*>+<NN.*>+}
    #             # NP_A: {<NN.*>+<IN>*<JJ.*>*}
    #             # NP_S: {<NN.*>?}"""

    grammar = r"""NP: {<JJ.*>+<NN.*>+}
            NP_A: {<NN.*>+<IN>*<JJ.*>*}"""

    np_parser = nltk.RegexpParser(grammar)
    np_tree = np_parser.parse(t)
    #pprint (np_tree)
    q_noun = []
    for i in np_tree:
        #to get all the Noun Phrases to q_noun
        NPs=""
        #print type(i) #shows the type of all nodes
        if type(i) == tree.Tree:
              for k in i:
                if NPs=="":
                    NPs=k[0]
                else:
                    NPs=NPs+" "+k[0]
                    q_noun.append(NPs)

    conjuction = ["of","in","as","if","as if","even","than","that","until","and","but","or","nor","for","yet","so"]
    for idx,i in enumerate(q_noun):
        #removes conjunction and replaces it with " " in btwn words for searching
        q_noun[idx] = q_noun[idx].lower()
        for j in conjuction:
            q_noun[idx]=str(q_noun[idx]).replace(j+" "," ")
            q_noun[idx]=str(q_noun[idx]).replace(" "+j," ")

    print q_noun
    if len(q_noun) == 1:

        search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
            'wbsearchentities&search='+q_noun[0]+'&language=en&format=json')
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
            'wbsearchentities&search='+q_noun[0]+'&language=en&format=json&type=property')
        search_json = search_resp.json()

        for p in search_json['search']:
            property_ids.append(p['id'])
        #print(property_ids)
        answer_fetched = False
        answer = ''
        search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
            'wbsearchentities&search='+q_noun[1]+'&language=en&format=json')
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
                    #pprint(property_value)
                    property_value_id = property_value['mainsnak']['datavalue']['value']['id']
                    answer_resp = requests.get('https://www.wikidata.org/w/api.php?'
                        'action=wbgetentities&ids='+property_value_id+'&format=json&languages=en')
                    answer_json = answer_resp.json()
                    answer = answer_json['entities'][property_value_id]['labels']['en']['value']
                    descr=answer_json['entities'][property_value_id]['descriptions']['en']['value']
                    answer_fetched = True
                    break
            if answer_fetched:
                break

        if answer_fetched:
            print 'Answer : ', answer
            #print 'Answer : ', json.dumps(answer) #to remove u from answer



        else:
            print'Cant find the answer'




# (qas-env) C:\Users\Achi\Desktop\nltk_apps\qbot>python test.py
# Enter the question:
# who is the author of harry potter?
# Answer :  J. K. Rowling
# Enter the question:
