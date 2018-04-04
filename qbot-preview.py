import requests, json, nltk, pattern.en
from nltk import tree
from pprint import pprint
from textblob import TextBlob
from models import History
from math import radians, cos, sin, asin, sqrt

def run():
    while True:
        question = raw_input('Enter the question: \n')
        if question == "close":
        	break

        #tags the question
        blob = TextBlob(question)
        q_tagged = blob.tags
        # print repr(q_tagged)

        parsed = parse(q_tagged, question)
        q_noun = parsed['q_noun']
        print q_noun

        #retrieve from History
        answer_doc = History.select().where(History.q_noun == str(q_noun))
        if answer_doc:
            print "from history",answer_doc[0].answer
            continue

        answer = None

        elif len(q_noun) == 1:
        	a = wikidata_search(q_noun[0])
        	entity_json = wikidata_get_entity(a['qid'])
        	val = entity_json['entities'][a['qid']]['descriptions']['en']['value']
        	if val:
        		answer = val
        		History.create(question=question, answer= answer, q_noun=str(q_noun))

        elif "distance" in question:
        	q_noun_copy = list(q_noun)
        	q_noun = [k for k in q_noun if 'distance' not in k]

        	loc1= q_noun[0]
        	loc2= q_noun[1]

        	loc1_search = wikidata_search(loc1)
        	loc2_search = wikidata_search(loc2)

        	qid1 = loc1_search['qid']
        	qid2 = loc2_search['qid']

        	loc1_json = wikidata_get_entity(qid1)
        	# pprint(loc1_json)
        	loc2_json = wikidata_get_entity(qid2)

        	if loc1_json['entities'][qid1]['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']:
        		latvalue1 = loc1_json['entities'][qid1]['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']
        		lonvalue1 = loc1_json['entities'][qid1]['claims']['P625'][0]['mainsnak']['datavalue']['value']['longitude']

        	if loc2_json['entities'][qid2]['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']:
        		latvalue2 = loc2_json['entities'][qid2]['claims']['P625'][0]['mainsnak']['datavalue']['value']['latitude']
        		lonvalue2 = loc2_json['entities'][qid2]['claims']['P625'][0]['mainsnak']['datavalue']['value']['longitude']

        	# print(latvalue1, lonvalue1, latvalue2, lonvalue2)
        	lon1, lat1, lon2, lat2 = map(radians, [lonvalue1, latvalue1, lonvalue2, latvalue2])
        	# haversine formula
        	dlon = lon2 - lon1
        	dlat = lat2 - lat1
        	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        	c = 2 * asin(sqrt(a))
        	r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        	d = int(c*r)
        	value = str(d) + " kms approx."
        	answer = value
        	History.create(question=question, answer= answer, q_noun=str(q_noun_copy))

        else:
        	property_ids = []
        	search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
        		'wbsearchentities&search='+q_noun[0]+'&language=en&format=json&type=property')
        	search_json = search_resp.json()
        	for p in search_json['search']:
        		property_ids.append(p['id'])
        	answer_fetched = False
        	answer = ''
        	search_resp = requests.get('https://www.wikidata.org/w/api.php?action='
        		'wbsearchentities&search='+q_noun[1]+'&language=en&format=json')
        	search_json = search_resp.json()
        	for s in search_json['search']:
        		entity_json = wikidata_get_entity(s['id'])
        		for p in property_ids:
        			if entity_json['entities'][s['id']]['claims'].get(p,None):
        				property_value = entity_json['entities'][s['id']]['claims'][p][0]
        				property_value_id = property_value['mainsnak']['datavalue']['value']['id']
        				answer_json = wikidata_get_entity(property_value_id)
        				answer = answer_json['entities'][property_value_id]['labels']['en']['value']
        				descr=answer_json['entities'][property_value_id]['descriptions']['en']['value']
        				answer_fetched = True
        				break
        		if answer_fetched:
        			break

        	if answer_fetched:
        		History.create(question=question, answer= answer, q_noun=str(q_noun))

        if answer:
        	print 'Answer : ', answer.decode()
        else:
        	print "Oops!Can't find the answer."

def wikidata_search(q_noun):
	qid = False
	q_noun.replace(" ","+")
	response = requests.get('https://www.wikidata.org/w/api.php?action=wbsearchentities&search='+q_noun+'&format=json&language=en')
	data = response.json()

	if data['search']:
		if 'description' in data['search'][0]:
			if data['search'][0]['description'] == 'Wikipedia disambiguation page' or data['search'][0]['description'] == 'Wikimedia disambiguation page':
				qid = data['search'][1]['id']
			else:
				qid = data['search'][0]['id']
		else:
			qid = data['search'][0]['id']
	if not qid:
		qid=False
	return {'q_noun':q_noun,'qid':qid}

def wikidata_get_entity(qid):
	response = requests.get('https://www.wikidata.org/w/api.php?action=wbgetentities&ids='+qid+'&format=json&languages=en')
	return response.json()

def parse(q_tagged, question):
    grammars=[r"""NP: {<JJ.*>*<NNS><IN>+<DT>*<NN.*>+}""",r"""NP: {<JJ.*>*<IN>*<NN.*>+}
    {<NN.*><IN>+<JJ.*>+}
    {<IN>*<CD>+}""",r"""NP:{<JJ.*>*<NN.*>+<VB.*><IN>?}"""]
    j=0
    q_noun=[]
    for grammar in grammars:
        grmr=j
        # print repr(grammar)
        np_parser = nltk.RegexpParser(grammar)
        np_tree = np_parser.parse(q_tagged)
        q_noun = []
        # print repr(np_tree)
        for i in np_tree:
        	# print repr("NP : " + str(i))						#to get all the Noun Phrases to q_noun
        	NPs=""
        	if str(type(i))=="<class 'nltk.tree.Tree'>":
        		for k in i:
        			if j==0:
        				if k[1]=="NNS":
        					t=pattern.en.singularize(k[0])
        				else:
        					t=k[0]
        			elif j==1:
        				if k[1]=="IN":
        					continue
        				else:
        					t=k[0]
        			elif j==2:
        				a = re.compile("VB.*")
        				if a.match(k[1]):
        					q_noun.append(NPs)
        					NPs=""
        				t=k[0]

        			if NPs=="":
        				NPs=t
        			else:
        				NPs=NPs+" "+t
        				# print repr("NPs : " + str(NPs))

        		q_noun.append(NPs)
        		# print repr("q_noun : " + str(q_noun))
        if (q_noun and j==0) or (len(q_noun)!=1 and j==1):
        	break
        if j==1 and len(q_noun)==1:
        	q_noun1=q_noun[:]
        if j==2 and not q_noun:
        	q_noun=q_noun1[:]

        j+=1

        # print repr(q_noun)
        # print repr("grmr :"+str(grmr))

    grammar = {'q_noun':q_noun, 'grammar':grmr,'np_tree':np_tree}

    parsed = qcheck(grammar, question)
    noun_save = ""
    for a in q_noun:
    	noun_save += " | " + a.lower()

    parsed['noun_save'] = noun_save

    return parsed

def qcheck(parsed, question):
    q_noun = parsed['q_noun']
    grmr = parsed['grammar']

    if not q_noun:
    	return {'q_noun':q_noun,'type':"keyword"}

    if grmr==0:
    	np_tree=parsed['np_tree']
    	return {'q_noun':q_noun,'type':"list",'np_tree':np_tree}

    if len(q_noun)==1 and grmr==2:
    	des = True
    	qid = False
    	for idx,i in enumerate(q_noun):					#add + in btwn words for searching
    		# print repr(str(q_noun[idx]))
    		x=str(q_noun[idx]).replace(" ","+")
    		q_noun[idx]=x
    	return {'q_noun':q_noun,'type':"description"}


    rng = False
    dt = False
    for idx,k in enumerate(q_noun):
    	if 'distance' in k or 'length' in k or 'long' in k or 'kilometers'in k or 'how far' in question:
    		rng = True
    		del q_noun[idx]

    if rng:
    	for idx,i in enumerate(q_noun):
    		q_noun[idx] = q_noun[idx].replace(' ','+')
    	return {'q_noun':q_noun,'type':"distance"}

    if ('days' in question and 'between' in question) or ('time' in question and 'duration' in question) :
    	dt = True
    	return {'q_noun':q_noun,'type':"time"}

    if grmr==2 or grmr==1:
    	return {'q_noun':q_noun,'type':"general"}

if __name__ == '__main__':
	run()
