import requests
import nltk, pattern.en
#from pprint import pprint

while True:
    question = raw_input('Enter the question: \n')
    if question == "close":
        break


    t=pattern.en.tag(question)
    grammar = r"""NP: {<JJ.*>+<NN.*>+}
                  NP: {<NNP>+}
                  NP: {<NN.*>+<IN>*<JJ.*>*}"""
    #grammar = [r"""NP: {<JJ.*>*<NNS><IN>+<DT>*<NN.*>+}""",r"""NP: {<JJ.*>*<IN>*<NN.*>+}
	 #          {<NN.*><IN>+<JJ.*>+}
	  #          {<IN>*<CD>+}""",r"""NP:{<JJ.*>*<NN.*>+<VB.*><IN>?}"""]
    #j=0
    np_parser = nltk.RegexpParser(grammar)
    np_tree = np_parser.parse(t)
    print np_tree
    q_noun = []
    for i in np_tree:
        #to get all the Noun Phrases to q_noun
        NPs=""
        if str(type(i))=="<class 'nltk.tree.Tree'>":
            for k in i:
                    # if j==0:
					# 	if k[1]=="NNS":
					# 		t=pattern.en.singularize(k[0])
					# 	else:
					# 		t=k[0]
				    # elif j==1:
					# 	if k[1]=="IN":
					# 		continue
					# 	else:
					# 		t=k[0]
					# elif j==2:
					# 	a = re.compile("VB.*")
					# 	if a.match(k[1]):
   					# 		q_noun.append(NPs)
   					# 		NPs=""
					# 	else:
   					# 		t=k[0]
                    #
					# if NPs=="":
					# 	NPs=t
					# else:
					# 	NPs=NPs+" "+t
                    #     q_noun.append(NPs)
                if k[1]=="NNP":
				    Nps=pattern.en.singularize(k[0])
                #    q_noun.append(NPs)
                elif NPs=="":
                    NPs=k[0]
                else:
                    NPs=NPs+" "+k[0]
            q_noun.append(NPs)
    # if (q_noun and j==0) or (len(q_noun)!=1 and j==1):
	# 	break
	# if j==1 and len(q_noun)==1:
	# 	q_noun1=q_noun[:]
	# if j==2 and not q_noun:
	# 	q_noun=q_noun1[:]
	# j+=1
    #
    #


    conjuction = ["of","in","as","if","as if","even","than","that","until","and","but","or","nor","for","yet","so"]
    for idx,i in enumerate(q_noun):
        #removes conjunction and replaces it with " " in btwn words for searching
        q_noun[idx] = q_noun[idx].lower()
        for j in conjuction:
            q_noun[idx]=str(q_noun[idx]).replace(j+" "," ")
            q_noun[idx]=str(q_noun[idx]).replace(" "+j," ")

    print(q_noun)
    print(len(q_noun))
    if len(q_noun) == 1:
        search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
            'wbsearchentities&search='+q_noun[0]+'&language=en&format=json')
        search_json = search_resp.json()
        #pprint(search_json['search'][0]['description'])
        a=search_json['search'][0]['id']
        #pprint (a)
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
        #pprint(property_ids)
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
