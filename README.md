# CutePetsBmore [@CutePetsBmore](http://www.twitter.com/CutePetsBmore)
This is a bot that retrieves listings from Baltimore City animal shelters and tweets photos and profile links to eligible pets.

Inspired by previous work by [CutePetsDenver](https://github.com/codeforamerica/CutePetsDenver) and [CutePetsAustin](https://github.com/open-austin/CutePetsAustin).

The python script assumes that available animals are posted on the Petango service.

## Quickstart:

### On twitter:

1. Create the twitter account that will be used to post tweets
1. Log into this new account and navigate to http://apps.twitter.com
1. Create a new app with permission to post
1. Generate credentials (consumer keys and access tokens)

### In code:

1. Configure `credentials.py` by adding the keys generated by twitter
1. Install dependencies `pip install -r requirements.txt`
1. Modify `shelters.py` to include desired shelters from Petango (see below)
1. Tweet a singe pet listing: `python tweet_pet.py`

### Schedule regular tweeting with crontab (Linux):

1. From the command line, edit the crontab file: `crontab -e`
1. Schedule the script to run every hour using a line similar to: `0 * * * * /usr/bin/python (path_to_tweet_pet.py) > (path_to_log.log) 2>&1`

## Notes:

### Extension to other shelters

Presently data is retrieved for animals from two animal shelters (Baltimore Animal Rescue and Care Shelter and Baltimore Humane Society). However, modifying the script to retrieve animals from other shelters that use Petango is straightforward.

Use [Petango's shelter search](http://www.petango.com/Forms/Search.aspx) to identify a shelter of interest.  Choose to view animals from this shelter and you will notice a url of the form:

**"www.petango.com/Forms/ShelterAnimals.aspx?s=1&sh=###"**

The number contained in **"sh=###"** is the ID number of that shelter.  This number can be used to add or modify the dictionary contained in `shelters.py`.  

Presently, the `tweet_pet.py` retrieves a list of animals from each each of the shelters in `shelters.py` then tweets an animal at random from this list. As a result, modifying this script to access animals from other shelters is as simple as modifying this dictionary.

### Avoidance of duplicate tweets

The script `tweet_pet.py` attempts to avoid reposting tweets about the same animals.  This is done by tracking recent tweets in a buffer file created by the script.  The size of the buffer file can be adjusted by changing the value of the `NUM_RECENT_TWEETS` in `tweet_pet.py`.

### Addtional notes:

* I intended this to run on a Raspberry Pi running Raspbian.  The python script posts a new tweet each time it is called. Regularly scheduled posting is handled by `cron`.
