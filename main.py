import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def main():

    print("Starting script")

    url = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums"
    print(f"- Fetching html from url")
    driver = handle_connection_to_url(url)
    print("- Fetched Url")

    #get played match data
    elems = driver.find_elements(By.TAG_NAME,"a")
    print(f"- Found {len(elems)} <a> elements")
   
    played_match_text = filter_for_played_match_text(elems)
    print(f"- Filtered to {len(played_match_text)} concluded matches")

    driver.quit()
    print("- Closed driver connection")

    df_long = parse_to_data_table_long(played_match_text)
    print("- Created data table from matches")

    df_long.to_html("index.html")
    print("- Finished exporting data")

    print("Finished script")

def handle_connection_to_url(url):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")

    driver = webdriver.Remote("http://localhost:4444",DesiredCapabilities.CHROME, options=options)

    # #fetch url
    driver.get(url)

    # wait for page to load and capture HTML
    driver.set_page_load_timeout(30)
    # navigate cookies (use explicit waits to avoid hangs if elements are absent)
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
    except Exception:
        pass

    return driver

def parse_to_data_table_wide(matches):
    i=1
    match_n=[]
    stage=[]
    teamA_name=[]
    teamA_score=[]
    teamB_name =[]
    teamB_score=[]
    for match in matches:
        teams = match.split("-")
        if len(teams) != 2:
            print(f"skipping match: {i}")
            continue

        match_n.append(i)
        parts = teams[0].split()
        teamA_score.append(parts[-1])
        teamA_name.append(' '.join(parts[0:-1]))
        parts = teams[1].split()
        teamB_score.append(parts[0])
        teamB_name.append(' '.join(parts[1:]))
        stage.append(get_stage(i))

        i+=1

    return pd.DataFrame(
        {
            'Match#':match_n,
            'Stage':stage,
            'TeamA':teamA_name,
            'TeamA Score':teamA_score,
            'TeamB':teamB_name,
            'TeamB Score':teamB_score
        }
    )

def parse_to_data_table_long(matches):
    i=1
    match_n=[]
    stage=[]
    team=[]
    score=[]
    result=[]
    for match in matches:
        teams = match.split("-")
        if len(teams) != 2:
            print(f"skipping match: {i}")
            continue

        s = get_stage(i)
        stage.append(s)
        stage.append(s)
        match_n.append(i)
        match_n.append(i)
        lhs = teams[0].split()
        rhs = teams[1].split()
        team.append(' '.join(lhs[0:-1]))
        team.append(' '.join(rhs[1:]))
        score.append(lhs[-1])
        score.append(rhs[0])
        result.append(get_score_outcome(lhs[-1], rhs[0]))
        result.append(get_score_outcome(rhs[0], lhs[-1]))

        i+=1

    return pd.DataFrame(
        {
            'Match#':match_n,
            'Stage':stage,
            'Team':team,
            'Score':score,
            'Result':result
        }
    )
    
def get_score_outcome(score1, score2):
    if score1 > score2:
        return "Win"
    elif score1 < score2:
        return "Loss"
    else:
        return "Draw"

def filter_for_played_match_text(elems):
    result = []
    # naive range check
    temp = elems[23:135]

    for line in temp:
        if " v " in line.text: continue # yet to be played
        if "-" in line.text: result.append(line.text)
        
    return result

def print_results(results):
    print(f"Number of elements: {len(results)}")
    i=1
    for res in results:
        print(f"{i}: {res}")
        i+=1

def get_stage(match_number):
    if   match_number  < 73 and match_number > 0:  return "Group Stage"
    elif match_number  < 89:  return "Round of 32"
    elif match_number  < 97:  return "Round of 16"
    elif match_number  < 101: return "Quarter Finals"
    elif match_number  < 103: return "Semi Finals"
    elif match_number == 103: return "Third Place Playoff"
    elif match_number == 104: return "Final"
    else:
        return "Unknown Stage"

if __name__ == "__main__":
    main()