from filter import filter_jobs

jobs = [
    ("Python Developer", "Google", "Lahore"),
    ("Cyber Security Intern", "NCCS", "Islamabad"),
    ("Frontend Developer", "Systems Ltd", "Karachi")
]

print("Search by title:")
print(filter_jobs(jobs, "Python"))

print()

print("Search by company:")
print(filter_jobs(jobs, "Google"))

print()

print("Search by location:")
print(filter_jobs(jobs, "Karachi"))