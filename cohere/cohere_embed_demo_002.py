#%%
# Cohere Demo: Visualize & understand intuition behind text embeddings, what use cases are they good for, and how we can customize them via finetuning.
# Source: https://colab.research.google.com/github/cohere-ai/notebooks/blob/main/notebooks/Visualizing_Text_Embeddings.ipynb?ref=txt.cohere.com&{query}

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import textwrap as tr

from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import cohere


#%% 
# Connect

load_dotenv()
api_key = os.getenv('cohere_key__free_trial') 
co = cohere.Client(api_key)


#%% 

# Load the dataset to a dataframe
df_orig = pd.read_csv('https://raw.githubusercontent.com/cohere-ai/notebooks/main/notebooks/data/atis_intents_train.csv',names=['intent','query'])

# Take a small sample for illustration purposes
sample_classes = ['atis_airfare', 'atis_airline', 'atis_ground_service']
df = df_orig.sample(frac=0.12, random_state=30)
df = df[df.intent.isin(sample_classes)]
df_orig = df_orig.drop(df.index)
df.reset_index(drop=True,inplace=True)

# Remove unnecessary column 
intents = df['intent'] #save for a later need
df.drop(columns=['intent'], inplace=True)
df.head()



#%% 
# Get text embeddings
def get_embeddings(texts,model='embed-english-v2.0'):
  output = co.embed(
                model=model,
                texts=texts)
  return output.embeddings

# Execute
df['query_embeds'] = get_embeddings(df['query'].tolist())
df.head()


#%%
# Reduce dimensionality using PCA
def get_pc(arr,n):
  pca = PCA(n_components=n)
  embeds_transform = pca.fit_transform(arr)
  return embeds_transform

# Execute reduce embeddings to 10 principal components to aid visualization
embeds = np.array(df['query_embeds'].tolist())
embeds_pc = get_pc(embeds,10)



#%%
# Visualize Embeddings Top-10 Principal Components  

# Set sample size to visualize
sample = 20

# Reshape the data for visualization purposes
source = pd.DataFrame(embeds_pc)[:sample]
source = pd.concat([source,df['query']], axis=1)
source = source.melt(id_vars=['query'])

# Configure the plot
chart = alt.Chart(source).mark_rect().encode(
    x=alt.X('variable:N', title="Embedding"),
    y=alt.Y('query:N', title='',axis=alt.Axis(labelLimit=500)),
    color=alt.Color('value:Q', title="Value", scale=alt.Scale(
                range=["#917EF3", "#000000"]))
)

result = chart.configure(background='#ffffff'
        ).properties(
        width=700,
        height=400,
        title='Embeddings with 10 dimensions'
       ).configure_axis(
      labelFontSize=15,
      titleFontSize=12)

# Show the plot
result




#%% 
# Visualize Embeddings Principal Components on a 2D plot  
def generate_chart(df,xcol,ycol,lbl='on',color='basic',title=''):
  chart = alt.Chart(df).mark_circle(size=500).encode(
    x=
    alt.X(xcol,
        scale=alt.Scale(zero=False),
        axis=alt.Axis(labels=False, ticks=False, domain=False)
    ),

    y=
    alt.Y(ycol,
        scale=alt.Scale(zero=False),
        axis=alt.Axis(labels=False, ticks=False, domain=False)
    ),
    
    color= alt.value('#333293') if color == 'basic' else color,
    tooltip=['query']
    )

  if lbl == 'on':
    text = chart.mark_text(align='left', baseline='middle',dx=15, size=13,color='black').encode(text='query', color= alt.value('black'))
  else:
    text = chart.mark_text(align='left', baseline='middle',dx=10).encode()

  result = (chart + text).configure(background="#FDF7F0"
        ).properties(
        width=800,
        height=500,
        title=title
       ).configure_legend(
  orient='bottom', titleFontSize=18,labelFontSize=18)
        
  return result

# Reduce embeddings to 2 principal components to aid visualization
embeds_pc2 = get_pc(embeds,2)

# Add the principal components to dataframe
df_pc2 = pd.concat([df, pd.DataFrame(embeds_pc2)], axis=1)

# Plot the 2D embeddings on a chart
df_pc2.columns = df_pc2.columns.astype(str)
generate_chart(df_pc2.iloc[:sample],'0','1',title='2D Embeddings')


#%% 
# Use Cases: Semantic Search

def get_similarity(target,candidates):
  # Turn list into array
  candidates = np.array(candidates)
  target = np.expand_dims(np.array(target),axis=0)

  # Calculate cosine similarity
  sim = cosine_similarity(target,candidates)
  sim = np.squeeze(sim).tolist()
  sort_index = np.argsort(sim)[::-1]
  sort_score = [sim[i] for i in sort_index]
  similarity_scores = zip(sort_index,sort_score)

  # Return similarity scores
  return similarity_scores

# Execute: Add new query
new_query = "show business fares"

# Get embeddings of the new query
new_query_embeds = get_embeddings([new_query])[0]

# Get the similarity between the search query and existing queries
similarity = get_similarity(new_query_embeds,embeds[:sample])

# View the top 5 articles
print('Query:')
print(new_query,'\n')

print('Similar queries:')
for idx,sim in similarity:
  print(f'Similarity: {sim:.2f};',df.iloc[idx]['query'])



#%%
# Plot the new query and existing queries on a chart

# Create new dataframe and append new query
df_sem = df.copy()
df_sem.loc[len(df_sem.index)] = [new_query, new_query_embeds]

# Reduce embeddings dimension to 2
embeds_sem = np.array(df_sem['query_embeds'].tolist())
embeds_sem_pc2 = get_pc(embeds_sem,2)

# Add the principal components to dataframe
df_sem_pc2 = pd.concat([df_sem, pd.DataFrame(embeds_sem_pc2)], axis=1)

# Create column for representing chart legend
df_sem_pc2['Source'] = 'Existing'
df_sem_pc2.at[len(df_sem_pc2)-1, 'Source'] = "New"

# Plot on a chart
df_sem_pc2.columns = df_sem_pc2.columns.astype(str)
selection = list(range(sample)) + [-1]
generate_chart(df_sem_pc2.iloc[selection],'0','1',color='Source',title='Semantic Search')



#%%
# Use Cases: Semantic Search

# Pick the number of clusters
df_clust = df_pc2.copy()
n_clusters=2

# Cluster the embeddings
kmeans_model = KMeans(n_clusters=n_clusters, random_state=0)
classes = kmeans_model.fit_predict(embeds).tolist()
df_clust['cluster'] = (list(map(str,classes)))

# Plot on a chart
df_clust.columns = df_clust.columns.astype(str)
generate_chart(df_clust.iloc[:sample],'0','1',lbl='on',color='cluster',title='Clustering Queries by their Embeddings')


# %%
# Use Cases: Classification 

# Bring back the 'intent' column so we can build the classifier
df_class = df_pc2.copy()
df_class['intent'] = intents

# Use the remaining dataset as training data
df_test = df_class[:sample]
df_train = df_class[sample:]

# Train the classifier with Support Vector Machine (SVM) algorithm
svm_classifier = make_pipeline(StandardScaler(), SVC())
features = df_train['query_embeds'].tolist()
label = df_train['intent']
svm_classifier.fit(features, label)


# %%
# Predict with test data

# Prepare the test inputs
df_test = df_test.copy()
inputs = df_test['query_embeds'].tolist()

# Predict the labels
df_test['intent_pred'] = svm_classifier.predict(inputs)

# Compute the score
score = svm_classifier.score(inputs, df_test['intent'])
print(f"Prediction accuracy is {100*score}%")

# Plot the predicted classes
df_test.columns = df_test.columns.astype(str)
generate_chart(df_test,'0','1',lbl='off',color='intent_pred',title='Classification - Prediction')


# %%
# Plot the actual classes

generate_chart(df_test,'0','1',lbl='off',color='intent',title='Classification - Actual')



# %%
# Finetuning Embeddings

# TODO: Implement finetunning using SDK (https://docs.cohere.com/docs/representative-models)

# The finetuned model ID
atis_ft_v1 = "ccc2a8dd-bac5-4482-8d5e-ddf19e847823-ft" # Replace with your own model ID

# Embed the dataset - use the finetuned model this time
df_ft = df.copy()
df_ft['intent'] = intents

df_ft['query_embeds'] = get_embeddings(df_ft['query'].tolist(), model=atis_ft_v1)


#%%
# Reduce embeddings to 2 dimensions
embeds_ft = np.array(df_ft['query_embeds'].tolist())
embeds_ft_pc2 = get_pc(embeds_ft,2)

# Plot the 2D embeddings from a finetuned model
df_ft_pc2 = pd.concat([df_ft, pd.DataFrame(embeds_ft_pc2)], axis=1)
df_ft_pc2.columns = df_ft_pc2.columns.astype(str)
generate_chart(df_ft_pc2.iloc[:sample],'0','1',lbl='off',color='intent', title='Finetuned model')



# %%
# Plot the 2D embeddings from a non-finetuned model

generate_chart(df_test,'0','1',lbl='off',color='intent',title='Non-finetuned model')




# %%
