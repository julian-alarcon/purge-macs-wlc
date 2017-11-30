# Purge old MAC's devices on Cisco WLC monitored by Graylog2

    Author: Julian Alarcon
    Language: XML
    License: GPLv3

This Python script is able to check a list of MACs, previously exported from Cisco Wireless Controller (WLC) with the command ```show macfilter summary```, search them in Graylog2 logs and if the MAC's device is not found in an specific amount of backwards days then it prints two files, one with the mac address and another similar but with the command for the WLC to delete it using the command ```config macfilter delete```

## Things needed previously to use this script

* You need to have one Cisco WLC that centralize the administration of your wireless networks, and you should be using mac filtering for security (Disclaimer at the end of README).

* Graylog2 installed and the WLC configured to send logs to this device. (AS Graylog2 uses Elasticsearch, maybe this scripts also works for ELK platforms, but I can't confirm if that's is possible). [Graylog Website](https://graylog.org/)

* Administration access to WLC and API access to Graylog2 service.

* Enough days of logs in Graylog2 from the WLC, as this is the way to check if any device was connected to the wireless network.

* Python version >=2.7 installed (this script is Python 3.6 compatible)

* Export file with current configured MACs. You can use the command ```show macfilter summary``` and clean it to remove other information not related with MACs as this example:

> You can use this command ```config paging disable``` to disable paging and get all the MAC output faster.

```text
00:da:14:6c:98:68           9              unknown           PDEVICE07 jdoe 20160905
ac:bd:02:5e:22:91           8              unknown           PDEVICE09 janed 20171030
```

> Recommendation: Always make a backup of your WLC configuration. I'm not responsible of any damage in your infrastructure.

## Script usage

Once you download the script ```verify-macs.py``` you have to run it giving the specifics arguments.

```bash
python verify-macs.py -i GraylogServerIP -o PortUsedByGraylogAPI -d NumberOfBackwardsDays -u GraylogUserWithPermissions -p GraylogPasswordOfUser -f text_file_with_macs.txt
```

Example:

```bash
python verify-macs.py -i 10.0.0.100 -o 9000 -d 90 -u admin -p myp4ss -f macs.txt
```

Once you run the script, you will get two files, ```macs_to_remove.txt``` and ```commands_to_remove_macs.txt```.

The first only have the devices MAC that had no record of being connected to the WiFi networks, only useful if you need to have a record of the MACs that you will delete.

The second is a similar file of MACs but with the prefix ```config macfilter delete```. Useful if you want to copy it and paste it in the WLC ssh console. This way you will delete all the old MACs.

You can also find a little help text for usage using the ```-h``` option.

```bash
user@computer:~/Purge_MACs_WLC$ python verify-macs.py -h
usage: verify-macs.py [-h] [-i GRAYLOG_IP] [-o GRAYLOG_API_PORT]
                      [-d BACKWARDS_TIME] [-u GRAYLOG_USER]
                      [-p GRAYLOG_PASSWORD] [-f FILE_PATH]

Find old devices in Graylog2 configured in WLC

optional arguments:
  -h, --help           show this help message and exit
  -i GRAYLOG_IP        The IP of Graylog2 Server
  -o GRAYLOG_API_PORT  The port of Graylog2 Server API
  -d BACKWARDS_TIME    The number of days back to check MAC devices in
                       Graylog2
  -u GRAYLOG_USER      The Graylog2 user with permissions to read API
  -p GRAYLOG_PASSWORD  The Graylog2 password of the user with permissions to
                       read API
  -f FILE_PATH         The path/name of the text file with MACs
```

## Use output to purge old MAC's devices from WLC

Open the file ```macs_to_remove.txt``` and check all the found MACs.

Then open the ```commands_to_remove_macs.txt``` file, open an SSH session to your WLC and paste the text.

This is an example of the execution of the pasted command

```cisco
user@computer:~$ ssh admin@10.80.33.50

(Cisco Controller)
User: admin
Password:*********************
(Cisco Controller) >

(Cisco Controller) >config macfilter delete 00:08:22:96:aa:aa

Deleted MAC Filter 00:08:22:96:aa:aa

(Cisco Controller) >
```

## JSON example of Graylog2 API output

This is a Json example of the output of a MAC that was found. Check the value of ```count```. As it's different of ```0```, this MAC won't be registered for deletion.

```json
{
  "time": 305,
  "count": 2413,
  "sum": 3640714627480026,
  "sum_of_squares": 5.493093751501996e+27,
  "mean": 1508791805835.0708,
  "min": 1504213733195,
  "max": 1511900368148,
  "variance": 5534262846660542000,
  "std_deviation": 2352501402.0528326,
  "built_query": "{\n  \"from\" : 0,\n  \"query\" : {\n    \"bool\" : {\n      \"must\" : {\n        \"query_string\" : {\n          \"query\" : \"\\\"18:13:01:b3:58:53\\\"\",\n          \"allow_leading_wildcard\" : true\n        }\n      },\n      \"filter\" : {\n        \"bool\" : {\n          \"must\" : {\n            \"range\" : {\n              \"timestamp\" : {\n                \"from\" : \"2017-08-30 21:41:00.213\",\n                \"to\" : \"2017-11-28 21:41:00.213\",\n                \"include_lower\" : true,\n                \"include_upper\" : true\n              }\n            }\n          }\n        }\n      }\n    }\n  },\n  \"aggregations\" : {\n    \"gl2_filter\" : {\n      \"filter\" : {\n        \"bool\" : {\n          \"must\" : {\n            \"range\" : {\n              \"timestamp\" : {\n                \"from\" : \"2017-08-30 21:41:00.213\",\n                \"to\" : \"2017-11-28 21:41:00.213\",\n                \"include_lower\" : true,\n                \"include_upper\" : true\n              }\n            }\n          }\n        }\n      },\n      \"aggregations\" : {\n        \"gl2_value_count\" : {\n          \"value_count\" : {\n            \"field\" : \"timestamp\"\n          }\n        },\n        \"gl2_extended_stats\" : {\n          \"extended_stats\" : {\n            \"field\" : \"timestamp\"\n          }\n        },\n        \"gl2_field_cardinality\" : {\n          \"cardinality\" : {\n            \"field\" : \"timestamp\"\n          }\n        }\n      }\n    }\n  }\n}",
  "cardinality": 2295
}
```

This is another example of the JSON output of a MAC that **wasn't** found. Check the value of ```count```. It's ```0``` so this MAC was not found in the Graylog2 logs in the specified time. So it's a candidate to be removed:

```json
{
  "time": 65,
  "count": 0,
  "sum": "NaN",
  "sum_of_squares": "NaN",
  "mean": "NaN",
  "min": "NaN",
  "max": "NaN",
  "variance": "NaN",
  "std_deviation": "NaN",
  "built_query": "{\n  \"from\" : 0,\n  \"query\" : {\n    \"bool\" : {\n      \"must\" : {\n        \"query_string\" : {\n          \"query\" : \"\\\"fc:de:48:ee:bd:8a\\\"\",\n          \"allow_leading_wildcard\" : true\n        }\n      },\n      \"filter\" : {\n        \"bool\" : {\n          \"must\" : {\n            \"range\" : {\n              \"timestamp\" : {\n                \"from\" : \"2017-08-30 21:45:43.894\",\n                \"to\" : \"2017-11-28 21:45:43.894\",\n                \"include_lower\" : true,\n                \"include_upper\" : true\n              }\n            }\n          }\n        }\n      }\n    }\n  },\n  \"aggregations\" : {\n    \"gl2_filter\" : {\n      \"filter\" : {\n        \"bool\" : {\n          \"must\" : {\n            \"range\" : {\n              \"timestamp\" : {\n                \"from\" : \"2017-08-30 21:45:43.894\",\n                \"to\" : \"2017-11-28 21:45:43.894\",\n                \"include_lower\" : true,\n                \"include_upper\" : true\n              }\n            }\n          }\n        }\n      },\n      \"aggregations\" : {\n        \"gl2_value_count\" : {\n          \"value_count\" : {\n            \"field\" : \"level\"\n          }\n        },\n        \"gl2_extended_stats\" : {\n          \"extended_stats\" : {\n            \"field\" : \"level\"\n          }\n        },\n        \"gl2_field_cardinality\" : {\n          \"cardinality\" : {\n            \"field\" : \"level\"\n          }\n        }\n      }\n    }\n  }\n}",
  "cardinality": 0
}
```

I tested in Ubuntu 17.10 with Python 2.7.14 and Python 3.6.3. It should work in Windows and macOS. Also the firmware version of the WLC was 8.3.132.0.

## Documentation

[Graylog API documentation](http://docs.graylog.org/en/2.3/pages/configuration/rest_api.html)
[Cisco WLC Command Reference](https://www.cisco.com/c/en/us/td/docs/wireless/controller/8-3/command-reference/b-cr83/preface.html)

> BTW: I know that MAC filtering is a **poor security solution** for wireless authorization/authentication, it's really easy to spoof an authorized MAC. But, this is business. **¯\\_(ツ)_/¯**