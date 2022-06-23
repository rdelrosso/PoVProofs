#!/usr/bin/env python3
##
# Script to continuously inserts new documents into the MongoDB database/
# collection 'test.records'
#
# Prerequisite: Install latest PyMongo driver, e.g:
#   $ sudo pip3 install pymongo
#
# For usage details, run with no params (first ensure script is executable):
#   $ ./continuous-insert.py
##
import sys
import random
import time
import datetime
import pymongo
import certifi


####
# Main start function
####
def main():
    print('')

    if len(sys.argv) < 4:
        print('Error: Insufficient command line parameters provided')
        print_usage()
    else:
        username = sys.argv[1].strip()
        password = sys.argv[2].strip()
        host = sys.argv[3].strip()
        retry = False

        if (len(sys.argv) >= 5):
            retry = True if (sys.argv[4].strip().lower() == 'retry') else False

        peform_inserts(username, password, host, retry)


####
# Perform the continuous database insert workload, sleeping for 10 milliseconds
# between each insert operation
####
def peform_inserts(username, password, host, retry):
    mongodb_url = f'mongodb+srv://{username}:{password}@{host}/test'\
                  f'?retryWrites={(str(retry)).lower()}'
    print(f'Connecting to:\n {mongodb_url}\n')
    connection = pymongo.MongoClient(mongodb_url,tls=True, tlsCAFile=certifi.where())
    connection.test.records.drop()
    print('Inserting records continuously...')
    connect_problem = False
    count = 0

    while True:
        try:
            if (count % 30 == 0):
                print(f'{datetime.datetime.now()} - INSERT {count}')

            connection.ups.shipmentTrackings.insert_one({
 
  "tracking_number": {
    "$numberLong": "63019142490811"
  },
  "customerID": 904,
  "package_rfid": "gsdbuw6d78w9di9jwndw567895678945678956789678900099787766555676754344567788899900000s0998765545rwdy6w778wd89wbhwdhbwbhwyyhdjwhbjwj",
  "status": "AtDestinationWarehouse",
  "scheduled_delivery": {
    "$date": {
      "$numberLong": "1161722462478"
    }
  },
  "shipped_from": {
    "country": "KW",
    "state": "NE",
    "city": "Ucubote",
    "postcode": "45974",
    "street": "Huved Park",
    "location": {
      "type": "Point",
      "coordinates": [
        -115.12742,
        37.48737
      ]
    },
    "apartment_suite": 574,
    "department": "dept"
  },
  "shipped_by_email": "mar@ojofuk.fm",
  "shipment_reference": "jefjeweodewk ewdkedooewkopew",
  "shipped_to": {
    "country": "DE",
    "state": "CAM",
    "city": "Dahedat",
    "postcode": "53769",
    "street": "Kivug Manor",
    "location": {
      "type": "Point",
      "coordinates": [
        -102.15219,
        35.17973
      ]
    },
    "apartment_suite": 249,
    "department": "dept"
  },
  "shipped_to_email": "jinvib@voj.gov",
  "shipping_date": {
    "$date": {
      "$numberLong": "1543705952527"
    }
  },
  "billing_date": {
    "$date": {
      "$numberLong": "1565821966820"
    }
  },
  "service_type": "standard",
  "weight": 785,
  "dimensions": {
    "cm": "110,112,1211",
    "oversized": "Yes,No"
  },
  "declared_value": 58327,
  "multiple_packages_num": 16,
  "tracking_history": [
    {
      "Date": {
        "$date": {
          "$numberLong": "1112728793156"
        }
      },
      "Time": "18:54:54",
      "Location": "Douane",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -93.65649,
          39.29808
        ]
      },
      "public_scan": "out on delivery",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "973401677490"
        }
      },
      "Time": "18:54:54",
      "Location": "Kent, UK",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -116.27578,
          39.91789
        ]
      },
      "private_scan": "unloading from plane",
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1407759421183"
        }
      },
      "Time": "18:54:54",
      "Location": "Kent, UK",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -107.70404,
          40.99453
        ]
      },
      "private_scan": "unloading from plane",
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "924301459148"
        }
      },
      "Time": "18:54:54",
      "Location": "MXP Airport",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -95.63374,
          40.05517
        ]
      },
      "private_scan": "unloading from plane",
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1282974073991"
        }
      },
      "Time": "18:54:54",
      "Location": "Kent, UK",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -110.2134,
          37.63536
        ]
      },
      "public_scan": "out on delivery",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1648979364424"
        }
      },
      "Time": "18:54:54",
      "Location": "Douane",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -117.74687,
          34.23842
        ]
      },
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1201854093864"
        }
      },
      "Time": "18:54:54",
      "Location": "Kent, UK",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -111.57334,
          33.27398
        ]
      },
      "public_scan": "departure scan",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1146735517039"
        }
      },
      "Time": "18:54:54",
      "Location": "Kent, UK",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -115.11775,
          34.1775
        ]
      },
      "public_scan": "destination scan",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1022543802834"
        }
      },
      "Time": "18:54:54",
      "Location": "LAX Warehouse",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -90.01952,
          35.71713
        ]
      },
      "public_scan": "export scan",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1154616301476"
        }
      },
      "Time": "18:54:54",
      "Location": "MXP Airport",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -103.81306,
          36.56752
        ]
      },
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1641616103331"
        }
      },
      "Time": "18:54:54",
      "Location": "Douane",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -111.83101,
          36.75903
        ]
      },
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1375919407602"
        }
      },
      "Time": "18:54:54",
      "Location": "LAX Warehouse",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -86.98428,
          41.55512
        ]
      },
      "public_scan": "departure scan",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1110546509741"
        }
      },
      "Time": "18:54:54",
      "Location": "Douane",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -99.83377,
          37.89156
        ]
      },
      "public_scan": "customs entry",
      "internal_activity": "no"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1145927414701"
        }
      },
      "Time": "18:54:54",
      "Location": "Kent, UK",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -115.45444,
          39.08548
        ]
      },
      "private_scan": "loading from",
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1065781174986"
        }
      },
      "Time": "18:54:54",
      "Location": "Douane",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -95.67394,
          36.18344
        ]
      },
      "private_scan": "unloading from plane",
      "internal_activity": "Yes"
    },
    {
      "Date": {
        "$date": {
          "$numberLong": "1299709864907"
        }
      },
      "Time": "18:54:54",
      "Location": "LAX Warehouse",
      "GPS Location": {
        "type": "Point",
        "coordinates": [
          -86.81194,
          39.08634
        ]
      },
      "private_scan": "loading from",
      "internal_activity": "Yes"
    }
  ],
  "additional_features": {
    "carbon_neutral": "Yes,No",
    "saturday_delivery": "Yes,No",
    "third_party_delivery": "Yes,No",
    "additional insurance": "Yes,No"
  },
  "vat_number": "BG999999999"
})
            count += 1

            if (connect_problem):
                print(f'{datetime.datetime.now()} - RECONNECTED-TO-DB')
                connect_problem = False
            else:
                time.sleep(0.01)
        except KeyboardInterrupt:
            print
            sys.exit(0)
        except Exception as e:
            print(f'{datetime.datetime.now()} - DB-CONNECTION-PROBLEM: '
                  f'{str(e)}')
            connect_problem = True


####
# Print out how to use this script
####
def print_usage():
    print('\nUsage:')
    print('$ ./continuous-insert.py <username> <password> <host> <retry>')
    print('\nExample: (run script WITHOUT retryable writes enabled)')
    print('$ ./continuous-insert.py main_user mypsswd '
          'testcluster-abcd.mongodb.net')
    print('\nExample: (run script WITH retryable writes enabled):')
    print('$ ./continuous-insert.py main_user mypsswd '
          'testcluster-abcd.mongodb.net retry')
    print()


####
# Main
####
if __name__ == '__main__':
    main()
