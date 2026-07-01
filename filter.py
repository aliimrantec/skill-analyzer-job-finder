def filter_jobs(jobs, keyword):
    """
    Filter jobs using a keyword.
    """

    filtered_jobs = []

    for job in jobs:
        if keyword.lower() in str(job).lower():
            filtered_jobs.append(job)

    return filtered_jobs