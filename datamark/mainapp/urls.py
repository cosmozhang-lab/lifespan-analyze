from .views.index import index as index, apis as index_apis
from .views.install import index as install, apis as install_apis

urls = []

urls.append(('', index))
for item in index_apis:
    urls.append(("api/index/" + item[0], item[1]))
urls.append(('install', install))
for item in install_apis:
    urls.append(("api/install/" + item[0], item[1]))