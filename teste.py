
import requests
session = requests.Session()

    res = session.get(url)


    mail.logout()



    resLogin = session.post(loginUrl, data = {'user' : user, 'password' : pwd})
