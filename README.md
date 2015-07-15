# CutePetsBmore
This is a bot that retrieves listings from Baltimore City animal shelters and tweets photos and profile links to eligible pets.

Inspired by previous work by [CutePetsDenver](https://github.com/codeforamerica/CutePetsDenver) and [CutePetsAustin](https://github.com/open-austin/CutePetsAustin).

The python script assumes that available animals are posted on the Petango service.

## Quickstart:

1. Configure `credentials.py`
2. Install dependencies `pip install -r requirements.txt`
3. Tweet a random pet `python fetchPostParse.py`

### Extension to other shelters

Presently data is retrieved for animals from a single animal shelter (Baltimore Animal Rescue and Care Shelter, Inc.). However, modifying the script to retrieve animals from other shelters that use petango is straightforward.

Use [Petango's shelter search](http://www.petango.com/Forms/Search.aspx) to identify a shelter of interest.  Choose to view animals from this shelter and you will notice a url of the form:

**"www.petango.com/Forms/ShelterAnimals.aspx?s=1&sh=###"**

The number contained in **"sh=###"** is the ID number of that shelter.  This number can be used to add or modify the `shelterDicts` dictionary.  Presently, the script chooses a shelter ID at random from this dictionary to fetch animals from. As a result, modifying this script to apply to other shelters is as simple as modifying this dictionary.

### Avoidance of duplicate tweets

The script attempts to avoid reposting tweets about the same animals.  This is done by tracking recent tweets in a buffer file created by the script.  The size of the buffer file can be adjusted by changing the value of the `queueLen` variable.

## Addtional notes:

* I intended this to run on a Raspberry Pi running debian.  The python script posts a new tweet each time it is called. Regularly scheduled posting is handled by `cron`.
