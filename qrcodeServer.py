from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import subprocess
import qrcode
import requests
import json
import base64
import datetime
import conf
import time

# Used for basic http authentication of the webserver
key = base64.b64encode("{}:{}".format(conf.get_user(), conf.get_password()))

# Program template for printer. written in EPL printer language. See https://www.zebra.com/content/dam/zebra/manuals/en-us/printer/epl2-pm-en.pdf
print_template = '''"N\\n
q304\\n
Q203\\n
D7\\n
b50,10,Q,m2,s3,eL,\\"{}\\"\\n
A50,120,0,1,1,1,N,\\"{}\\"\\n
A50,140,0,1,1,1,N,\\"{}\\"\\n
A50,160,0,1,1,1,N,\\"{}\\"\\n
P1\\n"'''


class S(SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_AUTHHEAD(self):
        print "send header"
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # Don't allow get requests
         self.send_response(404)

    def do_POST(self):
        # Use basic http authentication to perform the POST operation
        global key
        if self.headers.getheader('Authorization') == None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
            pass
        elif self.headers.getheader('Authorization') == 'Basic '+key:
            self.handle_header()
            pass
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.getheader('Authorization'))
            self.wfile.write('not authenticated')
            pass

    def handle_header(self):
        # Get the incoming POST JSON data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        j = json.loads(post_data)
        # Output QR codes in both print and file
        self.print_qrcode(j)
        self.save_qrcode(j)
        self._set_headers()
        self.wfile.write("Asset QR code generated")

    def parse_jira_data(self, jira_data):
        # Getting the Jira project and issue details
        jira_issue = jira_data['issue']['key']
        jira_project  = jira_data['issue']['fields']['project']['key']
        jira_asset_type = jira_data['issue']['fields']['issuetype']['name']
        jira_url = 'https://{}/projects/{}/issues/'.format(conf.jira_url(), jira_project)
        full_url = jira_url + jira_issue

        return {'jira_issue': jira_issue, 'full_url': full_url}

    def print_qrcode(self, qr_data):

        # Get current time
        now = datetime.datetime.now()
        now_formatted = now.strftime("%d-%m-%Y %H:%M")
        # Parse Jira JSON
        jira_data = self.parse_jira_data(qr_data)
        print_commands = print_template.format(jira_data['full_url'], jira_data['jira_issue'], now_formatted, conf.get_msg())

        # Output the EPL program to the printer in raw format
        bash_cmd = "printf {} | lpr -P {} -o raw".format(print_commands, conf.get_printer())
        p = subprocess.Popen(bash_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            pass
        retval = p.wait()

    def save_qrcode(self, qr_data):
        # Generate a QR Code to upload to Jira
        jira_data = self.parse_jira_data(qr_data)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        qr.add_data(jira_data['full_url'])
        qr.make(fit=True)

        # Save QR Code to file
        # Original idea was to save in memory with cStringIO.StringIO(). however filename and type missing in jira
        img = qr.make_image()
        qr_file_name = 'qrcode-' + jira_data['jira_issue'] + '.png'
        img.save(qr_file_name, "PNG")

        # Post the QR Code back to the jira issue
        url = 'https://{}/rest/api/2/issue/{}/attachments'.format(conf.jira_url(), jira_data['jira_issue'])
        headers = {"X-Atlassian-Token": "nocheck"}
        files = {'file': open(qr_file_name, 'rb')}
        time.sleep(2)
        r = requests.post(url, auth=(conf.jira_user(), conf.jira_pass()), files=files, headers=headers)
        print(r.status_code)
        print(r.text)


def run(server_class=HTTPServer, handler_class=S, host=conf.get_host(), port=conf.get_port()):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    print 'bind address ' + str(server_address)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
