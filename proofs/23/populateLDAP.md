# Scripts to Populate an Empty LDAP Server

The following scripts will create the hierarchy described in the main document of this proof. Note that after each `ldapadd` command you will need to provide the password of the `cn=admin` user.

**Note**: All commands below which modify the LDAP server will use a 'bind DN', aka a bind user. The examples use: `cn=admin,dc=ldap,dc=mongodb,dc=local`. In order to complete the operation and update the server you will need to provide the password for the bind user when you see the `Enter LDAP Password:` prompt.

### 1. Create user hierarchy

#### 1.1 Create parent node `ou=users`

```
cat <<EOF > add-users-ou.ldif
dn: ou=users,dc=ldap,dc=mongodb,dc=local
objectClass: organizationalunit
EOF

ldapadd -x -D cn=admin,dc=ldap,dc=mongodb,dc=local -W -f add-users-ou.ldif
```

#### 1.2 Create leaf node `uid=jane`

```
cat <<EOF > add-jane.ldif
dn: uid=jane,ou=users,dc=ldap,dc=mongodb,dc=local
objectClass: inetorgperson
cn: jane
sn: doe
EOF

ldapadd -x -D cn=admin,dc=ldap,dc=mongodb,dc=local -W -f add-jane.ldif
```

#### 1.3 Create leaf node `uid=john`

```
cat <<EOF > add-john.ldif
dn: uid=john,ou=users,dc=ldap,dc=mongodb,dc=local
objectClass: inetorgperson
cn: john
sn: doe
EOF

ldapadd -x -D cn=admin,dc=ldap,dc=mongodb,dc=local -W -f add-john.ldif
```

### 2. Create group hierarchy

#### 2.1 Create parent node `ou=groups`

```
cat <<EOF > add-groups-ou.ldif
dn: ou=groups,dc=ldap,dc=mongodb,dc=local
objectClass: organizationalunit
EOF

ldapadd -x -D cn=admin,dc=ldap,dc=mongodb,dc=local -W -f add-groups-ou.ldif
```

#### 2.2 Create leaf node `cn=admins`, adding Jane

```
cat <<EOF > add-admins.ldif
dn: cn=admins,ou=groups,dc=ldap,dc=mongodb,dc=local
objectClass: groupofnames
cn: admins
description: All users
# add the group members all of which are
# assumed to exist under users
member: uid=jane,ou=users,dc=ldap,dc=mongodb,dc=local
EOF

ldapadd -x -D cn=admin,dc=ldap,dc=mongodb,dc=local -W -f add-admins.ldif
```

#### 2.3 Create leaf node `cn=users`, adding Jane and John

```
cat <<EOF > add-users.ldif
dn: cn=users,ou=groups,dc=ldap,dc=mongodb,dc=local
objectClass: groupofnames
cn: users
description: All users
# add the group members all of which are
# assumed to exist under users
member: uid=john,ou=users,dc=ldap,dc=mongodb,dc=local
member: uid=jane,ou=users,dc=ldap,dc=mongodb,dc=local
EOF

ldapadd -x -D cn=admin,dc=ldap,dc=mongodb,dc=local -W -f add-users.ldif
```

### 3. Set user passwords

#### Set LDAP passwords

Run the following commands to set the password for both users, following the prompts as required (enter the user's password, repeat said password and then provide the admin password to confirm):

```
ldappasswd -H ldap:/// -S -W -D "cn=admin,dc=ldap,dc=mongodb,dc=local" -x "uid=jane,ou=users,dc=ldap,dc=mongodb,dc=local"
```

```
ldappasswd -H ldap:/// -S -W -D "cn=admin,dc=ldap,dc=mongodb,dc=local" -x "uid=john,ou=users,dc=ldap,dc=mongodb,dc=local"
```

### 4. Test group membership

Verify that Jane is in both the `cn=users` and the `cn=admins` groups by running the following command:

```
ldapsearch -x -LLL -H ldap:/// -b uid=jane,ou=users,dc=ldap,dc=mongodb,dc=local memberof
```

The output should be:

```
dn: uid=jane,ou=users,dc=ldap,dc=mongodb,dc=local
memberOf: cn=admins,ou=groups,dc=ldap,dc=mongodb,dc=local
memberOf: cn=users,ou=groups,dc=ldap,dc=mongodb,dc=local
```

Verify that John is in the `cn=users` group by running the following command:

```
ldapsearch -x -LLL -H ldap:/// -b uid=john,ou=users,dc=ldap,dc=mongodb,dc=local memberof
```

The output should be:

```
dn: uid=john,ou=users,dc=ldap,dc=mongodb,dc=local
memberOf: cn=users,ou=groups,dc=ldap,dc=mongodb,dc=local
```
