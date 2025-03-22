This is the README for COMP4321 Group Project (Group 19). I would teach you how to prepare the virtual Python environment, and how to build and execute the spider and the test program using Git Bash Terminal in Your VS Code using Windows machine.

---

# How to set up your local virtual Python environment?

## For Windows

1. After you have unzip the file `Phase1.zip`, you should see another zip file inside the unzipped folder `Phase1`, which is called `code.zip`. This zip file should contain all the necessary source codes of our project.

2. Unzip `code.zip` and you would get a folder called `code`. Open your Git Bash terminal in Visual Studio Code (VS Code), and make sure you are in the same directory location where the folder `project` and `requirements.txt` is being placed. Type `py -m venv venv` to create a new virtual environment called `venv`.

3. Wait for a while and the virtual environment would be set up for you. Then, activate the virtual environment by typing `source venv/Scripts/activate`. You should see `(venv)` in your command line interface if you have successfully activated the virtual environment.

4. Then, install all the requirements using `pip install -r requirements.txt` command. After that, you can type `pip freeze` to see what packages have been successfully installed.

5. You should successfully installed all necessary packages and the virtual environment should be ready now.

---

# Where is the Spider and the test program?

## For Windows

1. After you have prepared the local virtual Python environment by following the instructions from the above, you should get inside the directory cd project by entering `cd project`. Inside the directory, the Spider is located in `Spider.py` and the test program is located in `generate_spider_result.py`.

2. The `Spider.py` script is used to crawl web pages and store the data in `main.db`, while `generate_spider_result.py` processes the crawled data to generate results in `spider_result.txt`, which is similar to the ones in the project description handout.

---

# How to run the Spider and the test program to generate the result?

## For Windows

1. Once again please make sure your virtual environment is already activated. First, run the Spider by entering `python Spider.py` to start the crawling process. This should take around 2 minutes to completing crawling 30 pages. After the crawling process is finished, you should see `main.db` is generated. This SQLite database stores all the database table files that contain the indexed 30 pages starting from `https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm`.

2. Then, you can start to run the test program by entering `python generate_spider_result.py`. After a while, you should see `spider_result.txt` is generated. This txt file would contain the output of the test program.

---

# How to set up in your local environment

## For Windows

1. After you have successfully clone this repository to your local machine, make sure you are in the same direcory location where this README.md is being placed. Open your Git Bash terminal and type `py -m venv venv` to create a new virtual environment called `venv`.

2. Wait for a while and the virtual environment would be set up for you. Then, activate the virtual envioronment by typing `source venv/Scripts/activate`. You should see `(venv)` in your command line interface if you have successfully activated the virtual environment.

3. Then, install all the requirements using `pip install -r requirements.txt` command. After that, you can type `pip freeze` to see what packages have been successfully installed.

4. Get into `project` directory by typing `cd project`. Type `python manage.py runserver` to start the Django app server. Search `http://localhost:8000/` or `http://127.0.0.1:8000/` in your browser and you should be able to see the index page of our project. Press `Ctrl C` if you want to stop the Django app server from running.

---

# Running the Spider and Generating Results

The `Spider.py` script is used to crawl web pages and store the data, while `generate_spider_result.py` processes the crawled data to generate results similar to the ones in the handout. To run these scripts, ensure your virtual environment is activated. Then after navigating to project folder, use `python Spider.py` to start the crawling process and `python generate_spider_result.py` to process the data. Note again that both scripts should be executed from the root directory of the project.

---

# Useful References

* https://www.djangoproject.com/start/

* https://youtu.be/iKD1BwIfwNw?si=ZgYxBr0wMxeN0L0I