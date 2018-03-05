import nltk, pattern.en
s = raw_input("String???   ")

t=pattern.en.tag(s)
#grammar = r"""NP: {<DT|PP\$>?<JJ>*<NN.*>+}"""
# grammar = r"""NP: {<JJ.*>+<NN.*>+}
#             NP_A: {<NN.*>+(<IN>?<JJ.*>?)?}"""
grammar = r"""NP: {<JJ.*>+<NN.*>+}
            NP_A: {<NN.*>+<IN>*<JJ.*>*}"""        #grammar 2 for chunking
np_parser = nltk.RegexpParser(grammar)
np_tree = np_parser.parse(t)
print np_tree
q_noun = []
for i in np_tree:
    #to get all the Noun Phrases to q_noun
    NPs=""
    if str(type(i))=="<class 'nltk.tree.Tree'>":
          for k in i:
            if NPs=="":
                NPs=k[0]
            else:
                NPs=NPs+" "+k[0]
                q_noun.append(NPs)
#print (list(enumerate(q_noun)))
#output ----[(0, u'FATHER OF'), (1, u'BARACK OBAMA')]
conjuction = ["of","in","as","if","as if","even","than","that","until","and","but","or","nor","for","yet","so"]
for idx,i in enumerate(q_noun):
    q_noun[idx] = q_noun[idx].lower()  #if grammar 2 is used
                    #add + in btwn words for searching
    for j in conjuction:
        q_noun[idx]=str(q_noun[idx]).replace(j+" "," ")
        q_noun[idx]=str(q_noun[idx]).replace(" "+j," ")

print (q_noun)



# from textblob import TextBlob
# str="who is the president of india?"
# blob=TextBlob(str)
# print(blob.tags)
# [('who', 'WP'), ('is', 'VBZ'), ('the', 'DT'), ('president', 'NN'), ('of', 'IN'), ('india', 'NN')]
# str="what is the birthplace of Barack Obama?"
# blob=TextBlob(str)
# print(blob.tags)
# [('what', 'WP'), ('is', 'VBZ'), ('the', 'DT'), ('birthplace', 'NN'), ('of', 'IN'), ('Barack', 'NNP'), ('Obama', 'NNP')]
# >>> str="where was barack obama born?"
# >>> blob=TextBlob(str)
# >>> print(blob.tags)
# [('where', 'WRB'), ('was', 'VBD'), ('barack', 'JJ'), ('obama', 'NN'), ('born', 'VBN')]
