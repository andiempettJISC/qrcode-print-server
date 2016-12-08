# qrcode-print-server

Run  
`python qrcodeServer.py`

A python webserver used as an interface for label printers using the EPL printer programming language. See https://www.zebra.com/content/dam/zebra/manuals/en-us/printer/epl2-pm-en.pdf.

This was built with the idea to use a Jira webhook at the end of an issue being created for an inventory management jira project. Essentially for creating tags for assets. the webhook calls this server and a QR Code is printed off and posted back to the issue created in jira.

### config parameters

username and password to use for python http webserver authentication  
`username: username`  
`password: password`  
Port to bind to for the python http webserver  
Important to note that low numbered privalaged ports will need you to run this as root or sudo user. this is NOT recommended  
instead have a webserver or iptables forward requests to port 80 through to the low privilage port  
`port: 8000`  
`host: 0.0.0.0`  
local printer name in CUPS  
`printer-name: label-printer`  
Custom message to print, make sure not to exceed label horizontal size  
`custom_message: hello world`  
Jira authentication details  
`jira_url: example.atlassian.net`  
`jira_username: username`  
`jira_password: password`  

### epl program example

this will print a qrcode and some text encoding the word 'msg'  
see https://www.zebra.com/content/dam/zebra/manuals/en-us/printer/epl2-pm-en.pdf and wiki.wws5.com/doku.php?id=zebra_eltron_label_creation_via_epl2

    ; commands: clear image cache, set label size, set density, qrcode scale 5, text, text, print and cut
    N
    q304
    Q203
    D7
    b65,10,Q,s5,"msg"
    A65,130,0,2,1,1,N,"msg"
    A65,150,0,2,1,1,N,"msg"
    P1
