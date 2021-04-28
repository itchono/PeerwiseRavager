'''
PEERWISE RAVAGER V1.2
April 21, 2021

STEP 1
pip install python-dotenv
pip install selenium

STEP 2
download ChromeDriver, https://chromedriver.chromium.org/
and add it to system PATH (Google: "Add ChromveDriver to PATH")

STEP 3
Create a file in the same folder as this code called ".env", whose contents are
PEERWISEUSER = <peerwise username>
PEERWISEPW = <peerwise password>

STEP 4
Adjust the "NUM_QUESTIONS" variable on line 29 of this file to reflect the number of questions
'''
import os
import dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

NUM_QUESTIONS = 539 # NUMBER OF QUESTIONS CURRENTLY ON PEERWISE

driver: webdriver.Chrome = webdriver.Chrome()

dotenv.load_dotenv()  # Load credentials from file

driver.get("https://peerwise.cs.auckland.ac.nz/at/?utoronto_ca")

# LOG INTO PEERWISE
WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "user")))
driver.find_element_by_id("user").send_keys(os.environ.get("PEERWISEUSER"))
driver.find_element_by_id("pass").send_keys(os.environ.get("PEERWISEPW"))
driver.find_element_by_class_name("btn").click()

WebDriverWait(driver, 3).until(EC.title_contains("PeerWise"))
driver.get(
    "https://peerwise.cs.auckland.ac.nz/course/main.php?course_id=22474")

questionnumber = 0

# FIND ALL THE PAGES
for i in range(0, NUM_QUESTIONS, 10):
    offset = i + 1 # OFFSET NUMBER

    driver.get(
        f"https://peerwise.cs.auckland.ac.nz/course/main.php?cmd=showAnsweredQuestions&offset={offset}")

    elems = driver.find_elements_by_xpath("//a[@href]")
    valid_uris = [
        elem.get_attribute(
            "href") for elem in elems if "view" in elem.get_attribute("href")]

    for uri in valid_uris:
        # navigate to the question
        print(
            f"Question Number {questionnumber} -- Currently processing: " + uri)

        driver.get(uri)  # navigate to question

        # Wait for table to load
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "displayQuestionTable")))

        questionbox: WebElement = driver.find_element_by_id("questionDisplay")
        answerbox: WebElement = driver.find_element_by_id("displayQuestionTable")

        driver.execute_script("arguments[0].scrollIntoView();", answerbox)  # scroll to bottom of the page

        # FILE OUTPUTS
        with open(f"questions/question{questionnumber}.png", "wb") as f:
            f.write(answerbox.screenshot_as_png)

        with open("questions/peerwise_questions.txt", "a", encoding="utf-8") as f:
            f.write(str(questionnumber) + ". Page: " + uri + "\n" + questionbox.text + "\n\n")

        with open("questions/peerwise_questions.md", "a", encoding="utf-8") as f:
            f.write(f"### [Question {questionnumber}]({uri})\n\n" + questionbox.text + f"\n\n![question{questionnumber}.png](question{questionnumber}.png)\n\n\n")

        questionnumber += 1

# N.B. After running the code, convert the peerwise_question.md file to HTML using some other tool. 
# One example is https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf
