
sc stop ZKEco-proxy
sc delete ZKEco-proxy
sc stop ZKEco-apache0
sc delete ZKEco-apache0
sc stop ZKEco-apache1
sc delete ZKEco-apache1
sc stop ZKEco-apache2
sc delete ZKEco-apache2

sc stop ZKEco-apache
sc delete ZKEco-apache
sc stop ZKEco-mysql
sc delete ZKEco-mysql

sc stop ZKEco-pgsql
sc delete ZKEco-pgsql

sc stop memcached
sc delete memcached


taskkill /im iclockCat.exe /f