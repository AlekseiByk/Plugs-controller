# Plugs-controller
## System for controlling washers

You need tuya wifi smart sockets, raspberry pi(or other mini pc). First, you need to connect you sockets to the tuya smart app. 
Second, you need to set up tinytuya preferences, to do this, follow the instructions: https://github.com/jasonacox/tinytuya. After that you will have file devices.json like that:
```
{
  "id": "",
  "key": "",
  "mac": "",
  "uuid": "",
  "category": "",
  "product_name": "",
  "product_id": "",
  "biz_type": ,
  "model": "",
  "sub": ,
  "icon": ""
},
```
you need to add 3 fields :
```
{
  "name": you name for socket,
  "ip": ip address of the socket,
  "version": version of the socket firmvare(3.3 or 3.4),
},
```
Then enter the secret phrase, server details to the [file](Plugs.py) and run script with parameter -m (to run main code with sending data to server) or -l (for logging program).
On the server run [http_server.py](http_server.py) enter the same information.

You can run [parse.py](parse.py) with the logs file and draw beautiful plot.
