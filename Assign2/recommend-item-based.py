# recommendations users for one specific movie

from math import sqrt

# load database and construct the  nested dictionary
def loadMovies(path='/movies100K'):

  #Get movie titles
  movies={}
  for line in open(path+'/u.item'):
    (id, title) = line.split('|')[0:2]
    movies[id] = title

  #load data
  prefs={}
  for line in open(path+'/u.data'):
    (usr, movieid, rating, ts) = line.split('\t')
    prefs.setdefault(usr, {})
    prefs[usr][movies[movieid]]=float(rating)
  return prefs

# flip user-item in the nested dictionary "prefs"
def transformPrefs(prefs):
  result = {}
  for person in prefs:
    for item in prefs[person]:
      result.setdefault(item, {})

      #flip item and person
      result[item][person] = prefs[person][item]
  return result

# compute the Euclidean distance between two person's preferences
def sim_distance(prefs, person1, person2):

  #Get the list of shared items
  si = {}
  for it in prefs[person1]:
    if it in prefs[person2]:
      si[it]=1

  #if they have no ratings in common, return 0
  if (len(si) == 0): return 0

  # Add up the squares of all the differences
  euclidean_distance = sqrt(sum([pow(prefs[person1][it] - prefs[person2][it], 2) 
                    for it in si]))

  similarity = 1/(1+euclidean_distance)
  return similarity

# compute the pearson correlation coefficient
def sim_pearson(prefs, person1, person2):
 
  #Get the list of shared items
  si = {}
  for it in prefs[person1]:
    if it in prefs[person2]:
      si[it]=1
  
  # Find the number of elements
  n = len(si)

  # if they have no ratings in common, return 0
  if n==0:  return 0

  # sum
  sum1 = sum([prefs[person1][it] for it in si])
  sum2 = sum([prefs[person2][it] for it in si])

  # sum of the squares
  sum1Square = sum([pow(prefs[person1][it], 2) for it in si])
  sum2Square = sum([pow(prefs[person2][it], 2) for it in si])

  # sum up the products
  pSum = sum([prefs[person1][it]*prefs[person2][it] for it in si])

  # compute the correlation coefficient
  num = pSum - (sum1*sum2/n)
  denom = sqrt((sum1Square - pow(sum1, 2)/n)*(sum2Square - pow(sum2, 2)/n))

  if denom == 0: return 0

  pearson_correlation = num/denom

  return pearson_correlation

# return the top N most similar person/items
def topMatches(prefs, person, n=5, similarity=sim_pearson):
  scores=[(similarity(prefs, person, other), other)
             for other in prefs if other != person]

  # sort the list so the highest scores appear at the top
  scores.sort()
  scores.reverse()

  return scores[0:n]

# Build the complete dataset of similar items
def calculateSimilarItems(prefs, n=10):
  # Create a dictionary of items showing which other items they are
  # most similar to
  result = {}

  #Invert the preference matrix to be item-centric
  itemPrefs = transformPrefs(prefs)

  for item in itemPrefs:
    # Find the most similar n items to this one
    scores = topMatches(itemPrefs, item, n=n, similarity=sim_pearson)
    result[item] = scores

  return result

# Get recommendations for a person by using a weighted average
# of every other user's ranking
def getRecommendationsItems(prefs, itemMatch, user):

  userRatings = prefs[user]
  scores={}
  totalSim = {}
 
  # Loop over items rated by this user
  for (item, rating) in userRatings.items():

    #Loop over items similar to this one
    for (similarity, item2) in itemMatch[item]:

      #Ignore if this user has already rated this item
      if item2 in userRatings: continue

      # Weighted sum of rating times similarity
      scores.setdefault(item2, 0)
      scores[item2] += similarity * rating

      # Sum of all the similarities
      totalSim.setdefault(item2, 0)
      totalSim[item2] += similarity

  #Divide each total score by total weighting to get an average
  rankings = [(score/totalSim[item], item) 
                for item, score in scores.items() if totalSim[item] != 0]

  #Return the rankings from highest to lowest
  rankings.sort()
  rankings.reverse()
  return rankings

# main function
if __name__ == '__main__':

  prefs = loadMovies('movies100K')

  # find top n similar items to each item in the database
  itemMatch = calculateSimilarItems(prefs, 20)

  #get recommendations
  print '\nRecommended movies\n'
  recommendations = getRecommendationsItems(prefs, itemMatch, '747')
  print recommendations
  
