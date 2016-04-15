dn: uid={{club_account}},ou=People,dc=club,dc=kyutech,dc=ac,dc=jp
changetype: add
objectClass: top
objectClass: posixAccount
objectClass: shadowAccount
objectClass: inetOrgPerson
cn: {{gecos}}
sn: {{gecos_last}}
uid: {{club_account}}
uidNumber: #{new_uid}
gidNumber: 1000
homeDirectory: /home/club/{{club_account}}
gecos: {{gecos}}
userPassword: {{shadow_password}}
shadowLastChange: 10000
loginShell: /usr/local/bin/bash
cn;lang-ja: {{name_last}} {{name_first}}
sn;lang-ja: {{name_last}}
displayName: {{name_last}} {{name_first}}
employeeNumber: {{isc_account}}
employeeType: kyutech
l: {{l}}
mail: {{isc_account}}@mail.kyutech.jp
shadowExpire: #{account_expire_day?}
