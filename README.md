
## Set Up Your Local Development Environment
From here, `words that looks like this` are terminal commands

 - Install python on your local machine
    - Google it or go [here](https://www.python.org/psf/).
    
 - From the terminal navigate to the directory you want this code to live and clone this repo by typing the following into a terminal:
    
    `git clone https://github.com/mdaizovi/bookbuild`
    
 - `cd bookbuild` to get into repo. 
 
 - Make a Virtual Environment:
    - If you have python 3.9 on your system, you can make a virtual environment like so:
       - `python -m venv venv`
       - If that doesn't work, you might need to type `python3 -m venv venv`
  
 - Activate virtual environment:
  
    `source venv/bin/activate`

 - Install backend requirements (make sure you are in your virtual environment first):
  
    `pip install -r requirements.txt`
     - If that doesn't work, you might need to type `pip3 install -r requirements.txt`
     NOTE TO THE FUTURE: if this does not work, check to ensure that `cffi` is not pinned to a specific verison, in requirements.txt
     As of right now cffi is causing problems between versions of python 3.9 versus 3.10

### If you want same db as what is online:##
You'll need to download the db.sqlite from pythonanywhere and put it in 
`bookbuild/bookbuild_src` on your local environment

