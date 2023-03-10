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

### If you want same db as what is online:

You'll need to download the db.sqlite from pythonanywhere and put it in
`bookbuild/bookbuild_src` on your local environment

### How to make changes to the DB:

Edit the [models.py](https://github.com/mdaizovi/bookbuild/blob/main/bookbuild_src/importer/models.py) file locally. You can read about the django ORM [here](https://docs.djangoproject.com/en/4.1/topics/db/models/).

After you make desired changes LOCALLY run this--in your vitual environment-- from the `bookbuild/bookbuild_src` directory:

`python manage.py makemigrations`

Make sure they run properly with:
`python manage.py migrate`

If all is good, commit your code, push it to repo, go to the console ([ Bash console in virtualenv](https://www.pythonanywhere.com/user/Flocblog/)) on the deployment, pull code there, and apply the migrations. For code examples check next section.

## GIT - making changes to the code

### To push your changes

after you change code run

`git status` to see what has changed. For all the files you want to keep the changes for, do

`git add <filename>`

when you've added them all, write a commit message:

`git commit -m"<your message>"`

then push to repo

`git push orgin`

### To pull changes from origin to local or deployment

`git pull`
it will not work if you have local changes.
