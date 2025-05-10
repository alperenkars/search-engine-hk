# (For Final Phase)

This is the README for COMP4321 Group Project (Group 19). I would teach you how to prepare the virtual Python environment, and how to build and execute the spider, and how to start the Django web server to display the web user interface of our search engine using Git Bash Terminal in Your VS Code using Windows machine.

We would use Python (version 3.11.5), pip (version 23.2.1), VS Code’s Git Bash Terminal, Google Chrome browser and a Windows 11 machine. please prepare them beforehand.

---

# How to set up your local virtual Python environment & install all necessary packages?

## For Windows

0. (If you have go through the installation procedure in our final report, you can skip this part.)

1. After you have unzipped the file `FinalPhase.zip`, you should see another zip file inside the unzipped folder `FinalPhase`, which is called `code.zip`. This zip file should contain all the necessary source codes of our project.

2. Unzip `code.zip` and you would get a folder called `code`. Open your Git Bash terminal in Visual Studio Code (VS Code), and make sure you are in the same directory location where the folder `project` and `requirements.txt` is being placed. Type `py -m venv venv` to create a new virtual environment called `venv`.

3. Wait for a while and the virtual environment would be set up for you. Then, activate the virtual environment by typing `source venv/Scripts/activate`. You should see `(venv)` in your command line interface if you have successfully activated the virtual environment.

4. Then, install all the requirements using `pip install -r requirements.txt` command. After that, you can type `pip freeze` to see what packages have been successfully installed.

5. You should successfully install all necessary packages and the virtual environment should be ready now.

---

# Where is the Spider?

## For Windows

1. After you have prepared the local virtual Python environment by following the instructions from the above, you should get inside the directory cd project by entering `cd project`. Inside the directory, the Spider is located in `Spider.py`.

2. The `Spider.py` script is used to crawl web pages and store the data in `main.db`.

---

# How to run the Spider?

## For Windows

1. Once again please make sure your virtual environment is already activated. First, run the Spider by entering `python Spider.py` to start the crawling process. This should take around 30 seconds to complete crawling maximum 300 pages. After the crawling process is finished, you should see `main.db` is generated. This SQLite database stores all the database table files that contain the indexed 300 pages (at maximum) starting from `https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm`.

---

# How to start up the Django web server & see the web user interface?

## For Windows

1. After you have finish running the Spider, make sure you are still locating inside the `project` directory. Then, you can start the Django web server by typing `python manage.py runserver`.

2. Wait for a short while, and you should see there is a link `http://127.0.0.1:8000/` appeared in the terminal. Click on that link, or simply type in this link in your browser to go to the web user interface. (Note: You may encounter an error when you get into this link. This is due to the existence of the cookies from other groups. You can follow Step 3 below to solve this problem.)

3. To clear the previous cookies, press `F12` key to go to the Developer Tools page. Go to the `Application` tab. You should see there are 2 cookies, which are called `csrftoken` and `user_cookie_id`. Clear all these 2 cookies by clicking `Clear all cookies`. You can then refresh the web user interface by pressing `F5` key. You may also force refresh the web user interface by pressing `Shift` and `F5` keys at the same time. Alternatively, you can simply clode the browser tab, and open a new tab and serach for `http://127.0.0.1:8000/` again.

---

# What you can do with the web user interface?

## For Windows

1. You can start to start searching by typing your query in the search bar and click `Search` button. You can also perform phrase search, by using a pair of double quotation marks ("") to enclose the phrases.

2. Alternatively, you can also select a few stemmed keywords in the bottom left section and click `Search with Selected Keywords`.

3. When the web user interface returns the search result, you can click `Get Similar Pages` to search for the similar pages.

4. After you have searched for a few queries, you can see the left section would contain you latest 10 searching query history, you can click on one of it to do the query. You can also click `Clear History` to clean all query histories.

---

# How to turn off the Django web server?

## For Windows

1. Go back to your Git Bash Terminal in VS Code, and press `Ctrl` and `C` keys at the same time to terminate the running of the Django web server.

2. Deactivate the local virtual Python environment by typing `deactivate`.

---
---
---

# (For Phase 1)

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