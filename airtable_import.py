"""
Copy Kellogg Prof data into an Airtable DB for our Research Support CRM
"""
from google_sheets import GoogleSheets
from web_util import get_json, get_tree, css_select
import getpass
import requests
import json

def airtable_import():
    # load kellogg prof data
    gs = GoogleSheets()
    profs = gs.read_profs()
    profs = [p for p in profs if p.school=="Northwestern"]
    # prompt for airtable api key
    airtable_API_key = getpass.getpass("Enter your AirTable API key: ")

    # get iterate through all customers in airtable
    response = get_json(
        "https://api.airtable.com/v0/apptzGHIQmdYv9F1i/Customers?maxRecords=999&view=Grid%20view&api_key="
        + airtable_API_key)
    for customer in response["records"]:
        if "Professor" in customer["fields"]["Role"]:
            print("found professor: " + customer["fields"]["Full Name"])
            netId = customer["fields"]["NetId"]
            prof = [p for p in profs if netId in p.faculty_directory_url][0]
            # update the professor's airtable record
            update_body = {
                "fields": {
                    "Directory URL": prof.faculty_directory_url,
                    "Photo": [{
                        "url": get_photo_url(prof),
                        "filename": netId + "_headshot.jpg"
                    }],
                    "CV": [{
                        "url": prof.cv_url,
                    }]
                }
            }
            if prof.google_scholar_url:
                update_body["fields"]["Scholar URL"] = prof.google_scholar_url
            r = requests.patch("https://api.airtable.com/v0/apptzGHIQmdYv9F1i/Customers/" + customer["id"],
                               data=json.dumps(update_body),
                               headers={"Content-type": "application/json",
                                        "Authorization": "Bearer " + airtable_API_key})
            if r.status_code != 200:
                print("ERROR: response code %d" % r.status_code)
                print(r.text)


def get_photo_url(prof):
    img_tag = css_select(get_tree(prof.faculty_directory_url), "img.profileImg")[0]
    return "https://www.kellogg.northwestern.edu" + img_tag.get("src")


if __name__ == '__main__':
    airtable_import()