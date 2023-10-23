#%%
# Topic Modeling Example
# Using Latent Dirichlet Allocation (LDA)

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.preprocessing import StandardScaler
import nltk
import re


#%%
# Download requirements

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(nltk.corpus.stopwords.words('english'))


#%%
# Download the 20 Newsgroups dataset (takes a minute)

newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))

print("Number of documents:", len(newsgroups.data))
print("Categories (Targets):", newsgroups.target_names)

print("Example Document (first document):")
print("Data:", newsgroups['data'][0])  
print("Category (Target):", newsgroups.target[0], '-->', newsgroups.target_names[newsgroups.target[0]])  
print("Filename:", newsgroups.filenames[0])  


#%%
# Preprocess the text data 

def preprocess_text(text):
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    return text

preprocessed_docs = [preprocess_text(text) for text in newsgroups.data]

print("Example Document (first document):")
print(preprocessed_docs[0])


#%%
# Vectorize the text using CountVectorizer

vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
X = vectorizer.fit_transform(preprocessed_docs)


#%%
# Apply LDA for topic modeling

num_topics = 10  # You can adjust the number of topics
lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
lda.fit(X)


#%%
# Print the top words for each topic

feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    top_words_indices = topic.argsort()[:-10 - 1:-1]
    top_words = [feature_names[i] for i in top_words_indices]
    print(f"Topic {topic_idx + 1}: {', '.join(top_words)}")


#%%
# To classify a new document

new_doc = "The Devils continue to focus on improving the defensive side of their game, and Lindy discusses his time with the Devils after earning his 100th win last night."
print("New Document:\n", new_doc, '\n')

new_doc_prep = preprocess_text(new_doc)
new_doc_vec = vectorizer.transform([new_doc_prep])
topic_distribution = lda.transform(new_doc_vec)
print("Topic distribution for the new document:", topic_distribution, '\n')

# Get the top 3 topics with their scores
sorted_topics = sorted(enumerate(topic_distribution[0]), key=lambda x: x[1], reverse=True)
top_topics = sorted_topics[:3]
for topic_idx, score in top_topics:
    print(f"Topic {topic_idx + 1}: Score {score:.4f}")



#%%
