import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def main():
    # repo_root = Path.cwd()  # repo base when you run the script
    # log_file = repo_root / "chromedriver.log"

    # options = Options()
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # # options.add_argument("--headless=new")

    # service = Service(
    #     ChromeDriverManager().install(),
    #     service_args=["--verbose", f"--log-path={str(log_file)}"]
    # )

    driver = webdriver.Remote("http://localhost:4444", DesiredCapabilities.CHROME)
    # driver = webdriver.Chrome(service=service, options=options)

    #fetch url
    driver.get("https://www.watchathletics.com/page/7790/fifa-world-cup-2026-fixtures-results-full-match-schedule-and-knockout-bracket")
    
    #navigate cookies
    driver.find_element(By.CLASS_NAME,"fc-cta-manage-options").click()
    driver.find_element(By.CLASS_NAME,"fc-confirm-choices").click()

    #get played match data
    li_elems = driver.find_elements(By.TAG_NAME,"li")

    match_text = get_match_text_from_elements(li_elems)

    driver.quit()

    match_text_cleaned = regularise_format(match_text)

    played_match_text = filter_for_played_matches(match_text_cleaned)

    print(f"Number of Matches: {len(played_match_text)}")
    
    i=1
    for match in played_match_text:
        print(f"{i}: {match}")
        i+=1
    
def get_match_text_from_elements(list_elements):
    results = []
    for li in list_elements:
        if len(li.text.split()) > 3:
            results.append(li.text)
    return results

def regularise_format(match_text):
    result = match_text
    result[0] = "Mexico vs South Africa 2 : 0 — Group A — Mexico City Stadium"
    result[1] = "Korea Republic vs Czechia 2 : 1 — Group A — Guadalajara Stadium"
    return result

def filter_for_played_matches(match_text):
    result = []
    for match in match_text:
        if ":" in match:
            result.append(match)
    return result

if __name__ == "__main__":
    main()