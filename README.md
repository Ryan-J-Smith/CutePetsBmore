# CutePetsBmore
This is a bot that retrieves listings from Baltimore City animal shelters and tweets photos and profile links to eligible pets

Inspired by previous work by [CutePetsDenver](https://github.com/codeforamerica/CutePetsDenver) and [CutePetsAustin](https://github.com/open-austin/CutePetsAustin).

## Quickstart:

1. Configure `credentials.py`
2. Install dependencies `pip install -r requirements.txt`
3. Tweet a random pet `python fetchPostParse.py`

## Addtional Notes:

I intended this to run on a Raspberry Pi running debian.  The python script posts a new tweet each time it is called. Regularly scheduled posting is handled by `cron`.
