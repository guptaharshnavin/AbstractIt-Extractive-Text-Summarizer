# Importing Libraries
import re
# Importing Spacy English Library
import en_core_web_md
# Importing Spacy
import spacy
# Importing Stop Words
from spacy.lang.en.stop_words import STOP_WORDS
# Importing Count Vectorizer from SKLEARN
from sklearn.feature_extraction.text import CountVectorizer
# Importing Flask Related Components
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/dev_team/')
def dev_team():
    return render_template('dev_team.html')

@app.route('/summarize',methods=['POST'])
def summarize():
	form_features = []

	for x in request.form.values():
		form_features.append(x)

	form_features[0] = re.sub('[[0-9]+]','',form_features[0]).replace('\n','').replace('\r','').strip()
	form_features[1] = int(form_features[1])

	paragraph = form_features[0]
	# Loading the Spacy English MD Library
	nlp = en_core_web_md.load()
	# Creating Spacy Doc
	doc = nlp(paragraph)
	# Building Corpus
	corpus = []

	for s in doc.sents:
		corpus.append(s.text.lower())

	number_of_sents = len(corpus)

	# Applying Count Vectorizer To Corpus
	cv = CountVectorizer(stop_words=list(STOP_WORDS))
	cv_fit = cv.fit_transform(corpus)

	# Getting Word List from Count Vectorizer
	word_list = cv.get_feature_names()

	# Getting Sum of Word Occurences
	word_counts = cv_fit.toarray().sum(axis=0)

	# Creating Dictionary for Words and Occurences
	word_freq_dict = dict(zip(word_list, word_counts))

	# Sorting Word Counts in Descending Order
	sort_word_counts = sorted(word_freq_dict.values(), reverse=True)

	# Getting Higher Freqeuncy Words
	higher_frequency_words = []

	# Words With Top 5 Frequency are considered as Higher Frequency Words
	for word, freq in word_freq_dict.items():
		if freq in sort_word_counts[0:5]:
			higher_frequency_words.append(word)

	most_frequent_words = ""
	for word in higher_frequency_words:
		most_frequent_words = most_frequent_words + word + ", "

	# Scaling The Frequency Of Words With Relative To Highest Frequency
	for word in word_freq_dict.keys():
		word_freq_dict[word] = word_freq_dict[word]/sort_word_counts[0]

	# Assigning Ranks To Sentences
	sentence_ranks = {}

	for sentence in doc.sents:
		for word in sentence:
			if word.text.lower() in word_freq_dict.keys():
				if sentence in sentence_ranks.keys():
					sentence_ranks[sentence] += word_freq_dict[word.text.lower()]
				else:
					sentence_ranks[sentence] = word_freq_dict[word.text.lower()]
	
	# Sorting Sentences According To Ranks
	sorted_sentences = sorted(sentence_ranks.items(), key=lambda x: x[1], reverse=True)

	number_of_sentences = form_features[1]
	final_para = ""

	if number_of_sentences > number_of_sents:
		final_para = "Length Of Desired Summary Greater than Input Text"
	elif number_of_sentences <= 0:
		final_para = "Length Of Desired Summary Must Greater Than 0"
	else:
		for i in range(0, number_of_sentences):
			sentence_tuple = sorted_sentences[i]
			final_para = final_para + sentence_tuple[0].text

	most_head = "Most Occurring Words : "
	summ_head = "Summary Of Text"
	most_frequent_words = most_frequent_words[0:-2]
	return render_template('index.html', summary_text = final_para, most_heading = most_head, most_words = most_frequent_words,
		summ_head = summ_head)	

if __name__ == '__main__':
	app.run(debug=False)