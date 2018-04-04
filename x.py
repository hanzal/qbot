def parse(q_tagged):
	grammars=[r"""NP: {<JJ.*>*<NNS><IN>+<DT>*<NN.*>+}""",r"""NP: {<JJ.*>*<IN>*<NN.*>+}
	{<NN.*><IN>+<JJ.*>+}
	{<IN>*<CD>+}""",r"""NP:{<JJ.*>*<NN.*>+<VB.*><IN>?}"""]
	#^grammars for diff types of question
	j=0
	q_noun=[]
	for grammar in grammars:
		grmr=j
		print(repr(grammar))
		np_parser = nltk.RegexpParser(grammar)
		np_tree = np_parser.parse(q_tagged)
		q_noun = []
		print(repr(np_tree))
		for i in np_tree:
			print(repr("NP : " + str(i)))						#to get all the Noun Phrases to q_noun
			NPs=""2
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
						print(repr("NPs : " + str(NPs)))
				q_noun.append(NPs)
				print(repr("q_noun : " + str(q_noun)))
		if (q_noun and j==0) or (len(q_noun)!=1 and j==1):
			break
		if j==1 and len(q_noun)==1:
			q_noun1=q_noun[:]
		if j==2 and not q_noun:
			q_noun=q_noun1[:]
		j+=1
		print(repr(q_noun))
		print(repr("grmr :"+str(grmr)))
	grammar = {'q_noun':q_noun, 'grammar':grmr,'np_tree':np_tree}
	parsed = grammar
	noun_save = ""
	for a in q_noun:
		noun_save += " | " + a.lower()
	parsed['noun_save'] = noun_save
	return parsed


#	o/p
# >>> parse(q_tagged)
# 'NP: {<JJ.*>*<NNS><IN>+<DT>*<NN.*>+}'
# Tree('S', [('who', u'WP'), ('is', u'VBZ'), ('the', u'DT'), ('father', u'NN'), ('of', u'IN'), ('obama', u'NN')])
# "NP : ('who', u'WP')"
# "NP : ('is', u'VBZ')"
# "NP : ('the', u'DT')"
# "NP : ('father', u'NN')"
# "NP : ('of', u'IN')"
# "NP : ('obama', u'NN')"
# []
# 'grmr :0'
# 'NP: {<JJ.*>*<IN>*<NN.*>+}\n\t{<NN.*><IN>+<JJ.*>+}\n\t{<IN>*<CD>+}'
# Tree('S', [('who', u'WP'), ('is', u'VBZ'), ('the', u'DT'), Tree('NP', [('father', u'NN')]), Tree('NP', [('of', u'IN'), ('obama', u'NN')])])
# "NP : ('who', u'WP')"
# "NP : ('is', u'VBZ')"
# "NP : ('the', u'DT')"
# 'NP : (NP father/NN)'
# "q_noun : ['father']"
# 'NP : (NP of/IN obama/NN)'
# "q_noun : ['father', 'obama']"
# {'noun_save': u' | father | obama', 'q_noun': ['father', 'obama'], 'grammar': 1, 'np_tree': Tree('S', [('who', u'WP'), ('is', u'VBZ'), ('the', u'DT'), Tree('NP', [('father', u'NN')]), Tree('NP', [('of', u'IN'), ('obama', u'NN')])])}
