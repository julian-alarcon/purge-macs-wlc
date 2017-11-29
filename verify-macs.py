"""
This Python script gets a file filled with MAC address from Cisco WLC and search them in
Graylog2 using API in an specific time. If the MAC adress is not found then
it writes two files, one eith the MAC and another with the command line needed
to remove the MAC address from the Cisco WLC controller.
"""
__author__ = "Julian Alarcon"
__copyright__ = "Copyright (C) 2017 Julian Alarcon"
__license__ = "GPLv3"
__version__ = "1.0"

#!/usr/bin/env python
import argparse
import json
import requests

parser = argparse.ArgumentParser(description='Python script to find old devices in Graylog2 configured in WLC')
parser.add_argument('-i', dest='graylog_ip', type=str,
                    help='The IP of Graylog2 Server')
parser.add_argument('-o', dest='graylog_api_port', type=int,
                    help='The port of Graylog2 Server API')
parser.add_argument('-d', dest='backwards_time', type=int,
                    help='The number of days back to check MAC devices in Graylog2')
parser.add_argument('-u', dest='graylog_user', type=str,
                    help='The Graylog2 user with permissions to read API')
parser.add_argument('-p', dest='graylog_password', type=str,
                    help='The Graylog2 password of the user with permissions to read API')
parser.add_argument('-f', dest='file_path', type=str,
                    help='The path/name of the text file with MACs')
args = parser.parse_args()
parser.parse_args()

args.backwards_time = args.backwards_time*86400 # Convert backwards time to seconds, (days*24*60*60)
macs_file = open(args.file_path, "r")
lines_from_file = macs_file.readlines()
macs_to_remove = open("macs_to_remove.txt","w")
commands_to_remove_macs = open("commands_to_remove_macs.txt","w")
for mac_address in lines_from_file:
    mac_address_query = mac_address[:17]
    mac_address_query = mac_address_query.replace(":", "%5C%3A")
    # The next url string is build using Graylog2 API/Elasticsearch/Lucene search syntax
    # http://docs.graylog.org/en/2.3/pages/configuration/rest_api.html
    # Using API for Stats of Search/Relative Message search
    graylog_url = ("http://" + args.graylog_ip
                   + ":"
                   + str(args.graylog_api_port)
                   + "/api/search/universal/relative/stats?field=timestamp&query=%22"
                   + mac_address_query
                   + "%22&&range="
                   + str(args.backwards_time))
    json_response = requests.get(graylog_url, auth=(args.graylog_user, args.graylog_password))
    first_json_section = json_response.json()
    second_json_section = json.loads(first_json_section['built_query'])
    if (first_json_section['count']) > 0:
        macs_to_remove.write(mac_address[:17]+"\n")
        commands_to_remove_macs.write("config macfilter delete " + mac_address[:17]+"\n")
        # Print the URL output used to check the MAC address.
        # Just in case that you need to check directly the all the API output
        #print (graylog_url)
        # Print the specific item searched item in JSON response.
        # This is other method of getting the MAC address result
        #print (second_json_section['query']['bool']['must']['query_string']['query'])
macs_file.close()
macs_to_remove.close()
commands_to_remove_macs.close()
