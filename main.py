#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import getpass
import imaplib
import email

def start():

    user = 'barbara@lab804.com.br'
    pwd = getpass.getpass("Enter your password --> ")

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(user, pwd)
    return mail

def conn():

    c = start()
    if c:
        try:
            c.list()
            c.select("inbox")
            return c
        except imaplib.IMAP4.error as e:
            print ("LOGIN FAILED!!!  %s" % e)
            return False
    else:
        print("Erro de start")

def new_mail(c):

    with conn() as c:
        typ, data = c.select('inbox')
        print(typ, data)
        num_msgs = int(data[0])
        print('There are {} messages in INBOX'.format(num_msgs))
        return num_msgs

def get_mail(c):

        typ, data = c.search(None,  '(FROM "dados_pcd@cemaden.gov.br")')
        nm = new_mail(c)
        if nm >= 1:
            try:
                for num in data[0].split():
                    typ, msg_data = c.fetch(num, '(RFC822)')
                    print("NEW EMAIL")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_string(response_part[1])
                            subject=msg['subject']
                            print ('Message %s\n%s\n' % (num, data[0][1]))
                            print(subject)
                            payload=msg.get_payload()
                            body=extract_body(payload)
                            print(body)
                    typ, response = conn.store(num, '+FLAGS', r'(\Seen)')
            finally:
                try:
                    c.close()
                except:
                    pass
                c.logout()
        else:
            print("Nao ha emails")
def main():

    isconnect = conn()
    if isconnect:
        get_mail(isconnect)
    else:
        print("Erro na conexao com o gmail")

if __name__ == "__main__":

        main()
