# Configure MongoDB Enterprise Server for LDAP authN and authZ

This is an optional set in the proof only required if you want to test a self-hosted MongoDB Enterprise Server instance against an LDAP(S) server.

## Setup

Install MongoDB Enterprise Edition on the database server machine. This sever should be deployed in the same (or peered) VPC as the LDAPS server.

#### Create mongod.cfg file pointing to our new LDAP server

Create the following mongod.cfg file on the server:

```
cat <<EOF > mongod.cfg
storage:
  dbPath: /data/

processManagement:
  fork: true

systemLog:
  destination: file
  path: /data/mongodb.log

net:
  port: 27017
  bindIp: 0.0.0.0

security:
#   authorization: "enabled"
   ldap:
      servers: "<LDAP server FQDN here>:636"
      bind:
         queryUser: "cn=admin,dc=ldap,dc=mongodb,dc=local"
         queryPassword: "<bind user password>"
      userToDNMapping:
         '[
            {
               match : "(.+)",
               ldapQuery: "dc=ldap,dc=mongodb,dc=local??sub?(uid={0})"
            }
         ]'
      authz:
         queryTemplate: "{USER}?memberOf?base"
setParameter:
   authenticationMechanisms: "PLAIN"
EOF
```

This defines a fairly standard confuration but with LDAP enabled. Focusing on the `security` section:

* We have commented out the 'authorization' line as we are not enabling authorization at this point. This will allow us to connect to the server and create the roles and mappings defined in our LDAP server, simplifying the setup process. Once that's done this line can be uncommented and the server restarted to lock down the service. Production systems should have this line present and uncommented.
* 'servers' is a comma separated list of LDAPS servers and optional ports. For our purposes we will specify a single entry, the FQDN of our LDAPS server, namely the output of `hostname -f` run on the LDAPS server. *Aside*: If 'transportSecurity' (an additional setting, not shown here) is set to 'none' indicating that you are using a standard LDAP server with no TLS support, then you should update the port to `389`.
* We are binding with the `admin` user (using the full DN); update the password as appropriate.
* We have specified a single `userToDNMapping` rule which takes any input (based on the regex in the 'match' clause) and converts it into a sub-tree LDAP query, looking for users with that string (`{0}`) as their `uid`, starting from our default Base DN
* We've specified a _base_ LDAP query as the authorization template, taking the DN we matched via the `userToDNMapping` query (namely the `{USER}` value) and retrieving the `memberOf` attribute of that DN.
* We are using the `PLAIN` authentication mechanism, which is how we tell the system we're using an LDAP server for authentication purposes.

Once the config file is updated restart the `mongod` process:

```
mongod -f mongod.cfg
```

**Note**: If this is a fresh install on Ubuntu you may need to install the `snmp` package first:

```
sudo apt-get install snmp
```

#### Test using `mongoldap`

`mongoldap` is a command line tool supplied with MongoDB Enterprise which can validate the mongod configuration file without requiring you to start/restart a `mongod` process to validate the config file.

We can test the configuration file using the two users we defined earlier:

```
mongoldap --config mongod.cfg --user jane
mongoldap --config mongod.cfg --user john
```

Note that we use a simple value for each user. This value will be mapped to a DN based on the `userToDNMapping` rules. Once the full DN for each user is found the `queryTemplate` is used to run a second LDAP query to find out which groups that user belongs to (by performing a base search on the user's DN for the derived `memberOf` attribute).

Note: If you connect over LDAP (rather that LDAPS) you may see some FAIL's as you are binding with a plaintext password over a non-TLS connection.

The first command (for `uid=jane`) should return the following roles:

```
* cn=admins,ou=groups,dc=ldap,dc=mongodb,dc=local
* cn=users,ou=groups,dc=ldap,dc=mongodb,dc=local
```

The second command (for `uid=john`) should return the following role:

```
* cn=users,ou=groups,dc=ldap,dc=mongodb,dc=local
```

#### Create admin & readonly roles

In order to allow users defined in our LDAP server to connect to the database we have to create `roles` in the database with associated privileges. We do *not* have to create any users directly. Instead the roles defined in the database map to the groups in our LDAP server and users which are members of these groups will be granted the privileges defined by the associated MongoDB role.

We will create 2 roles:

1. For the `cn=admins` group, giving those users full root/admin permission.
2. For the `cn=users` group, giving those users read-only permissions.

Connect to the server using the `mongo` shell, then issue the following commands: 

```
use admin
db.createRole({role: "cn=admins,ou=groups,dc=ldap,dc=mongodb,dc=local", privileges:[], roles: ["root"]})
db.createRole({role: "cn=users,ou=groups,dc=ldap,dc=mongodb,dc=local", privileges: [], roles: ["readAnyDatabase"]})
```

In this example any member of the `cn=admins` group will be a MongoDB root user, while any member of the `cn=users` group will only be granted read access (to any database). Note that the `role` value is the full DN for the group in question - by knowing which LDAP groups a user belongs to (in the LDAP server) and knowing the mapping of LDAP groups to MongoDB groups, we can ensure these users have the relevant permissions when they connect to the MongoDB cluster.

#### Update mongod.cfg and restart server

Now that the roles have been defined you can reconfigure the server to enable `authorization` by uncommenting the relevant line in the configuration file, e.g. change the `security` section to:

```
security:
   authorization: "enabled"
   ...
```

Once this is done, save the file and restart the mongod process.

#### Test new roles

Connect to the LDAP-enabled `mongod` using the `mongo` shell supplying no user-credentials. Then issue the following commands:

```
use $external

db.auth({mechanism: "PLAIN", user: "jane", pwd:"<jane's password>"})
db.runCommand({connectionStatus:1})

db.auth({mechanism: "PLAIN", user: "john", pwd:"<john's password>"})
db.runCommand({connectionStatus:1})
```

(replace the `pwd` fields as appropriate)

The `db.auth()` command in both cases should succeed (returning `1`).

User `jane` is the only one that contains the `root@admin` role:

```
{
	"authInfo" : {
		...
		"authenticatedUserRoles" : [
			{
				"role" : "root",
				"db" : "admin"
			},
		...
	}
}
```

Both users should include the `readAnyDatabase@admin` role:

```
{
	"authInfo" : {
		...
		"authenticatedUserRoles" : [
			{
				"role" : "readAnyDatabase",
				"db" : "admin"
			},
		...
	}
}
```

**Note**: Both users also contain other roles based on the LDAP group but these are not relevant here.