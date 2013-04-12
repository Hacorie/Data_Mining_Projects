#!/usr/bin/env python

#Auther: Nathan Perry
#Homework: 4
#Due date: 2/27/2012

import numpy as np
import os
import re
import math
import sys
import htmlentitydefs   # contains nbsp, etc.
from math import log

MinimumProb = 1.0e-10

#takes a string and splits it in to a list of words
def SeparateWords(text, stopWords):
    output = []
    isnumeric = re.compile('\\-?\d+')
    splitter = re.compile('\\W*')
    words = splitter.split(text)
    for s in words:
        s = s.strip()
        s = s.lower()
        if s!='' and len(s) > 1 and not isnumeric.match(s) and not (s in stopWords):
           output.append(s)

    return output

def ReadStopWords():
    # read the list of stop words from the file "stopwords"
    stopWords = []
    stopwords = open("stopwords", 'r').readlines();
    for sw in stopwords:
       stopWords.append(sw.strip())

    return stopWords

# Learning Step
def Learn(path, percent_data=100):

    # Learning step
    # 1. for K classes (stored in K directories):
    #    1.a for each file in the kth class:
    #        1.a.1 find each word in the file
    #        1.a.2 cumulate the frequency of the word in this class
    #    1.b compute the conditional probabilites of each word in the kth class
    #
    totalFileCount = 0  # total number of files read

    stopWords = ReadStopWords()

    # read and process the data files in each of the class directories 
    dir = os.listdir(path)   # find the classes

    classProbability = {}  # p(Ck)
    model = {}  # P(Wi | Ck) each class has a corresponding table of 
                  # probabilities of the words seen for this class
    wordCounts={}
    Vocabulary= {}
    fileCounts={}
    for class_i in dir:

        termFreq = {}  # collect counts of terms in each document

        # Process class_i
        fileCount = 0 # number of files in this class
        wordCount = 0 # number of valid words in the current document

        posPath = os.path.join(path, class_i)

        #Calculate the correct number of files to read
        number_of_files =   int(percent_data/100.0 *   len(os.listdir(posPath)))
        fc = 0
        for fileName in os.listdir(posPath):

            fileCount += 1  # one more document in this class
            fc += 1

            #Do not read more files than specified!
            if fc >= number_of_files:
                break
            fileloc = os.path.join(posPath, fileName)
            article = open(fileloc, 'r').read()

            #separate out the list of words
            words = SeparateWords(article, stopWords)

            #remove numbers and single char words
            #compute the term frequency
            findNumber=re.compile('[0-9|-]+')
            for word in words:
               if (findNumber.search(word) == None) and len(word) > 1:

                 wordCount += 1   # found another valid word, add 1 to total word count 

                 if (word not in Vocabulary):  # add the word to vocabulary if first seen
                    Vocabulary[word] = 1

                 if (word in termFreq.keys()):  # tally the frequency count for the word
                     termFreq[word] += 1
                 else:  # word first seen, count is 1
                     termFreq[word] = 1

        # tally the counts for class_i
        fileCounts[class_i] = fileCount
        wordCounts[class_i] = wordCount
        print "class %s has %d files and %d words" % (class_i, fileCount, wordCount)

        totalFileCount += fileCount # total number of documents in the training data

        model[class_i] = termFreq

    VocabSize = len(Vocabulary)
    #print "vocab size = %d" % VocabSize
    for class_i in model:
        #compute the probabilites based on the termFreq
        classProbability[class_i] = float(fileCounts[class_i]) / totalFileCount

        for word in model[class_i]:
             model[class_i][word] = float((model[class_i][word])+1)/(wordCounts[class_i]+VocabSize)

        #print the top 10 words per each group
        count = 0
        for w in sorted(model[class_i], key = model[class_i].get, reverse=True):
            print "Top Word in %s: " %class_i,
            print "%s: %f" %(w, model[class_i][w])
            count +=1
            if count >= 10:
                break
        print "\n"

    return classProbability, model, wordCounts, VocabSize

#Classification step
def Classify(path, classProb, model, wordCounts, VocabSize):

    correct = 0;
    total = 0.0;
    stopWords = ReadStopWords()

    #loop over the directory structure
    for class_dir in os.listdir(path):
        print "Classifying %s" %class_dir
        sub_dir = os.path.join(path, class_dir)

        for fileName in os.listdir(sub_dir):
            fileloc = os.path.join(sub_dir, fileName)
            article = open(fileloc, 'r').read()

            #separate the words
            words = SeparateWords(article, stopWords)

            #remove numbers and single char words, compute the term frequency
            findNumber=re.compile('[0-9|-]+')
            thisDoc=[]
            for word in words:
                if (findNumber.search(word) == None) and len(word) > 1:
                    thisDoc.append(word)

            likelihood = []
            for class_i in classProb:
                currLogProb = 0
                for word in thisDoc:
                    if word in model[class_i]:
                        currLogProb += log(float(model[class_i][word]))
                    else:
                        currLogProb += log(1.0/(wordCounts[class_i]+VocabSize))
                currLogProb += log(float(classProb[class_i]))

                likelihood.append((currLogProb, class_i))

            likelihood.sort()
            likelihood.reverse()
            print likelihood[0]

            #Tally the number of correct classifications
            if likelihood[0][1] == class_dir:
                correct+=1
            total +=1

    #return the percentage correct
    return (correct/total)

if (__name__ == '__main__'):

    #Start of Part A
    accuracy = [100, 80, 60, 40, 20, 10, 5]
    list_accuracy = {}
    # Learning Step
    for item in accuracy:
        classProb, model, wordCounts, VocabSize = Learn('experiment/training/', item)
        list_accuracy[item] = Classify('experiment/testing/', classProb, model, wordCounts, VocabSize)
    print "The Accuracy of The documents at each accuracy level is below:" 
    print list_accuracy

    #Start of part B
    print "\n\n Part B starts here: Email Classification Spam vs. Good"
    classProb, model, wordCounts, VocabSize = Learn('experiment/emaillearn/')
    acc = Classify('experiment/emailtest/', classProb, model, wordCounts,  VocabSize)
    print "The Accuracy of my Spam to Good email classification is: %f" %acc

    # Classification Step
