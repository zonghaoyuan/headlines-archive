# https://docs.python.org/3/library/json.html
# This library will be used to parse the JSON data returned by the API.
import json
# https://docs.python.org/3/library/urllib.request.html#module-urllib.request
# This library will be used to fetch the API.
import urllib.request
# https://docs.python.org/3/library/urllib.error.html
# To handle potential request errors
import urllib.error
# https://docs.python.org/3/library/datetime.html
# To get the current time for the table title and filename
import datetime
# <<< 导入 timezone 和 timedelta >>>
from datetime import timezone, timedelta
# https://docs.python.org/3/library/time.html
# To add delays between requests
import time # <<< 导入 time 模块
import os # <<< 导入 os 模块
from dotenv import load_dotenv # <<< 导入 dotenv 库

# --- Load Environment Variables ---
load_dotenv() # <<< 加载 .env 文件中的环境变量

# --- Configuration ---
# !!! 请确保您的项目根目录有一个 .env 文件，其中包含 API_KEY=your_actual_key !!!
apikey = os.getenv("API_KEY") # <<< 从环境变量获取 API_KEY

# <<< 添加检查，确保 API 密钥已加载 >>>
if not apikey:
    print("Error: API_KEY not found in .env file or environment variables.")
    print("Please create a .env file in the project root with the following content:")
    print("API_KEY=YOUR_GNEWS_API_KEY")
    exit(1) # 退出脚本

# apikey = "16ebd207b8767acd777488ae00e6c1c4" # 使用你提供的key，但建议从安全的地方读取 # <<< 移除硬编码的 key
categories = ["general", "world", "nation", "business", "technology", "entertainment", "sports", "science", "health"]
base_url = "https://gnews.io/api/v4/top-headlines?lang=en&country=us&max=10&apikey={apikey}&category={category}"

# --- Get Current Time ---
# <<< 定义北京时区 (UTC+8) >>>
beijing_tz = timezone(timedelta(hours=8))
# <<< 获取当前的 UTC 时间 >>>
utc_now = datetime.datetime.now(timezone.utc)
# <<< 转换为北京时间 >>>
beijing_now = utc_now.astimezone(beijing_tz)

# 用于 Markdown 表格标题的时间格式 (e.g., 2025-04-30 13:20 Beijing Time)
formatted_title_time = beijing_now.strftime("%Y-%m-%d %H:%M") + " Beijing Time" # <<< 使用北京时间并添加时区说明
# 用于文件名的时间格式 (e.g., 20250430_1320) - 基于北京时间
formatted_filename_time = beijing_now.strftime("%Y%m%d_%H%M") # <<< 使用北京时间

# --- Prepare Markdown Table ---
markdown_output = []
markdown_output.append(f"# News Today -- Fetched at {formatted_title_time}") # <<< 更新标题以使用新的时间格式
markdown_output.append("") # Add an empty line for spacing
markdown_output.append("| Category | Title | Description | URL |")
markdown_output.append("|---|---|---|---|") # Header separator

# --- Fetch and Process News for Each Category ---
print("Fetching news...") # Add progress indicator

for i, category in enumerate(categories): # 使用 enumerate 获取索引
    print(f"Fetching category: {category} ({i+1}/{len(categories)})...")
    url = base_url.format(apikey=apikey, category=category)
    # print(f"Requesting URL: {url}") # For debugging

    try:
        with urllib.request.urlopen(url) as response:
            # Check if the request was successful
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                articles = data.get("articles", []) # Use .get() for safety

                if not articles:
                    print(f"  No articles found for category: {category}")
                    # Optionally add a placeholder row in the table
                    # markdown_output.append(f"| {category} | No articles found | - | - |")
                    # continue # Skip to the next category # 移除 continue，确保即使没有文章也会执行延时

                for article in articles:
                    # Get data safely, providing defaults for missing fields
                    title = article.get('title', 'N/A')
                    description = article.get('description', 'N/A')
                    article_url = article.get('url', '#') # Use '#' if URL is missing

                    # Clean data for Markdown table (remove pipes and newlines)
                    title = title.replace('|', '\|').replace('\n', ' ').replace('\r', '')
                    # Ensure description is not None before replacing
                    if description:
                        description = description.replace('|', '\|').replace('\n', ' ').replace('\r', '')
                    else:
                        description = 'N/A' # Handle None case explicitly

                    # Append data row to Markdown table
                    markdown_output.append(f"| {category} | {title} | {description} | {article_url} |")

            else:
                 print(f"  Error fetching category {category}: HTTP Status {response.status}")
                 # Add error row to table
                 markdown_output.append(f"| {category} | Error fetching | HTTP Status {response.status} | - |")

    except urllib.error.HTTPError as e:
        print(f"  HTTP Error for category {category}: {e.code} {e.reason}")
        error_reason = f"{e.code} {e.reason}"
        if e.code == 401:
             error_reason += " (Check API Key)"
        elif e.code == 403:
             error_reason += " (Forbidden - Check API Key/Plan)"
        elif e.code == 429:
             error_reason += " (Rate Limit Exceeded)"
        markdown_output.append(f"| {category} | HTTP Error | {error_reason} | - |")
    except urllib.error.URLError as e:
        print(f"  URL Error for category {category}: {e.reason}")
        markdown_output.append(f"| {category} | URL Error | {e.reason} | - |")
    except json.JSONDecodeError as e:
        print(f"  JSON Decode Error for category {category}: {e}")
        markdown_output.append(f"| {category} | JSON Error | Could not parse response | - |")
    except Exception as e:
        print(f"  An unexpected error occurred for category {category}: {e}")
        markdown_output.append(f"| {category} | Unexpected Error | {e} | - |")

    # --- Add Delay ---
    if i < len(categories) - 1:
        print("  Waiting 2 seconds before next category...")
        time.sleep(2) # <<< 等待 2 秒

print("\nFetching complete.\n")

# --- Print the final Markdown table ---
print("--- Generated Markdown Table ---")
print('\n'.join(markdown_output))
print("-------------------------------\n")

# --- (Optional) Save to a file ---
try:
    # 使用格式化后的时间戳来命名文件
    filename = f"news_{formatted_filename_time}.md" # <<< 修改文件名格式
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_output))
    print(f"Markdown table saved to file: {filename}") # <<< 打印正确的文件名
except IOError as e:
    print(f"Error saving file {filename}: {e}")
