def filter_jobs(jobs, keyword):
    """
    Filter jobs by title, company, or location.
    """

    filtered_jobs = []

    keyword = keyword.lower()

    for job in jobs:
        title = job[0].lower()
        company = job[1].lower()
        location = job[2].lower()

        if (
            keyword in title or
            keyword in company or
            keyword in location
        ):
            filtered_jobs.append(job)

    return filtered_jobs