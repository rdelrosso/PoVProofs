# ENCRYPT-FIELDS

__Ability for a client application to encrypt specific database fields at the application tier using encryption keys only accessible to the client, thus preventing any database/server-side access to the data__

__SA Maintainer__: [Matthew Aylard](mailto:matthew.aylard@mongodb.com) <br/>
__Time to setup__: 30 mins <br/>
__Time to execute__: 15 mins <br/>



---
## Description

This proof shows how MongoDB can be configured to allow applications to leverage Client-Side Field Level Encryption (CS-FLE) a feature released in MongoDB 4.2. CS-FLE allows applications to encrypt fields in documents prior to transmitting data over the wire to the server.

MongoDB 4.2 Enterprise supports *automatic* field level encryption using JSON schema syntax. Applications must modify only the driver client object configuration code to include automatic encryption settings. All read/write operations to a cluster via the encryption-configured client are automatically encrypted and decrypted using the predefined automatic encryption rules. Application code that uses the MongoDB standard CRUD operations does not require any additional modification to beging to leverage CS-FLE.

Only applications with access to the correct encryption keys and database can encrypt and write / decrypt and read the protected data. 

Consider the following document -

```json
{
	"_id" : ObjectId("5db2e8bf6bf42af9e6753949"),
	"firstName" : "Alan",
	"lastName" : "Turing",
	"ssn" : "901-01-0001",
	"address" : {
		"street" : "123 Main",
		"city" : "Omaha",
		"zip" : "90210"
	},
	"contact" : {
		"mobile" : "202-555-1212",
		"email" : "alan@example.com"
	}
}
```

With client-side field level encryption, the application can specifically encrypt sensitive information like the `ssn`, `mobile` and `email` fields. Encrypted fields are transmitted to and from the database as [`binary data`](https://docs.mongodb.com/manual/reference/mongodb-extended-json-v1/#data_binary) with [`subtype 6`](https://github.com/mongodb/specifications/blob/master/source/client-side-encryption/subtype6.rst).

```json
{
	"_id" : ObjectId("5db2e8bf6bf42af9e6753949"),
	"firstName" : "Alan",
	"lastName" : "Turing",
	"ssn" : BinData(6,"AZL+SIFHKke4lZCrTkhK0fcCQoJq+YHYsefD55a27QNzgwHh0Yx5ejF+d4Kui+Hqda+EQtmNkSXFhCgg8MP96OdkCIGrqimoy+mUuBwBjTXecHxF0gmrGu0YiAKrUesIna8="),
	"address" : {
		"street" : "123 Main",
		"city" : "Omaha",
		"zip" : "90210"
	},
	"contact" : {
		"mobile" : BinData(6,"AS3AOd7ykkYLiilbgenofjoC5nKMxMB7yeAyL0WfvoRUghg2KGruxvPkVbeHMUzkXlZCewRXwxUnsmhSV6WiI4Vls0mtmtayWHYJnPtCWDXOe63h+0lB5H/0Dh2odAapQsw="),
		"email" : BinData(6,"AS3AOd7ykkYLiilbgenofjoC05RkHoTQurknMDYONRltSbegE2CWLRAkfAjU2XDsHpji6ADdL70uAhEQiUn2sANeiCKjY+w4wzO8D6sbXZrR68DVTQfTgrTV2Xm/aLL1Hzg=")
	}
}
```

For this proof we will create a MongoDB 4.2 Enterprise cluster in Atlas, connect to it via the Mongo 4.2-ent shell (leveraging the built in javascript engine) and configure the following:

- The key vault namespace (`demoFLE.keystore`) used to store encrypted data keys
- A Local Master encryption key file to use
- Per-field encryption rules using JSON schema syntax
  - one key for the `ssn`
  - another key for the `mobile`and `email`

We will then insert some documents and validate the fields contain encrypted data. We will also validate that a client, without knowledge of the keys, only sees cipher text in both the shell and MongoDB Compass for the affected fields.

Applications with [`read`](https://docs.mongodb.com/manual/reference/built-in-roles/#read) access to the key vault collection can retrieve data keys by querying the collection. However, only applications with access to the Customer Master Key (CMK) used to encrypt a data key can use that key for encryption or decryption.

Note, using a 'Local' Master encryption key is not recommended for production use. If you prefer to use AWS KMS service for the CMK, follow this separate article. For complete documentation on data key management, see [Manage Client-Side Encryption Data Keys](https://docs.mongodb.com/manual/tutorial/manage-client-side-encryption-data-keys/).

---
## Setup

**1. Configure Laptop**

- Ensure MongoDB version **4.2+ enterprise** is already installed on your computer, mainly to enable MongoDB command line tools to be used (no MongoDB databases will be run on the laptop for this proof)
   - _NOTE_: MongoDB Enterprise is needed for the automatic association and use of encryption keys, if Community is used you would have to explicitly define for each CRUD operation the use of encryption features and which key to use. MongoDB 4.2 Enterprise extends 4.2-compatible driver encryption support to include [automatic field level encryption](https://docs.mongodb.com/manual/core/security-client-side-encryption/#field-level-encryption-automatic) using [JSON schema syntax](https://docs.mongodb.com/manual/reference/security-client-side-automatic-json-schema/#field-level-encryption-json-schema). Please note the types of encryption that can be [used](https://docs.mongodb.com/manual/core/security-client-side-encryption/#encryption-algorithms).
- [Download](https://www.mongodb.com/download-center/compass) and install Compass on your laptop

**2. Configure Atlas Environment**

- Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
- In the project's Security tab, choose to add a new user called **main_user**, and for **User Privileges** specify **Atlas Admin** (make a note of the password you specify)
- Create an **M10** based 3 node replica-set in a single cloud provider region of your choice with default settings except __specify the MongoDB version to be 4.2__
- In the Security tab, add a new **IP Whitelist** for your laptop's current IP address

**3. Generate a Locally Managed Key to be Used as the Master Key as our Key Management Service (KMS)**

This key will be used for storing and retrieving a Customer Master Key (CMK)

- Configuring client-side field level encryption for a locally managed key requires specifying a base64-encoded 96-byte string with no line breaks. In the command line terminal of your laptop, run the following to create a file with the javascript environment variable ready to be used later

```javascript
// For Linux & Mac:
echo $(head -c 96 /dev/urandom | base64 | tr -d '\n')

// For Win 10/2016+:
powershell -command "[Convert]::ToBase64String((1..96|%{[byte](Get-Random -Max 256)}))"

// Note: Get-Random in Windows 10/Server 2016 uses a CSPRNG seed by default. Prior to PS 5.1, seed was system clock.
```

- The output should be around 100 ASCII characters, use these generated characters to create a local key file

-  Choose a suitable location to create this key file on your local system, and name the file `mykey.env` . The contents of the file need to contain the value `env.localDevKey = "<CMK generated above>"`. We will use this later in the proof. **You will need to run the MongoDB Shell from this location** unless you amend the script to specify the location of this file.

  *Example: `mykey.env`*

```javascript
  env.localDevKey = "eye7rhjSIGg52D1weIrCSz7VMdkdsds1raOsE0k9tdecDoUr5P9v7ZrvXGQHe+s8XaePUpaJsIlWL4Kxbv5EDejfcrDKZ5fGGaNAOmOcaZiZ7eVHkYxdWhdCWui3cvE5"
```

  

**WARNING** - *A local key file like this should ONLY be used for development & testing, never in production. A KMS should be used in production.*

**4. Start the MongoDB Shell and confirm successful connection to your Atlas Cluster**

- In the Atlas console, for the database cluster you deployed, click the **Connect button**, select **Connect with the Mongo Shell**, and in the **Run your connection string in your command line** section copy the connection command line - make a note of this connection command line

- From a command line terminal on your laptop, in the same folder as the key file, launch the MongoDB Shell using the Atlas cluster connection command you just captured, and when prompted, provide the password that you specified in an earlier setup step (keep the Mongo Shell open ready for the _Execution_ steps), for example:

  ```
  mongo "mongodb+srv://testcluster-abcde.mongodb.net" --username main_user 
  ```

---
## Execution

**While in the MongoDB shell connected to your Atlas cluster the next series of steps will involve copy and pasting various JavaScript code**. Note that the MongoDB shell needs to be run from the location that you created the `mykey.env` above and you will need to **amend password and srv record** in the connection string `connStr`.

**1. Define Initial Setup Parameters** - ENSURE YOU CHANGE _PASSWORD_ & _SRVHOSTNAME_ FIRST

```javascript
var connStr = "mongodb+srv://main_user:PASSWORD@SRVHOSTNAME.mongodb.net";
```

**2. Define Other Initial Setup Variables**

```javascript
var demoDB = "demoFLE";
var env = {};
load('mykey.env');
// JS/Shell equivalent of: use demoFLE
db = db.getSiblingDB( demoDB );
// empty collections in database to easily start from clean slate
db.dropDatabase();
// Nothing special about key collection name, but recommend a unique label
var keystoreColl = "keystore";
var keystore = db.getCollection( keystoreColl );
// define local master key
var localDevMasterKey = {
    key: BinData( 0, env.localDevKey )
};

```

**3. Enable Client Side Field Level Encryption Session Mode**

```javascript
// Enable CSFLE session mode, with handles labeled "encryptedSession" and "db".
var clientSideFLEOptions = {
    kmsProviders: {
        local: localDevMasterKey,
    },
    keyVaultNamespace: keystore.toString() ,
    schemaMap: {},  // on first invocation, prior to field key generation this should be empty
};

encryptedSession = new Mongo(connStr, clientSideFLEOptions);
// JS/Shell equivalent of: use demoFLE
// connect and use demoFLE again
db = db.getSiblingDB( demoDB )

// specify key vault
var keyVault = encryptedSession.getKeyVault();
```

**4. Generate New Field Keys Using Master Key to do Wrapping Encryption**

```javascript
// note: the second parameter is an ARN, which doesn't apply for local: can either be empty value or eg: "dummy-localKMS-ARN"

keyVault.createKey("local", "", [ 'fieldKey1' ]);
keyVault.createKey("local", "", [ 'fieldKey2' ]);

// Specify which fields need to be encrypted via client-side enforcement and init new FLE session

var key1 = db.getCollection( keystoreColl ).find({ keyAltNames: 'fieldKey1' }).toArray()[0]._id
var key2 = db.getCollection( keystoreColl ).find({ keyAltNames: 'fieldKey2' }).toArray()[0]._id
// show the encrypted keys in the keystore collection
db.keystore.find().pretty()

```

You can also validate the creation of these keys in MongoDB Compass, worth noting the keyMaterial is encrypted with the CMK.

![46compass01](img/46compass01.png)

**5. Define the JSON Schema That Will be Used for Both Client Side and Server Side**

```javascript
// Create people JSON schema that can be used for both defining the client side and server side. Note type enforced is only true for server-side JSON schema, not the "schema-lite" that drivers enforce, the client side ignores non "encrypt" elements.

var peopleSchema={
   "bsonType": "object",
   "properties": {
      "firstName": { "bsonType": "string" }, // not required, but if listed type will be enforced
      "lastName":  { "bsonType": "string" }, // not required, but if listed type will be enforced
      "ssn": {
         "encrypt": {
            "bsonType": "string",
            "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
            "keyId": [ key1 ]
         }
      },
      "address": {
         "bsonType": "object",
         "properties": {
            "street" : { bsonType: "string"  },
            "city"   : { bsonType: "string"  },
            "state"  : { bsonType: "string"  },
            "zip"    : { bsonType: "string" },
          }
      },
      "contact": {
         "bsonType": "object",
         "properties": {
            "email"   : {
               "encrypt": {
                  "bsonType": "string",
                  "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
                  "keyId": [ key2 ]
               }
            },
            "mobile"  : {
               "encrypt": {
                  "bsonType": "string",
                  "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
                  "keyId": [ key2 ]
               }
            }
         },
      },
   }
};
```

**6. Map the JSON Schema on the People Collection**

```javascript
// NOTE: the collection name here ("demoFLE.people") *must* be an inline literal - no constants or variables allowed
var peopleSchemaMap = {
     "demoFLE.people" : peopleSchema
};
```

**7. Update Current Connection to Reflect Client-enforced Configuration**

```javascript
var clientSideFLEOptions = {
    kmsProviders : {
        local : localDevMasterKey
    },
    keyVaultNamespace : keystore.toString(),
    schemaMap : peopleSchemaMap
};

var encryptedSession = new Mongo(connStr, clientSideFLEOptions);
db = encryptedSession.getDB( demoDB );
```

**8. Insert data to people collection**

```javascript
db.people.insert({
   firstName: 'Alan',
   lastName:  'Turing',
   ssn:       '901-01-0001',
   address: {
      street: '123 Main',
      city: 'Omaha',
      zip: '90210'
   },
   contact: {
      mobile: '202-555-1212',
      email:  'alan@example.com'
   }
});
```

And NOW the collection people exists we can also set the server side JSON schema.

```
// set server side JSON schema
db.runCommand({
   collMod: "people",
   validator: {
      $jsonSchema: peopleSchema }
});
```

Validate with MongoDB Compass the schema validation is in place on the server side

![46compass02](img/46compass02.png)



---
## Measurement

**1. In the same MongoDB shell read back the data (we will refer to this as shell 1)**

```javascript
use demoFLE
db.people.find().pretty()
```

**2. Now open another separate MongoDB shell (we will refer to this as shell 2)**

Connect a new MongoDB shell to the same cluster and read back the data, as this shell has not been configured with the knowledge to use the CMK or Keystore collection, you will note the fields for `ssn, mobile and email` were not able to be decrypted and show as cipher text.

*Example:*

![46shell01](img/46shell01.png)

**3. Note how MongoDB Compass displays the data**

Since MongoDB Compass also has no knowledge of the CMK or Keystore collection usage, data that is encrypted is shown with stars, and these fields can not be edited.

![46compass03](img/46compass03.png)


