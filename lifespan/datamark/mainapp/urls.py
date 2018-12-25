from .views.index import index as index, apis as index_apis
from .views.login import login, register, apis as login_apis
from .views.marking import index as marking, apis as marking_apis
from .views.install import index as install, apis as install_apis

urls = []

urls.append(('', index))
for item in index_apis:
    urls.append(("api/index/" + item[0], item[1]))
urls.append(('login', login))
urls.append(('register', register))
for item in login_apis:
    urls.append(("api/login/" + item[0], item[1]))
urls.append(('marking', marking))
urls.append(('reviewing', marking))
urls.append(('testing', marking))
for item in marking_apis:
    urls.append(("api/marking/" + item[0], item[1]))
urls.append(('install', install))
for item in install_apis:
    urls.append(("api/install/" + item[0], item[1]))