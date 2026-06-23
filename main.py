import pandas as pd
import sys
from datetime import datetime, timezone
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def main():
    print("Starting script")
    url = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums"
    driver = handle_connection_to_url(url)
    #get played match data
    elems = driver.find_elements(By.TAG_NAME,"a")
    print(f"- Found {len(elems)} <a> elements") 
    played_matches = filter_for_played_matches(elems)
    driver.quit()
    print("- Closed driver connection")
    df_long = parse_to_data_table_long(played_matches)
    df_html_str = df_long.to_html()
    export_to_index_html(df_html_str)
    print("- Finished exporting data")
    print("Finished script")

def get_update_period():
    try:
        update_period_hrs = sys.argv[1]
    except IndexError:
        update_period_hrs = 6
    return float(update_period_hrs)

def handle_connection_to_url(url):
    print(f"- Setting up selenium driver")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)

    # #fetch url
    print(f"- Fetching html from url")
    driver.get(url)

    # wait for page to load and capture HTML
    driver.set_page_load_timeout(30)
    # navigate cookies (use explicit waits to avoid hangs if elements are absent)
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
    except Exception:
        pass

    print("- Fetched Url")

    return driver

def parse_to_data_table_wide(matches):
    i=1
    match_n=[]
    stage=[]
    teamA_name=[]
    teamA_score=[]
    teamB_name =[]
    teamB_score=[]
    for teams in matches:
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
    for teams in matches:
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
    
    print("- Created data table from matches")

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

def filter_for_played_matches(elems):
    result = []
    # naive range check
    temp = elems[23:135]

    for line in temp:
        if " v " in line.text: continue
        if "-" not in line.text: continue
        parts = line.text.split("-")
        if len(parts) == 2: result.append(parts)

    print(f"- Found {len(result)} concluded matches")
        
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
    
def export_to_index_html(df_html_str):
    template = """
    <html>
    <head>
        <title>World Cup 2026 Match Results</title>
        <h1 data-last-update="{last_update_epoch}"></h1>
        <h1 data-update-period="{update_period_epoch}"></h1>
    </head>
    <body>
        <h1>World Cup 2026 Match Results</h1>
        <p id="last-update"></p>
        <p id="next-update"></p>
        {table}
    </body>
    <script src="index.js" defer></script>
    </html>
    """
    page_html = template.format(
            last_update_epoch=int(datetime.now(tz=timezone.utc).timestamp()),
            update_period_epoch=get_update_period() * 3600,
            table=df_html_str
        )    

    index_file_path = Path(__file__).parent / "index.html"
    with open(index_file_path, "w") as f:
        f.write(page_html)
    print(f"- Exported data to {index_file_path}")

if __name__ == "__main__":
    main()
