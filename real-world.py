import requests
import pandas as pd
import sys
import time
import os
from dotenv import load_dotenv

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# .env yükle
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ GITHUB_TOKEN bulunamadı!")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com/search/repositories"


def fetch_repos(query="stars:>1000", per_page=100, max_pages=10):
    all_repos = []
    seen_ids = set()  # duplicate engellemek için

    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }

        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params)
        except requests.exceptions.RequestException as e:
            print("❌ Bağlantı hatası:", e)
            break

        if response.status_code != 200:
            print(f"❌ Hata kodu: {response.status_code}")
            print("Detay:", response.json())

            # Rate limit kontrolü
            if response.status_code == 403:
                print("⏳ Rate limit olabilir, 60 saniye bekleniyor...")
                time.sleep(60)
                continue
            break

        data = response.json()
        items = data.get("items", [])

        if not items:
            print("⚠️ Veri gelmedi, durduruluyor.")
            break

        for repo in items:
            if repo["id"] in seen_ids:
                continue

            seen_ids.add(repo["id"])

            all_repos.append({
                        "full_name": repo["full_name"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "open_issues": repo["open_issues_count"],
                        "language": repo["language"] or "Unknown",
                        "created_at": repo["created_at"],
                        "pushed_at": repo["pushed_at"],
                        "owner_type": repo["owner"]["type"],
                        "size": repo["size"]
                        

            })

        print(f"✅ Sayfa {page} çekildi | Toplam repo: {len(all_repos)}")

        time.sleep(1.2)  # rate limit güvenliği

    return pd.DataFrame(all_repos)


# Veri çek
df = fetch_repos(query="stars:>1000", max_pages=10)

# Kontrol
print("\n📊 İlk veriler:")
print(df.head())

# CSV kaydet
df.to_csv("github_repos.csv", index=False)

print("\n✅ Veri başarıyla kaydedildi: github_repos.csv")