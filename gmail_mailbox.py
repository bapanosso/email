#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

import imaplib
import getpass
import requests
import re, os

session = requests.Session()

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = '993'
IMAP_USE_SSL = True
FROM = '(FROM "dados_pcd@cemaden.gov.br")'
email_address = "dados_pcd@cemaden.gov.br"
link_re = re.compile(rb'href=\'(.*)?\'')

class Gmail(object):

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.cont = 0
        if IMAP_USE_SSL:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        else:
            self.imap = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)

    def __enter__(self):
        self.imap.login(self.user, self.password)
        self.imap.select('Inbox')
        return self

    def __exit__(self, type, value, traceback):
        self.imap.close()
        self.imap.logout()

    def get_count(self):
        status, data = self.imap.search(None, FROM)
        return sum(1 for num in data[0].split())

    def delete_message(self, num):
        self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def delete_all(self):
        status, data = self.imap.search(None, FROM)
        for num in data[0].split():
            self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def print_msgs(self):
        status, data = self.imap.search(None, FROM)
        for num in reversed(data[0].split()):
            status, data = self.imap.fetch(num, '(RFC822)')
            print ('Message %s\n%s\n' % (num, data[0][1]))
            link = self.search_link(data[0][1])
            csv = self.download_file(link)
            if csv:
                print("Download file success")
                self.delete_message(num)
                print("Email deletado")
            else:
                print("Error download file")

    @staticmethod
    def search_link(data):
        link = link_re.findall(data)
        result = (b''.join(link).decode())
        print(result)
        return result

    def delete_msgs_sent_to(self, email_address):
        status, data = self.imap.search(None, 'TO', email_address)
        if status == 'OK':
            for num in reversed(data[0].split()):
                status, data = self.imap.fetch(num, '(RFC822)')
                self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    staticmethod
    def filename(url):
        link = self.search_name(url)
        print (link)
        return link

    def download_file(self, url):
        linkname = url.split('/')[-1]
        local_filename = ('%s.csv' % linkname)
        r = session.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.close()
                    return True
                else:
                    return False

if __name__ == '__main__':
    imap_username = 'scraping.camaden@gmail.com'
    imap_password = getpass.getpass("Enter your password --> ")
    with Gmail(imap_username, imap_password) as mail:
        print (mail.get_count())
        print (mail.print_msgs())
