This is the README for COMP4321 Group Project (Group 19).

---

# How to set up in your local environment

## For Windows

1. After you have successfully clone this repository to your local machine, make sure you are in the same direcory location where this README.md is being placed. Open your Git Bash terminal and type `py -m venv venv` to create a new virtual environment called `venv`.

2. Wait for a while and the virtual environment would be set up for you. Then, activate the virtual envioronment by typing `source venv/Scripts/activate`. You should see `(venv)` in your command line interface if you have successfully activated the virtual environment.

3. Then, install all the requirements using `pip install -r requirements.txt` command. After that, you can type `pip freeze` to see what packages have been successfully installed.

4. Get into `project` directory by typing `cd project`. Type `python manage.py runserver` to start the Django app server. Search `http://localhost:8000/` or `http://127.0.0.1:8000/` in your browser and you should be able to see the index page of our project. Press `Ctrl C` if you want to stop the Django app server from running.

---

# Useful References

* https://www.djangoproject.com/start/

* https://youtu.be/iKD1BwIfwNw?si=ZgYxBr0wMxeN0L0I