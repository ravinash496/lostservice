# SpatialRouter LoST Service
Spatial Router LoST service application.

### Install Python  
Download and install python (Windows) from [here](https://www.python.org/ftp/python/3.6.1/python-3.6.1-amd64.exe)  

### Install GitGub client  
Download and install GitHub (Windows) from [here](https://desktop.github.com)  

### Pull the project from GitHub  
`git clone https://github.com/Geo-Comm/lostservice.git`  

### Set up your project python environment.  
`cd <project folder>`  
`virtualenv --python c:\Users\<your user>\AppData\Local\Programs\Python\Python36\python.exe lost-env`  
`.\lost-env\Scripts\activate`

### Install Prerequisite Packages
_Linux_

`pip install -r requirements.txt`  

_Windows_

`win-requirements.bat`

### For Windows Only
The batch file above should install all of the dependencies for the project. If it does not, chances are it failed on installing some of the wheels, which you will now have to do manually. The wheels can be found in the dependencies directory of the repository:  

Shapely:  

`pip install Shapely-1.5.17-cp36-cp36m-win_amd64.whl`  

LibXML Parsing:  

`pip install lxml-3.7.3-cp36-cp36m-win_amd64.whl`  

### Installing Packages from Scratch
psychpg2:  
`pip install psycopg2`  

geoalchemy2:  
`pip install geoalchemy2`  

numpy:  
`pip install numpy`  

Shapely:  
Windows:  
[Shapely-1.5.17-cp36-cp36m-win_amd64.whl](http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely)  
`pip install Shapely-1.5.17-cp36-cp36m-win_amd64.whl`  

Linux:  


LibXML Parsing:  
Windows:  
[lxml-3.7.3-cp36-cp36m-win_amd64.whl](https://pypi.python.org/packages/cb/18/5e1a771220b23640b984765133414070c2f52da7102987b3377a51ccfa2c/lxml-3.7.3-cp36-cp36m-win_amd64.whl#md5=f8b0b8e0363305ecba33925d31d27631)  
`pip install lxml-3.7.3-cp36-cp36m-win_amd64.whl`  

Linux:  

Sphinx:  
`pip install Sphinx`  

logging:  
TBD  

testing:  
TBD  

If you ever add new dependencies with pip, you need to recreate the requirements.txt file:  
`pip freeze > requirements.txt`  

