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
        """Inicialização das variaveis recebidas e conexao com IMAP"""
        self.user = user
        self.password = password
        if IMAP_USE_SSL:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        else:
            self.imap = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)

    def __enter__(self):
        """Realiza login com usuario e senha, selecionando caixa de entrada geral"""
        self.imap.login(self.user, self.password)
        self.imap.select('Inbox')
        return self

    def __exit__(self, type, value, traceback):
        """Realiza logout da sessao e email"""
        self.imap.close()
        self.imap.logout()

    def get_count(self):
        """Realiza a busca de emails(contabilizando). Pra isso, tem
        como parametro o email address de um determinado remetente"""
        status, data = self.imap.search(None, FROM)
        return sum(1 for num in data[0].split())

    def delete_message(self, num):
        """É responsável por deletar um email de um determinado remetente"""
        self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def delete_all(self):
        """É responsável por deletar todos emails de um determinado remetente"""
        status, data = self.imap.search(None, FROM)
        for num in data[0].split():
            self.imap.store(num, '+FLAGS', r'\Deleted')
        self.imap.expunge()

    def print_msgs(self):
        """Imprime a quantidade total de emailo e conteudo, além de gerenciar
        a busca pelo link no email e realizar o download do arquivo.
        Após isto, deleta o email referente ao arquivo baixado com sucesso"""
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
        """É responsável pela busca do link de download do arquivo,
        em meio ao conteudo do email"""
        link = link_re.findall(data)
        result = (b''.join(link).decode())
        print(result)
        return result

    staticmethod
    def filename(url):
        """Responsável por nomear o arquivo baixado"""
        link = self.search_name(url)
        print (link)
        return link

    def download_file(self, url):
        """Realiza o download do arquivo atraves do link encaminhado
        para o email cadastrado."""
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
