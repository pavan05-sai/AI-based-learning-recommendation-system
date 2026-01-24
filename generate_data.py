# generate_data.py
import json
import urllib.parse

branches = [
    "Computer Science Engineering",
    "Information Technology",
    "Artificial Intelligence & Machine Learning",
    "Data Science",
    "Web Development",
    "Cyber Security",
    "Cloud & DevOps",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Electronics & Communication Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Biotechnology",
    "Automobile Engineering",
    "Aerospace Engineering",
    "Instrumentation Engineering"
]

subjects_pool = {
    "Computer Science Engineering": [
        "Programming Fundamentals", "Data Structures", "Algorithms", 
        "Operating Systems", "DBMS", "Computer Networks", 
        "Software Engineering", "Web Technologies", "AI Basics", 
        "Cloud Computing", "Machine Learning", "Compiler Design"
    ],
    "Information Technology": [
        "IT Fundamentals", "Networking", "Database Systems", 
        "Web Programming", "Cyber Security Basics", "Scripting Languages",
        "E-Commerce", "Mobile Computing", "Data Mining", "Cloud Architecture"
    ],
    "Mechanical Engineering": [
        "Engineering Mechanics", "Thermodynamics", "Fluid Mechanics", 
        "Strength of Materials", "Machine Design", "Manufacturing Processes",
        "Heat Transfer", "Robotics", "Automobile Engineering", "CAD/CAM"
    ],
    "General": [
        "Engineering Mathematics-I", "Engineering Physics", "Engineering Chemistry",
        "Communication Skills", "Environmental Science", "Engineering Graphics"
    ]
}

def generate_subjects():
    subjects_data = []
    
    for branch in branches:
        branch_specific_pool = subjects_pool.get(branch, [])
        if not branch_specific_pool and "Engineering" in branch:
             branch_specific_pool = [f"{branch} Core {i}" for i in range(1, 10)]
        
        full_pool = subjects_pool["General"] + branch_specific_pool
        
        for sem in range(1, 9):
            sem_subjects = []
            start_index = (sem - 1) * 3
            count = 0
            while count < 5:
                idx = (start_index + count) % len(full_pool)
                subj_name = full_pool[idx]
                if subj_name not in [s['name'] for s in sem_subjects]:
                     sem_subjects.append({
                        "name": subj_name,
                        "branch": branch,
                        "semester": sem,
                        "roadmap": [
                            f"Introduction to {subj_name}",
                            f"Module 1: Basics of {subj_name}",
                            f"Module 2: Advanced Concepts",
                            f"Module 3: Practical Applications",
                            f"Review & Assessment"
                        ]
                     })
                count += 1
            subjects_data.extend(sem_subjects)
    return subjects_data

def generate_resources(subjects_list):
    resources_data = []
    for sub in subjects_list:
        # Notes: Direct tutorial URL
        note_slug = sub['name'].replace(' ', '-').lower()
        notes_link = f"https://www.geeksforgeeks.org/{note_slug}/"
        
        # Video: SUBJECT-SPECIFIC YouTube Search Embed
        # This will automatically find and play the most relevant video for the TOPIC
        query_video = urllib.parse.quote(f"{sub['name']} {sub['branch']} engineering tutorial")
        video_embed_url = f"https://www.youtube.com/embed?listType=search&list={query_video}"
        
        resources_data.append({
            "branch": sub["branch"],
            "semester": sub["semester"],
            "subject": sub["name"],
            "note_url": notes_link,
            "video_url": video_embed_url
        })
    return resources_data

if __name__ == "__main__":
    print("Generating comprehensive seed data with TOPIC-SPECIFIC LINKS...")
    subs = generate_subjects()
    res = generate_resources(subs)
    
    with open("data/subjects.json", "w", encoding="utf-8") as f:
        json.dump(subs, f, indent=2)
    
    with open("data/resources.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
        
    print(f"Generated {len(subs)} subjects and {len(res)} topic-specific resource links.")
