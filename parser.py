import re
import math
import spacy
from collections import Counter
from pypdf import PdfReader

# Initialize spaCy model globally
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Predefined Skill Taxonomy
SKILLS_TAXONOMY = {
    "Backend & Databases": [
        "python", "java", "c++", "c#", "golang", "go", "ruby", "rust", "node.js", "nodejs", 
        "express", "django", "flask", "fastapi", "spring boot", "microservices", "api", "rest api", 
        "graphql", "sql", "mysql", "postgresql", "mongodb", "redis", "cassandra", "sqlite", 
        "oracle", "firebase", "elasticsearch", "dynamodb"
    ],
    "Frontend & Web": [
        "javascript", "typescript", "react", "angular", "vue", "next.js", "nextjs", "html", "html5", 
        "css", "css3", "tailwind", "tailwind css", "bootstrap", "sass", "less", "jquery", "webpack", 
        "redux", "vuex"
    ],
    "Data Science & AI/ML": [
        "machine learning", "deep learning", "nlp", "natural language processing", "computer vision", 
        "pytorch", "tensorflow", "scikit-learn", "sklearn", "keras", "pandas", "numpy", "spacy", 
        "nltk", "opencv", "matplotlib", "seaborn", "tableau", "powerbi", "power bi", "r", 
        "apache spark", "spark", "hadoop", "data mining", "data analysis", "data science"
    ],
    "DevOps & Cloud": [
        "docker", "kubernetes", "k8s", "aws", "amazon web services", "gcp", "google cloud", 
        "azure", "devops", "ci/cd", "jenkins", "github actions", "gitlab ci", "terraform", 
        "ansible", "linux", "nginx", "apache", "bash", "shell"
    ],
    "Mobile & Systems": [
        "swift", "kotlin", "flutter", "react native", "objective-c", "android", "ios", 
        "c", "embedded systems", "arduino", "raspberry pi"
    ],
    "Methodologies & Soft Skills": [
        "agile", "scrum", "product management", "system design", "sdlc", "git", "github", 
        "gitlab", "jira", "leadership", "communication", "teamwork", "problem solving", 
        "critical thinking", "project management", "collaboration", "analytical skills"
    ]
}

# Stopwords for keyword matching & similarity calculations
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", 'using', 'also', 'development',
    'experience', 'work', 'project', 'team', 'system', 'skills', 'application', 'design', 'software', 'technology',
    'working', 'responsibilities', 'responsible', 'duties', 'role'
}

# Action verbs to search for in Experience section
ACTION_VERBS = [
    "led", "managed", "designed", "developed", "built", "implemented", "created", "spearheaded",
    "engineered", "architected", "optimized", "improved", "launched", "achieved", "delivered",
    "analyzed", "facilitated", "formulated", "initiated", "resolved", "coordinated", "collaborated",
    "increased", "reduced", "saved", "maximized", "minimized", "streamlined", "transformed"
]

def extract_text_from_pdf(pdf_file):
    """Extracts raw text from a PDF file object or bytes."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_contact_info(text):
    """Extracts email, phone number, and professional links from the text."""
    # Standard email regex
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    # Standard phone regex (handles formats: +1-234-567-8900, (123) 456-7890, 123.456.7890, etc.)
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    # Professional links
    linkedin_regex = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    github_regex = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
    portfolio_regex = r'(?:https?://)?(?:www\.)?(?:[a-zA-Z0-9_-]+\.)*(?:portfolio|me|xyz|io|com|net|org)(?:/[a-zA-Z0-9_-]*)*'

    emails = re.findall(email_regex, text)
    phones = re.findall(phone_regex, text)
    linkedins = re.findall(linkedin_regex, text)
    githubs = re.findall(github_regex, text)
    
    # Basic portfolio extraction (avoid extracting standard emails or generic websites)
    portfolios = []
    all_links = re.findall(r'https?://[^\s]+', text)
    for link in all_links:
        link_clean = link.strip('.,()[]{}<>')
        if 'linkedin.com' not in link_clean and 'github.com' not in link_clean:
            portfolios.append(link_clean)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedins[0] if linkedins else None,
        "github": githubs[0] if githubs else None,
        "portfolio": portfolios[0] if portfolios else None
    }

def detect_sections(text):
    """Detects presence of standard resume sections."""
    sections = {
        "Summary/Objective": ["summary", "objective", "profile", "professional summary", "about me", "executive summary"],
        "Experience": ["experience", "employment", "work history", "professional experience", "career history", "work experience"],
        "Education": ["education", "academic", "qualifications", "educational background", "academic background"],
        "Skills": ["skills", "technical skills", "core competencies", "technologies", "expertise", "languages"],
        "Projects": ["projects", "personal projects", "academic projects", "key projects", "selected projects"],
        "Certifications": ["certifications", "certificates", "awards", "courses", "achievements", "accomplishments"]
    }
    
    found_sections = {}
    text_lower = text.lower()
    
    for section_name, keywords in sections.items():
        found = False
        for kw in keywords:
            # Check for keyword as standalone header line or preceded by newline
            pattern = rf'(?:^|\n)\s*{re.escape(kw)}\s*(?:\n|:|-|$)'
            if re.search(pattern, text_lower):
                found = True
                break
        found_sections[section_name] = found
        
    return found_sections

def find_skills(text):
    """Extracts and groups skills found in the text according to our taxonomy."""
    text_lower = text.lower()
    identified_skills = {}
    
    for category, skills in SKILLS_TAXONOMY.items():
        identified_skills[category] = []
        for skill in skills:
            escaped = re.escape(skill)
            # Custom boundary checking supporting C++, Node.js, C#, etc.
            if skill.endswith('+') or skill.endswith('#') or '.' in skill:
                pattern = rf'(?:^|[^a-zA-Z0-9]){escaped}(?:[^a-zA-Z0-9]|$)'
            else:
                pattern = rf'\b{escaped}\b'
                
            if re.search(pattern, text_lower):
                # Standardize casing for UI
                display_name = skill
                if skill == "go":
                    display_name = "Golang"
                elif len(skill) <= 3 and skill not in ["css", "git", "nlp", "r", "k8s", "c"]:
                    display_name = skill.upper()
                else:
                    display_name = " ".join([word.capitalize() for word in skill.split()])
                    # special corrections
                    display_name = display_name.replace("Js", "JS").replace("Api", "API").replace("Sql", "SQL")
                    display_name = display_name.replace("Html5", "HTML5").replace("Css3", "CSS3")
                    display_name = display_name.replace("Aws", "AWS").replace("Gcp", "GCP").replace("Sdlc", "SDLC")
                    display_name = display_name.replace("Pytorch", "PyTorch").replace("Tensorflow", "TensorFlow")
                    display_name = display_name.replace("Github", "GitHub").replace("Gitlab", "GitLab")
                    display_name = display_name.replace("Devops", "DevOps").replace("Powerbi", "Power BI")
                
                identified_skills[category].append(display_name)
                
    return identified_skills

def clean_and_tokenize(text):
    """Cleans text and tokenizes into words, filtering stopwords and punctuation."""
    text = text.lower()
    # Replace non-alphanumeric (keep + and # for C++, C#)
    text = re.sub(r'[^a-z0-9+#\s-]', ' ', text)
    words = text.split()
    # Filter stopwords and short tokens (except standard skills like Go, R, C)
    filtered_words = [
        w for w in words 
        if w not in STOPWORDS and (len(w) > 2 or w in ['go', 'r', 'c', 'c#', 'c++'])
    ]
    return filtered_words

def calculate_cosine_similarity(text1, text2):
    """Calculates Cosine Similarity between two texts using manual TF representation."""
    tokens1 = clean_and_tokenize(text1)
    tokens2 = clean_and_tokenize(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
        
    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    
    numerator = sum(vec1[x] * vec2[x] for x in intersection)
    
    sum1 = sum(vec1[x]**2 for x in vec1.keys())
    sum2 = sum(vec2[x]**2 for x in vec2.keys())
    
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def analyze_job_description(resume_text, jd_text):
    """Matches the resume text against the Job Description."""
    if not jd_text or not jd_text.strip():
        return None
        
    similarity = calculate_cosine_similarity(resume_text, jd_text)
    
    # Extract potential skills from JD
    jd_skills = find_skills(jd_text)
    resume_skills = find_skills(resume_text)
    
    flat_jd_skills = set()
    for cat_skills in jd_skills.values():
        flat_jd_skills.update(cat_skills)
        
    flat_resume_skills = set()
    for cat_skills in resume_skills.values():
        flat_resume_skills.update(cat_skills)
        
    # Find matching and missing skills
    matched_skills = list(flat_jd_skills & flat_resume_skills)
    missing_skills = list(flat_jd_skills - flat_resume_skills)
    
    # General keyword overlap analysis
    jd_tokens = clean_and_tokenize(jd_text)
    resume_tokens = clean_and_tokenize(resume_text)
    
    # Top keywords in JD (excluding already identified skills)
    jd_word_counts = Counter(jd_tokens)
    top_jd_words = [word for word, count in jd_word_counts.most_common(20)]
    
    # Filter out words that are part of identified skills
    skill_words = set()
    for skill in flat_jd_skills:
        skill_words.update(skill.lower().split())
        
    top_keywords_filtered = [
        word for word in top_jd_words 
        if word not in skill_words and len(word) > 3
    ][:10]
    
    matched_keywords = [w for w in top_keywords_filtered if w in resume_tokens]
    missing_keywords = [w for w in top_keywords_filtered if w not in resume_tokens]
    
    # Similarity Match percentage (0-100)
    match_percentage = int(similarity * 100)
    
    # Normalize similarity: even a highly matched resume rarely exceeds 0.6-0.7 raw cosine similarity
    # We will scale it: raw similarity of 0.45 or more is a near perfect match (90%+)
    scaled_match_score = min(100, int((similarity / 0.5) * 100)) if similarity > 0 else 0
    # Blend skill match rate into it
    jd_skill_count = len(flat_jd_skills)
    if jd_skill_count > 0:
        skill_match_rate = len(matched_skills) / jd_skill_count
        final_match_score = int(0.6 * scaled_match_score + 0.4 * (skill_match_rate * 100))
    else:
        final_match_score = scaled_match_score
        
    return {
        "score": max(5, final_match_score),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "matched_keywords": sorted([w.capitalize() for w in matched_keywords]),
        "missing_keywords": sorted([w.capitalize() for w in missing_keywords])
    }

def generate_suggestions(text, contact_info, sections, skills, jd_analysis=None):
    """Generates detailed, high-value, actionable recommendations for the candidate."""
    suggestions = []
    
    # 1. Missing sections suggestion
    missing_sections = [sec for sec, found in sections.items() if not found]
    if missing_sections:
        suggestions.append({
            "category": "Structure & Formatting",
            "impact": "High",
            "title": f"Add missing essential sections: {', '.join(missing_sections)}",
            "description": "Standard ATS parsers scan your resume for recognizable section headings. Make sure your headings use conventional naming conventions (e.g., 'Work Experience' instead of 'Where I've Been') to avoid layout parsing errors."
        })
        
    # 2. Contact details suggestion
    missing_contact = []
    if not contact_info["phone"]: missing_contact.append("Phone Number")
    if not contact_info["email"]: missing_contact.append("Email Address")
    if not contact_info["linkedin"]: missing_contact.append("LinkedIn Profile Link")
    
    if missing_contact:
        suggestions.append({
            "category": "Contact Details",
            "impact": "High",
            "title": f"Include critical contact info: {', '.join(missing_contact)}",
            "description": "Recruiters cannot contact you if your information is hidden or missing. Adding an optimized LinkedIn URL increases profile views and builds professional credibility."
        })
        
    # 3. GitHub/Portfolio suggestion (for technical resumes)
    has_tech_skills = any(len(skills[cat]) > 0 for cat in ["Backend & Databases", "Frontend & Web", "Data Science & AI/ML", "DevOps & Cloud"])
    if has_tech_skills and not contact_info["github"] and not contact_info["portfolio"]:
        suggestions.append({
            "category": "Online Presence",
            "impact": "Medium",
            "title": "Add GitHub or Online Portfolio link",
            "description": "For technical roles, showing proof of work through a GitHub profile, personal site, or portfolio is highly encouraged. It serves as an instant validator of your coding expertise."
        })

    # 4. Action verbs analysis
    text_lower = text.lower()
    found_verbs = [verb for verb in ACTION_VERBS if re.search(rf'\b{verb}\b', text_lower)]
    if len(found_verbs) < 5:
        suggestions.append({
            "category": "Content & Writing",
            "impact": "High",
            "title": "Incorporate strong action verbs",
            "description": f"Your resume uses {len(found_verbs)} standard action verbs. Elevate your bullet points by starting each with dynamic, result-oriented words (e.g., 'Spearheaded', 'Architected', 'Optimized', 'Streamlined') instead of passive phrases like 'Responsible for' or 'Helped with'."
        })
        
    # 5. Quantitative impact analysis (Metrics/Numbers)
    # Check if numbers, percentages, or dollar values exist in the bullet points
    metrics_matches = re.findall(r'\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\s*million|\s*k)?|\b\d+\s*(?:\+|-|x|percent|users|hours|dollars|gb|tb|million|billion)\b', text_lower)
    if len(metrics_matches) < 3:
        suggestions.append({
            "category": "Impact & Results",
            "impact": "High",
            "title": "Quantify your achievements with metrics",
            "description": "Resumes without numbers read like a list of job duties. Add metrics like performance improvements (e.g., 'reduced page load time by 30%'), cost savings (e.g., 'saved $5K in cloud costs'), or team scaling parameters to demonstrate tangible value."
        })

    # 6. Skill Density suggestions
    total_skills_count = sum(len(lst) for lst in skills.values())
    if total_skills_count < 6:
        suggestions.append({
            "category": "Skills & Competencies",
            "impact": "Medium",
            "title": "Expand technical skills section",
            "description": f"We detected only {total_skills_count} skills on your resume. Build a dedicated 'Technical Skills' section categorizing your competencies (Languages, Frameworks, Cloud, Databases) to make your resume highly searchable for automated screening tools."
        })
    elif total_skills_count > 30:
        suggestions.append({
            "category": "Skills & Competencies",
            "impact": "Low",
            "title": "Curate and streamline technical keywords",
            "description": f"You have listed {total_skills_count} technical skills. Keyword stuffing can actually hurt readability. Ensure every skill listed is relevant to your target role and that you are prepared to answer technical questions about them in interviews."
        })
        
    # 7. Job description specific suggestions
    if jd_analysis:
        if jd_analysis["missing_skills"]:
            top_missing = jd_analysis["missing_skills"][:5]
            suggestions.append({
                "category": "Job Description Alignment",
                "impact": "Critical",
                "title": f"Integrate missing target skills: {', '.join(top_missing)}",
                "description": "These core technical skills were found in the job description but are absent in your resume. If you have experience with these technologies, ensure they are clearly listed in your skills or experience descriptions."
            })
        if jd_analysis["missing_keywords"]:
            top_missing_kw = jd_analysis["missing_keywords"][:5]
            suggestions.append({
                "category": "ATS Keyword Optimization",
                "impact": "High",
                "title": f"Include standard industry terms: {', '.join(top_missing_kw)}",
                "description": "These important contextual words appear frequently in the job description. Weave these phrases naturally into your job descriptions or summary to optimize your matching profile against ATS algorithms."
            })
            
    # 8. Resume Length suggestion
    # Simple estimate of words
    word_count = len(text.split())
    if word_count > 0:
        if word_count < 200:
            suggestions.append({
                "category": "Resume Length",
                "impact": "Medium",
                "title": "Resume content is too brief",
                "description": "Your resume contains fewer than 200 words. A standard professional resume should have between 400 to 800 words of rich content explaining your work experience, projects, and impact."
            })
        elif word_count > 1200:
            suggestions.append({
                "category": "Resume Length",
                "impact": "Medium",
                "title": "Trim resume formatting (too wordy)",
                "description": f"Your resume has over {word_count} words. Recruiters scan resumes in under 7 seconds, and excessive text can dilute your key achievements. Condense your points and aim for a strict 1-page (for <5 years experience) or 2-page limit."
            })
            
    # Default suggestions if resume is already highly optimized
    if not suggestions:
        suggestions.append({
            "category": "Perfect Score",
            "impact": "Low",
            "title": "Resume is exceptionally formatted!",
            "description": "Your resume has high keyword matching, excellent formatting, clear structural headings, contact details, and lists high-impact metrics. Maintain direct references to your major projects."
        })
        
    return suggestions

def calculate_ats_score(sections, contact_info, skills, text, jd_analysis=None):
    """Calculates overall ATS / Optimization score out of 100."""
    score = 0
    
    # 1. Sections presence (max 30 pts)
    # 5 pts per essential section found
    essential_sections = ["Summary/Objective", "Experience", "Education", "Skills", "Projects", "Certifications"]
    for sec in essential_sections:
        if sections.get(sec, False):
            score += 5
            
    # 2. Contact details (max 15 pts)
    if contact_info["email"]: score += 5
    if contact_info["phone"]: score += 5
    if contact_info["linkedin"] or contact_info["github"]: score += 5
    
    # 3. Resume depth / metrics (max 20 pts)
    # Check action verbs
    text_lower = text.lower()
    found_verbs = [verb for verb in ACTION_VERBS if re.search(rf'\b{verb}\b', text_lower)]
    score += min(10, len(found_verbs) * 2) # max 10 pts
    
    # Check metrics
    metrics_matches = re.findall(r'\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\s*million|\s*k)?|\b\d+\s*(?:\+|-|x|percent|users|hours|dollars|gb|tb|million|billion)\b', text_lower)
    score += min(10, len(metrics_matches) * 2.5) # max 10 pts
    
    # 4. Skills match (max 35 pts)
    total_skills_count = sum(len(lst) for lst in skills.values())
    if total_skills_count >= 15:
        skills_score = 35
    elif total_skills_count >= 8:
        skills_score = 25
    elif total_skills_count >= 4:
        skills_score = 15
    else:
        skills_score = 5
        
    if jd_analysis:
        # If JD is provided, base the final 35 pts on JD alignment (job score out of 100, scaled to 35)
        jd_match_score = jd_analysis["score"]
        skills_score = int((jd_match_score / 100.0) * 35)
        
    score += skills_score
    
    return min(100, max(5, int(score)))

def extract_name(text):
    """Extracts candidate name using spaCy NER from the first portion of the resume."""
    if nlp is None:
        return "Candidate Details"
        
    try:
        # Process the first few lines of the text where the name usually appears
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        first_lines_text = "\n".join(lines[:8])
        doc = nlp(first_lines_text)
        
        # Look for PERSON entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                # Clean name: should have at least 2 words, only letters/spaces, and reasonable length
                if 2 <= len(name.split()) <= 4 and re.match(r'^[a-zA-Z\s\.\,\-]+$', name):
                    return name
    except Exception as e:
        print(f"Error extracting name using spaCy PERSON entity: {e}")
    
    # Fallback: take the first non-empty line if no PERSON entity is found
    for line in text.split("\n"):
        clean_line = line.strip()
        if clean_line and len(clean_line.split()) <= 4 and re.match(r'^[a-zA-Z\s\.\,\-]+$', clean_line):
            # Check it's not a common section header
            if clean_line.lower() not in ['summary', 'experience', 'education', 'skills', 'projects', 'resume', 'cv', 'about', 'contact']:
                return clean_line
                
    return "Candidate Details"

def extract_education_details(text):
    """Extracts degrees and universities from the text using NLP and regex."""
    degrees = []
    institutions = []
    
    # Regex to find degrees
    degree_patterns = [
        r'\b(?:B\.?S\.?|B\.?A\.?|B\.?E\.?|B\.?Tech|Bachelor(?:\'s)?)(?:\s+(?:of|in)\s+[a-zA-Z\s\-]+)?\b',
        r'\b(?:M\.?S\.?|M\.?A\.?|M\.?E\.?|M\.?Tech|Master(?:\'s)?)(?:\s+(?:of|in)\s+[a-zA-Z\s\-]+)?\b',
        r'\b(?:Ph\.?D\.?|Doctorate|Doctor(?:\'s)?)(?:\s+(?:of|in)\s+[a-zA-Z\s\-]+)?\b',
        r'\b(?:MBA|M\.?B\.?A\.?)\b'
    ]
    
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean_match = re.sub(r'\s+', ' ', match).strip()
            # Clean degree names slightly if they get overly long
            if len(clean_match) > 40:
                clean_match = clean_match[:37] + "..."
            if clean_match not in degrees:
                degrees.append(clean_match)
                
    # Use spaCy NER to find Universities
    if nlp is not None:
        try:
            doc = nlp(text[:8000]) # Limit parsing to first 8000 chars for efficiency
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    txt = ent.text.strip()
                    if any(kw in txt.lower() for kw in ["university", "college", "institute", "school", "academy", "polytechnic"]):
                        if txt not in institutions and 5 < len(txt) < 80:
                            institutions.append(txt)
        except Exception as e:
            print(f"Error extracting universities with spaCy: {e}")
            
    # Fallback to regex if no universities extracted via spaCy
    if not institutions:
        lines = text.split("\n")
        for line in lines:
            if any(kw in line.lower() for kw in ["university", "college", "institute", "school"]):
                clean_line = line.strip()
                if 5 < len(clean_line) < 80 and not any(header in clean_line.lower() for header in ["education", "experience", "summary"]):
                    institutions.append(clean_line)
                    
    return {
        "degrees": sorted(list(set(degrees)))[:3],
        "institutions": sorted(list(set(institutions)))[:3]
    }

def extract_experience_details(text):
    """Extracts employers and estimated years of experience from the text."""
    companies = []
    
    # Use spaCy NER to extract organization names that look like employers
    if nlp is not None:
        try:
            doc = nlp(text[:8000])
            exclude_kws = ["university", "college", "school", "institute", "academy", "foundation", "corporation of", "technologies", "association", "systems"]
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    txt = ent.text.strip()
                    if len(txt) > 3 and len(txt) < 60:
                        txt_lower = txt.lower()
                        # Check it doesn't represent a school/uni
                        if not any(kw in txt_lower for kw in exclude_kws):
                            # Ensure it isn't listed in our skill taxonomy
                            is_skill = False
                            for category, skills in SKILLS_TAXONOMY.items():
                                if any(s.lower() == txt_lower for s in skills):
                                    is_skill = True
                                    break
                            if not is_skill and txt not in companies:
                                companies.append(txt)
        except Exception as e:
            print(f"Error extracting employers with spaCy: {e}")
            
    # Fallback regex for experience years
    experience_years = 0
    year_matches = re.findall(r'\b(?:[1-9]|1\d|20)\+?\s*years?\s+(?:of\s+)?experience\b', text, re.IGNORECASE)
    if year_matches:
        num_match = re.search(r'\d+', year_matches[0])
        if num_match:
            experience_years = int(num_match.group())
            
    # Fallback to count date ranges (e.g. 2018 - 2022) to estimate years
    if experience_years == 0:
        year_ranges = re.findall(r'\b(20\d{2})\s*(?:-|to)\s*(20\d{2}|present)\b', text, re.IGNORECASE)
        total_duration = 0
        for start, end in year_ranges:
            start_yr = int(start)
            end_yr = 2026 if end.lower() == 'present' else int(end) # Use current local year 2026
            duration = end_yr - start_yr
            if 0 < duration < 15:
                total_duration += duration
        if total_duration > 0:
            experience_years = min(20, total_duration)

    return {
        "companies": sorted(list(set(companies)))[:4],
        "estimated_years": f"{experience_years}+ Years" if experience_years > 0 else "Not Specified"
    }

def analyze_resume(pdf_file, jd_text=None):
    """Main function called by app.py to fully analyze a resume PDF."""
    text = extract_text_from_pdf(pdf_file)
    if not text.strip():
        return {
            "success": False,
            "error": "Could not extract readable text from the uploaded PDF file. Please ensure the PDF contains searchable text and is not scanned."
        }
        
    contact_info = extract_contact_info(text)
    # Perform spaCy PERSON entity name extraction
    contact_info["name"] = extract_name(text)
    
    sections = detect_sections(text)
    skills = find_skills(text)
    
    # NLP-based extraction of Education & Careers Profiles
    education_info = extract_education_details(text)
    experience_info = extract_experience_details(text)
    
    # Analyze JD if provided
    jd_analysis = None
    if jd_text and jd_text.strip():
        jd_analysis = analyze_job_description(text, jd_text)
        
    ats_score = calculate_ats_score(sections, contact_info, skills, text, jd_analysis)
    suggestions = generate_suggestions(text, contact_info, sections, skills, jd_analysis)
    
    # Flatten skills for clean response
    flat_skills_count = sum(len(lst) for lst in skills.values())
    
    return {
        "success": True,
        "raw_text_preview": text[:2000] + ("...\n[Text truncated, full resume parsed in-memory]" if len(text) > 2000 else ""),
        "contact_info": contact_info,
        "sections": sections,
        "skills": skills,
        "skills_count": flat_skills_count,
        "education": education_info,
        "experience_details": experience_info,
        "jd_analysis": jd_analysis,
        "ats_score": ats_score,
        "suggestions": suggestions
    }
