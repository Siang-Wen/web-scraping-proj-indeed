from bs4 import BeautifulSoup
import re, random, math, csv, time, datetime
from curl_cffi import requests as cureq

# HTML Retrieval Error Handler
class HTMLRetrievalError(Exception):
    pass

# To GET HTML from URL and parse using BeautifulSoup
def retrieve_html(url, headers):
    results = cureq.get(url, headers=headers)
    if results.status_code != 200:
        for i in range(5):  # 5 retries in case of blokcing from bots
            time.sleep(5)
            results = cureq.get(url, headers=headers)
            if results.status_code == 200:
                break
    if results.status_code == 200:
        return BeautifulSoup(results.text, "html.parser")
    else:
        raise HTMLRetrievalError("Unable to parse blocked HTML contents!")

# To create CSV file from the information gathered
def create_csv(search_term, location, search_result):
    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%Y%m%d")
    # Specify the CSV file name
    file_name = f'{formatted_date}_job_list_{search_term.lower().replace("+", "_")}_{location.lower().replace("+", "_")}.csv'
    # Writing to the CSV file
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Job Title', 'Company Name', 'Location', 'Remarks'])
        # Write the header
        writer.writeheader()
        # Write the data
        writer.writerows(search_result)
    return file_name

def main(search_term, location):
    try:
        job_titles = []
        job_companies = []
        job_locations = []
        remarks = []
        search_result = []

        search_term = search_term.replace(" ", "+")
        location = location.replace(" ", "+")

        url = f"https://au.indeed.com/jobs?q={search_term}&l={location}&sort=date"
        # Create randomized user agents to simulate a real user
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
        ]
        headers = {
            'User-Agent': random.choice(user_agents)
        }

        results_html = retrieve_html(url, headers=headers)

        # Find the number of jobs available
        jobs_num_tag = results_html.find("meta", attrs={"name": "description"})
        num_of_jobs = int(jobs_num_tag["content"].split(" ")[1].replace(",", ""))
        num_of_pages = math.ceil(num_of_jobs/15)

        for page in range(num_of_pages):
            if page == 5:   # Collect the info of the jobs up to a maximum of 5 pages
                break
            else:
                url = f"https://au.indeed.com/jobs?q={search_term}&l={location}&sort=date&start={page}0"
                results_html = retrieve_html(url, headers=headers)
            job_results_div = results_html.find("div", id = "mosaic-jobResults")    # Focus on the div with all the jobs info
            # Find the all the job titles from the parsed page
            job_titles_tags = job_results_div.find_all("span", id=re.compile(r'jobtitle', re.IGNORECASE))
            for job_title_tag in job_titles_tags:
                job_titles.append(job_title_tag.string)
            # Find the respective employers from the parsed html
            job_companies_tags = job_results_div.find_all("span", attrs={"data-testid": "company-name"})
            for job_companies_tag in job_companies_tags:
                job_companies.append(job_companies_tag.string)
            # Find the respective employers' location from the parsed html
            job_locations_tags = job_results_div.find_all("div", attrs={"data-testid": "text-location"})
            for job_locations_tag in job_locations_tags:
                job_locations.append(job_locations_tag.string)
                # Find the respective remarks for each job from the parsed html
                remark_tags = job_locations_tag.find_parent(class_ = re.compile(r'company_location')).parent.find(class_ = re.compile(r'jobMetaDataGroup', re.IGNORECASE)).find_all("div", attrs={"data-testid":"attribute_snippet_testid"})
                if len(remark_tags) == 0: # Check if remark is available for each job and put "--" for jobs without remarks
                    remarks.append("--")
                else:
                    buff_list = []
                    for remark_tag in remark_tags:
                        buff_list.append(remark_tag.get_text(strip = True))
                    remarks.append(":".join(buff_list)) # Join the remarks with ":" symbol if there are more than one remark for a job
            time.sleep(2)

        # Create a list containing dictionaries of each job's info
        for i in range(len(job_titles)):
            buffer_dict = {}
            buffer_dict["Job Title"] = job_titles[i]
            buffer_dict["Company Name"] = job_companies[i]
            buffer_dict["Location"] = job_locations[i]
            buffer_dict["Remarks"] = remarks[i]
            search_result.append(buffer_dict)

        csv_file = create_csv(search_term, location, search_result)
        print(f"CSV file '{csv_file}' created successfully.")

    except HTMLRetrievalError as e:
        print(f"Caught an exception: {e}")

if __name__ == "__main__":
    main("Python", "Melbourne")