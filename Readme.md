# Strava2Geovelo

This script allows to transfer your activities from Strava to Geovelo.

## Why

The geovelo website allows the upload of GPX files (geolocation info of your activities), but only one by one. You cannot upload multiple GPX files at once.
So I made this script that automatically does it one by one for all the activities in your Strava data export.

## How to use

### Download your Strava data

First you'll need to export your activities from Strava. You can get it on this page : https://www.strava.com/athlete/delete_your_account by clicking "Request your archive".
You will then receive an email with a link to download your .zip archive containing all your data.
There are two files/folder of interest :
- `activities.csv `: lists all your activities
- the `activities` folder : contains all gpx files


### Setup

Install playwright :
```
pip install playwright
playwright install
```

Write your account info (email and password) in the the `user_data.py` file.

Extract your whole Strava archive wherever you want, but remember its path. Write it in the `user_data.py` file.

### Execute the script

Launch the script :
```
python3 main.py
```
This will launch a web browser that will automatically navigate to the geovelo website and performs the steps to upload your activities. This may take some time to fully execute.

### Known errors

You may encounter 'timeout errors' during execution, that are solved by running the script again.
If you want to save time, you can modify the `activities.csv` file to remove the activities already uploaded, so the script will not waste time retrying.
