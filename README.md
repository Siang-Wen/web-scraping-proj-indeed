# web-scraping-proj-indeed
This is a Web Scraping Project using Python on the Indeed Job-Searching Website.

This Python script allows you to input the position you are searching for, along with the location you are interested in, to scrape all available jobs from the first five pages of the Indeed website, sorted by date. The script outputs a CSV file that includes the job title, company, job location, and additional remarks for all available jobs found within those pages.

Inside the main function, there are two additional functions: retrieve_html() and create_csv(), which enhance the robustness of the code. To tackle the issue of bot blocking, the script implements five retries when making a URL request, and a random user-agent is selected for each request.
