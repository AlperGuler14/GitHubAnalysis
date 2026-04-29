import requests
import sys
import pandas as pd 
import time
import os
from dotenv import load_dotenv

if sys.platform =="win32":
   import io
   sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
   print("warnning")
   sys.exit(1)

HEADERS = {"Authorization":f"token {GITHUB_TOKEN}"}

def fetch_github_repos(language,total_count = 500 ):
   
   all_repos = []
   per_page = 100
   pages = total_count // per_page


   for page in range(1, pages+1):
   
        url = f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&order=desc&per_page={per_page}&page={page}"
        try:
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    repo_info = {
                        "full_name": item["full_name"],
                        "stars": item["stargazers_count"],
                        "forks": item["forks_count"],
                        "open_issues": item["open_issues_count"],
                        "language": language,
                        "created_at": item["created_at"],
                        "pushed_at": item["pushed_at"],
                        "owner_type": item["owner"]["type"],
                        "size": item["size"]
                    }
                    all_repos.append(repo_info)
                
                print(f"[BILGI] {language}: Sayfa {page} bitti. Toplam: {len(all_repos)}")
                # API Limitlerini korumak icin bekleme
                time.sleep(2) 

            elif response.status_code == 403:
                print("[WARNING] We've hit the speed limit. Please wait 60 seconds...")
                time.sleep(60)
            else:
                print(f"[HATA] {response.status_code}: {response.text}")
                break
        except Exception as e:
             print(f"[KRITIK] Bir hata olustu: {e}")
             break   
   return pd.DataFrame(all_repos)
if __name__ == "__main__":
    
    target_languages = ["python", "javascript", "typescript", "java", "cpp", "csharp", "php", "go", "rust", "swift","ruby", "kotlin", "dart", "html", "css","c", "scala", "r", "julia", "matlab", "lua", "perl", "haskell"]
    
    all_df = []

    for lang in target_languages:
        df_lang = fetch_github_repos(language =lang ,total_count = 500 )

        if not df_lang.empty:
            all_df.append(df_lang)
            print(f"[Okey] {lang} Added to the list.")
        
        time.sleep(3)
    if all_df:
        final_df = pd.concat(all_df, ignore_index=True)
        filename = "github_multi_lang_data.csv"
        final_df.to_csv(filename, index=False)
        
        print("\n" + "="*40)
        print(f" SUCCESSFUL: Data '{filename}' was saved to the file.")
        print(f" Total Rows: {len(final_df)}")
        print(f" Languages: {', '.join(target_languages)}")
        print("="*40)
    else:
        print("[ERROR] No data was collected. Check your token or internet connection.")