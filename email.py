#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import imaplib
import time
import uuid
import email
import getpass
import re

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = '993'
IMAP_USE_SSL = True
FROM = '(FROM "dados_pcd@cemaden.gov.br")'
email_address = "dados_pcd@cemaden.gov.br"
link_re = re.compile (rb'href=\'(.*)?\'')
class Gmail(object):

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.ret = []
        if IMAP_USE_SSL:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        else:
            self.imap = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)

    def __enter__(self):
        self.imap.login(self.user, self.password)
        self.imap.list()
        self.imap.select('Inbox')
        return self

    def __exit__(self, type, value, traceback):
        self.imap.close()
        self.imap.logout()

    def get_count(self):
        status, data = self.imap.search(None, FROM)
        return sum(1 for num in data[0].split())

    def fetch_message(self, num):
        status, data = self.imap.fetch(str(num), '(RFC822)')
        email_msg = email.message_from_string(data[0][1])
        return email_msg

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
            print (link)
            time.sleep(2)

    def search_link(self, data):
        self.ret = link_re.findall(data)
        return self.ret

    def get_latest_email_sent_to(self, email_address, timeout=300, poll=1):
        start_time = time.time()
        while ((time.time() - start_time) < timeout):
            status, data = self.imap.select('Inbox')
            if status != 'OK':
                time.sleep(poll)
                continue
            status, data = self.imap.search(None, 'TO', email_address)
            data = [d for d in data if d is not None]
            if status == 'OK' and data:
                for num in reversed(data[0].split()):
                    status, data = self.imap.fetch(num, '(RFC822)')
                    email_msg = email.message_from_string(data[0][1])
                    return email_msg
            time.sleep(poll)
        raise AssertionError("No email sent to '%s' found in inbox "
             "after polling for %s seconds." % (email_address, timeout))

    def delete_msgs_sent_to(self, email_address):
        status, data = self.imap.search(None, 'TO', email_address)
        if status == 'OK':
            for num in reversed(data[0].split()):
                status, data = self.imap.fetch(num, '(RFC822)')
                self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()


if __name__ == '__main__':
    imap_username = 'barbara@lab804.com.br'
    imap_password = getpass.getpass("Enter your password --> ")
    with Gmail(imap_username, imap_password) as mail:
        print (mail.get_count())
        print (mail.print_msgs())
