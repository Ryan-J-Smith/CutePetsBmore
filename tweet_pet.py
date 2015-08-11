from bs4 import BeautifulSoup
import requests
import tweepy

import datetime
import os
import re
import random
import shutil
import time

from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from shelters import SHELTER_IDS

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOCAL_IMG_FILE = SCRIPT_DIR + '/pet_img.jpg'
RECENT_TWEETS_FILE = SCRIPT_DIR + '/recent_tweets.dat'
NUM_RECENT_TWEETS = 72 # Number of recent posts to track


class TwitterAPI(object):

    def __init__(self): 
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)
    
    def tweet(self, message):
        self.api.update_status(status=message)

    def tweet_with_img(self, img_path, msg):
        self.api.update_with_media(filename=img_path, status=msg)


class RescuePet(object):

    def __init__(self):
        self.name = None
        self.gender = None
        self.breed = None
        self.photo_url = None
        self.profile_url = None
    
    def __str__(self):
        name_str = 'Name: {0}\n'.format(self.name)
        gender_str = 'Gender: {0}\n'.format(self.gender)
        breed_str = 'Breed: {0}\n'.format(self.breed)
        photo_str = 'Photo URL: {0}\n'.format(self.photo_url)
        profile_str = 'Profile URL: {0}'.format(self.profile_url)
        full_str = name_str + gender_str + breed_str + photo_str + profile_str
        return full_str

    def get_image(self):
        '''Download image for pet, write to local file'''
        res = requests.get(self.photo_url, stream=True)
        with open(LOCAL_IMG_FILE, 'wb') as f:
            shutil.copyfileobj(res.raw, f)

    def post_tweet(self):
        '''Get image, format tweet, post tweet'''
        twitter = TwitterAPI()
        self.get_image()
        tweetMsg = 'Hi! My name is {0}. I\'m a {1} {2}. Adopt me at: {3}'.format(self.name, self.gender, self.breed, self.profile_url)
        twitter.tweet_with_img(LOCAL_IMG_FILE, tweetMsg)

    def tweeted_recently(self):
        '''Check to determine whether pet has been tweeted recently''' 
        return self.profile_url in get_recent_tweets()

    def update_recent_tweets(self):
        '''Write profile URL to list of recent tweets'''       
        recent_tweets = get_recent_tweets()
        recent_tweets.append(self.profile_url)

        while len(recent_tweets) > NUM_RECENT_TWEETS:
            recent_tweets.pop(0)
        
        with open(RECENT_TWEETS_FILE, 'w') as f:
            for item in recent_tweets:
                f.write('{0}\n'.format(item))


def get_recent_tweets():
    '''Return list of URLs to recently tweeted pets'''
    # Get recent tweets from local file if they exist
    if os.path.isfile(RECENT_TWEETS_FILE):
        with open(RECENT_TWEETS_FILE, 'r') as f:
            recent_tweets = f.read().splitlines()
    else:
        recent_tweets = []

    return recent_tweets


def fetch_petango(species, shelter_id):
    '''Find webpage on Petango.  Return HTML content.'''
    SITE_URL = 'http://www.petango.com/Forms/ShelterAnimals.aspx'
    NUM_REQUEST_ATTEMPTS = 5 # Number of times to attempt to query petango page

    if species.lower() == 'other':
        species_id = 0
    elif species.lower() == 'dog':
        species_id = 1
    elif species.lower() == 'cat':
        species_id = 2
    else: #Default case: dog
        species_id = 1

    payload = {
        'sh': str(shelter_id), # Which shelter?
        's': str(species_id), # Species: Other = '0', Dog = '1', Cat = '2'
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
    for attempt in range(NUM_REQUEST_ATTEMPTS):
        try:
            res = requests.get(SITE_URL, params=payload, timeout=5)
            break
        except:
            time.sleep(5) # Wait 5 seconds before trying again

    page = BeautifulSoup(res.text)
    return page


def parse_petango(page):
    '''Extract content from petango page, return a list of RescuePet objects'''
    pet_list = []

    # Regex for extracting breed
    breedPattern = re.compile(r'\|\s*(.*)\s*')

    for animal in page.find_all('div', {'class':'asr-wrap-animal'}):

        # Initialize pet
        newPet = RescuePet()

        # Get name
        infoTag = animal.find('img', {'class':'pet-image'})
        petName = infoTag['alt']

        # Get photo URL
        photo_url = infoTag['src']
        photo_url = photo_url.replace('_TN1', '') # Make sure not to get thumbnail

        # Get gender and breed
        breedTag = animal.find('li', {'class':'asr-animalname'})
        petGender = breedTag.find('strong').string
        breedType = breedPattern.search(breedTag.text)
        petBreed = breedType.group(1).strip()

        # Get URL to pet page
        linkTag = animal.find('div', {'id':'photo_div'}).find('a')
        profile_url= linkTag['href']

        # Set pet attributes
        newPet.name = petName
        newPet.gender = petGender
        newPet.breed = petBreed
        newPet.photo_url = photo_url
        newPet.profile_url = profile_url

        # Add pet to list
        pet_list.append(newPet)
    
    return pet_list


def main():
    pet_tweeted = False

    # Alternate between posting cats and dogs
    cur_hour = datetime.datetime.now().hour
    if (cur_hour % 2 == 1):
        species = 'cat'
    elif (cur_hour % 2 == 0):
        species = 'dog'
    else:
        species = 'dog'

    # Get a page of pets for each shelter in shelters.py
    pet_list = []
    for shelter in SHELTER_IDS.values():
        petango_page = fetch_petango(species, shelter)
        shelter_pets = parse_petango(petango_page)
        pet_list.extend(shelter_pets)

    # Tweet a random pet from list
    random.shuffle(pet_list)
    for pet in pet_list:
        if not pet.tweeted_recently():
            pet.post_tweet()
            pet.update_recent_tweets()
            pet_tweeted = True
            break

    # If all pets recently tweeted, select pet at random, post tweet
    if not pet_tweeted:
        pet = random.choice(pet_list)
        pet.post_tweet()
        pet_tweeted = True

    print pet

if __name__ == '__main__':
    main()

