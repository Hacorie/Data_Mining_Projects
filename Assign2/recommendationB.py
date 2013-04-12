# user based recommendations

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
  prefs2 = {}
  for line in open(path+'/u.data'):
    (usr, movieid, rating) = line.split('\t')[0:3]
    if int(usr) in range(1,101):
      prefs2.setdefault(usr, {})
      prefs2[usr][movies[movieid]]=float(rating)
    prefs.setdefault(usr, {})
    prefs[usr][movies[movieid]]=float(rating)
  return prefs, prefs2

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
  euclidean_distance = sqrt(sum([pow(prefs[person1][it] - prefs[person2][it], 2) for it in si]))

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
def topMatches(prefs, person, n=5, similarity=sim_distance):
  scores=[(similarity(prefs, person, other), other)
             for other in prefs if other != person]

  # sort the list so the highest scores appear at the top
  scores.sort()
  scores.reverse()

  return scores[0:n]

# Get recommendations for a person by using a weighted average
# of every other user's ranking
def getRecommendations(prefs, person,  similarity=sim_distance):

  totals={}
  simSums = {}


  for other in prefs:
    # don't compare one to himself
    if other == person:
      continue

    sim = similarity(prefs, person, other)

    #ignore scores of zero or lower
    if sim <= 0:
      continue

    for item in prefs[other]:
      #only score movies I have not seen before
      if item not in prefs[person] or prefs[person][item]==0:
        totals.setdefault(item, 0)

        #simiarity * score
        totals[item] += prefs[other][item]*sim

        #sum of similarities
        simSums.setdefault(item, 0)
        simSums[item] += sim

  # Create the normalized list
  rankings=[(total/simSums[item], item)
              for item, total in totals.items()]

  # Return the sorted list
  rankings.sort()
  rankings.reverse()

  return rankings

# Gets the recommended ranks for movies a person has seen.
# Masks the movie and then uses getRecommendations to get
# the estimated Rank.
def getRecommendedRanks(prefs, person):

  #list to hold all the ranks
  totalRanks = []
  #List to hold all recommended ranks for a person's seen movies
  recommendedRanks = []
  #A copy of Prefs
  newPrefs = prefs[person]

  #Pick out a movie a the person has seen and remove it
  for movie in newPrefs:
    rmvdKey = movie
    rmvdVal = newPrefs[movie]
    del newPrefs[movie]

    #update prefs to display the change above
    prefs[person] = newPrefs

    #Compute the recommendation for the movie we just removed
    totalRanks = getRecommendations(prefs, person)

    #Find the new recommendation and save it
    for (x,y) in totalRanks:
      if y == rmvdKey:
        recommendedRanks.append((y,x))
    newPrefs[rmvdKey] = rmvdVal

  #Put prefs back to normal
  prefs[person] = newPrefs

  return recommendedRanks

# Takes a persons recommended rankings for movies they
# have seen from getRecommendedRanks and compares them
# to the true ranking the person gave the movie and 
# applies sim_pearson's to these values to get the 
# correlation.
def compareRec2True(prefs, person, recommendedRanks):

  #Dictionaries to hold comparitive data to be put in prefs
  newPerson = {}
  rankPerson = {}

  #populate newperson and rankperson
  for (x,y) in recommendedRanks:
    for movie in prefs[person]:
      if x == movie:
        newPerson[movie] = prefs[person][movie]
        rankPerson[movie] = y
  #insert the two newpeople into the prefs dictionary for comparison
  prefs['101'] = rankPerson
  prefs['102'] = newPerson

  #pearson corellation for the two new users
  r1 = sim_pearson(prefs, '101', '102')

  #open two files to save the recommended ranks and a person's data
  #f1 = open('recRanks1.txt','w')
  #f2 = open('person1.txt','w')
  #write to the files for comparison
  #for rank in prefs['101']:
    #f1.write('%s\n\t' % rank)
    #f1.write('%s\n' % prefs['101'][rank])
  #for rank in prefs['102']:
    #f2.write('%s\n\t' % rank)
    #f2.write('%s\n' % prefs['102'][rank])

  #get rid of the two new users you added to prefs
  del prefs['101']
  del prefs['102']

  #return the correlation value
  return r1





# main function
if __name__ == '__main__':

  prefs, prefs2 = loadMovies('movies100K')
  #print prefs

  #toprint = [(person) for person in prefs]
  #print toprint

  #print "pearson distance:\n"
  #mostSimilar=topMatches(prefs, '1', 20, sim_pearson)
  #print mostSimilar
  #print '\n'

  #print "euclidean distance:\n"
  #mostSimilar=topMatches(prefs, '345', 5, sim_distance)
  #print mostSimilar
  #print '\n'

  #List of all the correllations
  rList = []

  #variable of the corellations
  sum1 = 0

  #loop thorugh and extract all users' corellations
  for person in prefs2:
    recommendedRanks = getRecommendedRanks(prefs,person)
    r1 = compareRec2True(prefs2,person,recommendedRanks)
    rList.append(r1)
    sum1 += r1

  #print all the corellations and the average of them all
  print rList
  print sum1 / len(rList)


  #get recommendations
  #s = getRecommendations(prefs, '47', sim_pearson)
  #print recommendations

