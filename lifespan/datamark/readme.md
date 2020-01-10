# 1 modify config.conf (from config.example.config) to set save dir

# 2 activate conda base

# 3 python manage.py runserver 0.8080

# 4 check ip by ifconfig

# 5 visit http://x.x.x.x:8080/install (x is the ip)

# 6 login & choose dataset, then setup

# 7 visit http://x.x.x.x:8080 & start label

# env

conda install Django
conda install numpy
conda install pytorch torchvision -c pytorch
conda install scikit-image
conda install python-opencv
conda isntall progressbar2
sudo apt-get install npm
