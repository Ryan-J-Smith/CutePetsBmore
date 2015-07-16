from bs4 import BeautifulSoup

import requests
import re
import random
import tweepy
import shutil
import datetime
import os
import time

from credentials import twitterConsumerKey, twitterConsumerSecret, twitterAccessToken, twitterAccessTokenSecret

global shelterDict
shelterDict = {
    'barcs': 556,
    'bhs': 444
    }

scriptDir = os.path.dirname(os.path.realpath(__file__))

class twitterAPI(object):
    def __init__(self): 
        auth = tweepy.OAuthHandler(twitterConsumerKey, twitterConsumerSecret)
        auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)
        self.api = tweepy.API(auth)
    
    def tweet(self, message):
        self.api.update_status(status=message)

    def tweetWPic(self, imgPath, msg):
        self.api.update_with_media(filename=imgPath,status=msg)

class rescuePet(object):

    def __init__(self):
        self.name = None
        self.gender = None
        self.breed = None
        self.photoURL = None
        self.profileURL = None
        self.localImgPath = scriptDir + '/petImg.jpg'
    
    def __str__(self):
        nameStr = 'Name: {0}\n'.format(self.name)
        genderStr = 'Gender: {0}\n'.format(self.gender)
        breedStr = 'Breed: {0}\n'.format(self.breed)
        photoStr = 'Photo URL: {0}\n'.format(self.photoURL)
        profileStr = 'Profile URL: {0}'.format(self.profileURL)
        fullStr = nameStr + genderStr + breedStr + photoStr + profileStr
        return fullStr

    def getImage(self):
        res = requests.get(self.photoURL, stream=True)
        with open(self.localImgPath, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        del res       

    def postTweet(self):
        '''Get image, format tweet, post tweet'''

        # Get image
        self.getImage()

        # Create message
        tweetMsg = 'Hi! My name is {0}. I\'m a {1} {2}. Adopt me at: {3}'.format(self.name, self.gender, self.breed, self.profileURL)

        # Post tweet
        twitter = twitterAPI()
        twitter.tweetWPic(self.localImgPath,tweetMsg)

    def tweetedRecently(self):
        '''Check to determine whether pet has been tweeted recently'''
        queueLen = 50 # Number of recent posts to track
        bufferFile = scriptDir + '/recentTweets.dat'

        # Get recent tweets from local file if they exist
        if os.path.isfile(bufferFile):
            with open(bufferFile,'r') as f:
                tweetQueue = f.read().splitlines()
        else:
            tweetQueue = []            

        # Write back to buffer
        if self.profileURL in tweetQueue:
            return True

        else:
            tweetQueue.append(self.profileURL)
            while len(tweetQueue) > queueLen:
                tweetQueue.pop(0)
            with open(bufferFile,'w') as f:
                for item in tweetQueue:
                    f.write('{0}\n'.format(item))
            return False

def fetchPetango(animalType, shelterID):
    '''Find webpage on Petango'''

    numRequestAttempts = 5 # Number of times to attempt to query petango page

    if animalType.lower() == 'other':
        speciesVar = 0
    elif animalType.lower() == 'dog':
        speciesVar = 1
    elif animalType.lower() == 'cat':
        speciesVar = 2

    else: #Default case: dog
        speciesVar = 1

    #siteURL = 'http://www.petango.com/Forms/ShelterAnimals.aspx?z=&d=0&sh={0}&s={1}&b=0&g=All&size=All&c=All&a=All&dec=All&p=True&v=False&sid=0&zs=True&ht=False'.format(str(shelterID), str(speciesVar))

    siteURL = 'http://www.petango.com/Forms/ShelterAnimals.aspx'
    payload = {
        'sh': str(shelterID), # Which shelter?
        's': str(speciesVar), # Species: Other = '0', Dog = '1', Cat = '2'
        'p': 'True', # Has photo?
        #'z': '', # Zipcode
        #'d': '0', # Distance (in miles)
        #'b': '0', # Breed: 0 for all
        #'g': 'All', # Gender: 'All', 'M', or 'F'
        #'size': 'All', # Size: 'All', 'S', 'M', 'L', 'X'
        #'c': 'All', # Color: 'All', 'Black', 'White', 'Brown', 'Blue', 'Red'
        #'dec': 'All',
        #'v': 'False', # Has video?
        #'sid': '0',
        #'zs': 'True',
        #'ht': 'False'
    }

    # Get and parse page
    for attempt in range(numRequestAttempts):
        try:
            res = requests.get(siteURL, params=payload, timeout=5)
            break
        except:
            time.sleep(5) # Wait 5 seconds before trying again

    page = BeautifulSoup(res.text)

    return page

def parsePetango(page):
    '''Extract content from petango page'''
    # List of pets on page
    petList = []

    # Regex for extracting breed
    breedPattern = re.compile(r'\|\s*(.*)\s*')


    for animal in page.find_all('div',{'class':'asr-wrap-animal'}):

        # Initialize pet
        newPet = rescuePet()

        # Get name
        infoTag = animal.find('img',{'class':'pet-image'})
        petName = infoTag['alt']

        # Get photo URL
        photoURL = infoTag['src']
        photoURL = photoURL.replace('_TN1','') # Make sure not to get thumbnail

        # Get gender and breed
        breedTag = animal.find('li',{'class':'asr-animalname'})
        petGender = breedTag.find('strong').string
        breedType = breedPattern.search(breedTag.text)
        petBreed = breedType.group(1).strip()

        # Get URL to pet page
        linkTag = animal.find('div', {'id':'photo_div'}).find('a')
        profileURL= linkTag['href']

        # Set pet attributes
        newPet.name = petName
        newPet.gender = petGender
        newPet.breed = petBreed
        newPet.photoURL = photoURL
        newPet.profileURL = profileURL

        # Add pet to list
        petList.append(newPet)
    
    return petList

def main():
    global shelterDict
    luckyShelter = random.choice(shelterDict.values())

    curTime = datetime.datetime.now()
    curHour = curTime.hour

#    animalList = ['dog','cat']
    if (curHour % 2 == 1):
        luckySpecies = 'cat'
    elif (curHour % 2 == 0):
        luckySpecies = 'dog'

    # Get page
    petangoPage = fetchPetango(luckySpecies, luckyShelter)

    # Parse page to get list of animals
    petList = parsePetango(petangoPage)

    # Post first animal that hasn't been tweeted recently
    for pet in petList:
        if pet.tweetedRecently():
            continue
        else:
            pet.postTweet()
            print pet
            return

    # If all pets recently tweeted, select pet at random, post tweet
    pet = random.choice(petList)
    pet.postTweet()
    print pet

if __name__ == '__main__':
    main()
