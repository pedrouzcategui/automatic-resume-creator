import re

job_desc = """
HireShire is a forward-thinking talent solutions and staffing platform, connecting global enterprises with top-tier professionals. As part of our expansion, we are launching a DevOps Engineering Internship for technically skilled individuals passionate about automating systems, optimizing cloud infrastructure, and enabling agile software delivery at scale.


Role Overview



As a DevOps Engineering Intern, you will collaborate with our engineering and infrastructure teams to design, implement, and optimize CI/CD pipelines, cloud deployments, and monitoring solutions. This internship is ideal for candidates eager to gain hands-on experience with real-world DevOps tools and practices used by top tech organizations.


Key Responsibilities



Assist in setting up and managing CI/CD pipelines using tools like Jenkins, GitHub Actions, or GitLab CI.
Work on containerization and orchestration using Docker and Kubernetes.
Automate cloud infrastructure provisioning using Infrastructure-as-Code (IaC) tools such as Terraform or CloudFormation.
Monitor system performance, availability, and security using tools like Prometheus, Grafana, and the ELK stack.
Collaborate with developers to troubleshoot build, deployment, and runtime issues in staging and production environments.
Support cloud resource optimization on AWS, Azure, or GCP for cost and performance efficiency.
Implement scripting solutions in Python, Bash, or similar for automation tasks.
Maintain configuration management using Ansible, Chef, or similar tools.


Requirements



Currently pursuing or recently graduated in Computer Science, Information Technology, or related fields.
Familiarity with version control systems (especially Git) and CI/CD concepts.
Understanding of basic cloud computing concepts (AWS, Azure, or GCP).
Knowledge of Linux/Unix systems and shell scripting.
Problem-solving attitude with attention to detail and eagerness to learn fast.


Nice to Have



Familiarity with Docker and Kubernetes.
Exposure to Infrastructure-as-Code tools like Terraform or Ansible.
Knowledge of logging and monitoring tools (Grafana, Prometheus, ELK).
Understanding of software development lifecycle (SDLC) and agile methodologies.
Familiarity with networking concepts (DNS, firewalls, load balancing).


What You’ll Gain

Real-world experience managing scalable, cloud-native DevOps environments.
Mentorship from senior DevOps engineers and architects.
Exposure to DevSecOps practices and modern automation frameworks.
Internship certificate & recommendation letter upon successful completion.
Possibility of Pre-Placement Offer (PPO) at HireShire or partner firms.


Stipend

The internship offers a minimum stipend of 20USD/hour, with potential for a higher rate based on performance during assessments and interviews.
"""

all_skills = ['jenkins', 'github', 'github actions', 'gitlab', 'aws', 'azure', 'gcp', 'C++', 'C', 'Grafana']
my_skills = ['github', 'aws']

def find_skills_gap(job_skills: list, my_skills: list):
    job_set = {s.lower() for s in job_skills} # Is this what is known as list comprehension?
    my_set = {s.lower() for s in my_skills}

    matching_skills = job_set.intersection(my_set)

    missing_skills = job_set - my_set

    return list(matching_skills), list(missing_skills)

def extract_keywords_from_job_description(job_description: str) -> list:
    lowercase_job_description = job_description.lower()
    '''
    I have a job description, I want to extract a list of skills from said description.
    Should I:
    1. Split text and convert it into an array?
    2. Analyze text without splitting an array?
    '''

    found_skills = []
    for skill in all_skills:
        pattern = rf"\b{re.escape(skill.lower())}\b"
        
        if re.search(pattern, lowercase_job_description):
            found_skills.append(skill)

    [x, y] = find_skills_gap(found_skills, my_skills)
    print(f"Matching Skills {x}\n")
    print(f"Missing Skills {y}\n")


extract_keywords_from_job_description(job_description=job_desc)