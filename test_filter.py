from filter import filter_jobs

jobs = [
    ("Python Developer", "Google", "Lahore"),
    ("Cyber Security Intern", "NCCS", "Islamabad"),
    ("Frontend Developer", "Systems Ltd", "Karachi")
]

result = filter_jobs(jobs, "Cyber")

print(result)