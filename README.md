## Set Up Your Local Development Environment

From here, `words that looks like this` are terminal commands

- Install python on your local machine
  - Google it or go [here](https://www.python.org/psf/).
- Install git on your local machine.
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

### To push your changes

make a new branch:

`git checkout -b some-branch-name`

after you change code run

`git status` to see what has changed. For all the files you want to keep the changes for, do

`git add <filename>`

when you've added them all, write a commit message:

`git commit -m"<your message>"`

then push to repo

`git push orgin`

### To pull changes from origin to local or deployment

`git pull`

it will not work if you have local changes. If that's an issue you might need to make a throaway branch so you can pull from origin, and deal with it later (maybe manually bring your changes over)
one solution:
`git checkout -b some-branch-name`
`git add .`
`git commit -m"<your message>"`
and then
`git checkout main`
`git pull`


#### Common Problems

##### XXX Doesn't Exist

sadly you can't create new related items (Category, Neighborhood, etc) through the import. If you run into "Neighborhood doesn't exist" you need to create that Neighborhood and try again.

##### get() returned more than one Blob -- it returned 2

We identify Blobs by title and if you have more than 1 with the same title you need to remove them form the csv and add them manually. The only way to avoid this would be to identify in a different way, like title and category. But then you'll have problems with changing those. Or we could export with IDs and keep add those to your sheet, then change ID as the identifier. But then you need to keep hem straight.

## GIT - making changes to the code
