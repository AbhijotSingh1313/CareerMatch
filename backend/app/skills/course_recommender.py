from urllib.parse import quote_plus
from app.skills.gap_analyzer import analyze_skill_gaps
from app.ai_service import ask_gemini_json


# ─── Real course database with verified direct links ───
COURSE_DB = {
    # Programming Languages
    "python": [
        {"name": "Python for Everybody Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/python", "difficulty": "Beginner", "free": True},
        {"name": "100 Days of Code - Python Pro Bootcamp", "provider": "Udemy", "url": "https://www.udemy.com/course/100-days-of-code/", "difficulty": "Beginner"},
    ],
    "javascript": [
        {"name": "JavaScript Algorithms and Data Structures", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "difficulty": "Beginner", "free": True},
        {"name": "The Complete JavaScript Course 2024", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-javascript-course/", "difficulty": "Beginner"},
    ],
    "typescript": [
        {"name": "Understanding TypeScript", "provider": "Udemy", "url": "https://www.udemy.com/course/understanding-typescript/", "difficulty": "Intermediate"},
        {"name": "TypeScript Full Course for Beginners", "provider": "YouTube (Dave Gray)", "url": "https://www.youtube.com/watch?v=gieEQFIfgYc", "difficulty": "Beginner", "free": True},
    ],
    "java": [
        {"name": "Java Programming and Software Engineering", "provider": "Coursera (Duke)", "url": "https://www.coursera.org/specializations/java-programming", "difficulty": "Beginner", "free": True},
        {"name": "Java Programming Masterclass", "provider": "Udemy", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/", "difficulty": "Beginner"},
    ],
    "c++": [
        {"name": "Beginning C++ Programming", "provider": "Udemy", "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/", "difficulty": "Beginner"},
        {"name": "C++ Tutorial for Beginners - Full Course", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=vLnPwxZdW4Y", "difficulty": "Beginner", "free": True},
    ],
    "c#": [
        {"name": "C# Basics for Beginners", "provider": "Udemy", "url": "https://www.udemy.com/course/csharp-tutorial-for-beginners/", "difficulty": "Beginner"},
    ],
    "go": [
        {"name": "Programming with Google Go Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/google-golang", "difficulty": "Intermediate", "free": True},
    ],
    "golang": [
        {"name": "Programming with Google Go Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/google-golang", "difficulty": "Intermediate", "free": True},
    ],
    "rust": [
        {"name": "The Rust Programming Language (Rustlings)", "provider": "GitHub", "url": "https://github.com/rust-lang/rustlings", "difficulty": "Beginner", "free": True},
        {"name": "Rust Programming Course", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=BpPEoZW5IiY", "difficulty": "Beginner", "free": True},
    ],
    "php": [
        {"name": "PHP for Beginners", "provider": "Udemy", "url": "https://www.udemy.com/course/php-for-complete-beginners-includes-msql-object-oriented/", "difficulty": "Beginner"},
    ],
    "ruby": [
        {"name": "Learn Ruby on Codecademy", "provider": "Codecademy", "url": "https://www.codecademy.com/learn/learn-ruby", "difficulty": "Beginner", "free": True},
    ],
    "swift": [
        {"name": "iOS & Swift - The Complete iOS App Development", "provider": "Udemy", "url": "https://www.udemy.com/course/ios-13-app-development-bootcamp/", "difficulty": "Beginner"},
    ],
    "kotlin": [
        {"name": "Android Basics with Compose", "provider": "Google (Android Developers)", "url": "https://developer.android.com/courses/android-basics-compose/course", "difficulty": "Beginner", "free": True},
    ],

    # Frontend Frameworks
    "react": [
        {"name": "React - The Complete Guide (incl. Next.js)", "provider": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "difficulty": "Intermediate"},
        {"name": "Full Stack Open - React", "provider": "University of Helsinki", "url": "https://fullstackopen.com/en/", "difficulty": "Intermediate", "free": True},
    ],
    "angular": [
        {"name": "Angular - The Complete Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-guide-to-angular-2/", "difficulty": "Intermediate"},
    ],
    "vue": [
        {"name": "Vue.js 3 Tutorial", "provider": "Vue Mastery", "url": "https://www.vuemastery.com/courses/intro-to-vue-3/intro-to-vue3", "difficulty": "Beginner", "free": True},
    ],
    "next.js": [
        {"name": "Next.js Learn Course", "provider": "Vercel", "url": "https://nextjs.org/learn", "difficulty": "Intermediate", "free": True},
    ],
    "html": [
        {"name": "Responsive Web Design", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "difficulty": "Beginner", "free": True},
    ],
    "css": [
        {"name": "Responsive Web Design", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "difficulty": "Beginner", "free": True},
        {"name": "CSS - The Complete Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/css-the-complete-guide-incl-flexbox-grid-sass/", "difficulty": "Beginner"},
    ],
    "tailwind": [
        {"name": "Tailwind CSS From Scratch", "provider": "Udemy", "url": "https://www.udemy.com/course/tailwind-css-from-scratch/", "difficulty": "Beginner"},
    ],

    # Backend / Frameworks
    "node.js": [
        {"name": "The Complete Node.js Developer Course", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/", "difficulty": "Intermediate"},
        {"name": "Node.js and Express.js Full Course", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=Oe421EPjeBE", "difficulty": "Beginner", "free": True},
    ],
    "nodejs": [
        {"name": "The Complete Node.js Developer Course", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/", "difficulty": "Intermediate"},
    ],
    "express": [
        {"name": "Node.js, Express, MongoDB & More", "provider": "Udemy", "url": "https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/", "difficulty": "Intermediate"},
    ],
    "django": [
        {"name": "Django for Everybody", "provider": "Coursera (UMich)", "url": "https://www.coursera.org/specializations/django", "difficulty": "Intermediate", "free": True},
    ],
    "flask": [
        {"name": "REST APIs with Flask and Python", "provider": "Udemy", "url": "https://www.udemy.com/course/rest-api-flask-and-python/", "difficulty": "Intermediate"},
    ],
    "fastapi": [
        {"name": "FastAPI Full Course", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=tLKKmouUams", "difficulty": "Intermediate", "free": True},
    ],
    "spring": [
        {"name": "Spring Boot 3, Spring 6 & Hibernate", "provider": "Udemy", "url": "https://www.udemy.com/course/spring-hibernate-tutorial/", "difficulty": "Intermediate"},
    ],
    "laravel": [
        {"name": "Laravel From Scratch", "provider": "Laracasts", "url": "https://laracasts.com/series/laravel-8-from-scratch", "difficulty": "Beginner", "free": True},
    ],

    # Databases
    "sql": [
        {"name": "SQL for Data Science", "provider": "Coursera (UC Davis)", "url": "https://www.coursera.org/learn/sql-for-data-science", "difficulty": "Beginner", "free": True},
        {"name": "The Complete SQL Bootcamp", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "difficulty": "Beginner"},
    ],
    "postgresql": [
        {"name": "The Complete SQL Bootcamp (PostgreSQL)", "provider": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "difficulty": "Beginner"},
    ],
    "mysql": [
        {"name": "MySQL for Data Analytics", "provider": "Udemy", "url": "https://www.udemy.com/course/mysql-for-data-analytics/", "difficulty": "Beginner"},
    ],
    "mongodb": [
        {"name": "MongoDB University - Free Courses", "provider": "MongoDB", "url": "https://learn.mongodb.com/", "difficulty": "Beginner", "free": True},
    ],
    "redis": [
        {"name": "Redis University", "provider": "Redis", "url": "https://university.redis.com/", "difficulty": "Intermediate", "free": True},
    ],

    # DevOps & Cloud
    "docker": [
        {"name": "Docker Mastery: with Kubernetes + Swarm", "provider": "Udemy", "url": "https://www.udemy.com/course/docker-mastery/", "difficulty": "Intermediate"},
        {"name": "Docker Tutorial for Beginners", "provider": "YouTube (TechWorld with Nana)", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "difficulty": "Beginner", "free": True},
    ],
    "kubernetes": [
        {"name": "Kubernetes for the Absolute Beginners", "provider": "Udemy (KodeKloud)", "url": "https://www.udemy.com/course/learn-kubernetes/", "difficulty": "Intermediate"},
    ],
    "aws": [
        {"name": "AWS Cloud Practitioner Essentials", "provider": "AWS Skill Builder", "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials", "difficulty": "Beginner", "free": True},
        {"name": "Ultimate AWS Certified Solutions Architect", "provider": "Udemy", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/", "difficulty": "Intermediate"},
    ],
    "azure": [
        {"name": "AZ-900 Microsoft Azure Fundamentals", "provider": "Microsoft Learn", "url": "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/", "difficulty": "Beginner", "free": True},
    ],
    "gcp": [
        {"name": "Google Cloud Fundamentals", "provider": "Coursera (Google)", "url": "https://www.coursera.org/learn/gcp-fundamentals", "difficulty": "Beginner", "free": True},
    ],
    "ci/cd": [
        {"name": "GitHub Actions - The Complete Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/github-actions-the-complete-guide/", "difficulty": "Intermediate"},
    ],
    "git": [
        {"name": "Git & GitHub for Beginners - Crash Course", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "difficulty": "Beginner", "free": True},
    ],
    "linux": [
        {"name": "Introduction to Linux", "provider": "edX (Linux Foundation)", "url": "https://www.edx.org/learn/linux/the-linux-foundation-introduction-to-linux", "difficulty": "Beginner", "free": True},
    ],

    # Data Science & ML
    "machine learning": [
        {"name": "Machine Learning Specialization", "provider": "Coursera (Andrew Ng)", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "difficulty": "Intermediate", "free": True},
        {"name": "Practical Deep Learning for Coders", "provider": "fast.ai", "url": "https://course.fast.ai/", "difficulty": "Intermediate", "free": True},
    ],
    "deep learning": [
        {"name": "Deep Learning Specialization", "provider": "Coursera (Andrew Ng)", "url": "https://www.coursera.org/specializations/deep-learning", "difficulty": "Advanced", "free": True},
    ],
    "data science": [
        {"name": "IBM Data Science Professional Certificate", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/ibm-data-science", "difficulty": "Beginner", "free": True},
    ],
    "data analysis": [
        {"name": "Google Data Analytics Professional Certificate", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-data-analytics", "difficulty": "Beginner", "free": True},
    ],
    "nlp": [
        {"name": "NLP Specialization", "provider": "Coursera (DeepLearning.AI)", "url": "https://www.coursera.org/specializations/natural-language-processing", "difficulty": "Advanced", "free": True},
    ],
    "computer vision": [
        {"name": "First Principles of Computer Vision", "provider": "Coursera (Columbia)", "url": "https://www.coursera.org/specializations/firstprinciplesofcomputervision", "difficulty": "Advanced", "free": True},
    ],
    "tensorflow": [
        {"name": "TensorFlow Developer Certificate", "provider": "Coursera (DeepLearning.AI)", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "difficulty": "Intermediate", "free": True},
    ],
    "pytorch": [
        {"name": "PyTorch for Deep Learning", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=V_xro1bcAuI", "difficulty": "Intermediate", "free": True},
    ],
    "pandas": [
        {"name": "Data Analysis with Python", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "difficulty": "Beginner", "free": True},
    ],
    "numpy": [
        {"name": "Data Analysis with Python", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "difficulty": "Beginner", "free": True},
    ],
    "scikit-learn": [
        {"name": "Machine Learning with scikit-learn", "provider": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "difficulty": "Intermediate", "free": True},
    ],
    "power bi": [
        {"name": "Microsoft Power BI Data Analyst", "provider": "Coursera (Microsoft)", "url": "https://www.coursera.org/professional-certificates/microsoft-power-bi-data-analyst", "difficulty": "Beginner", "free": True},
    ],
    "tableau": [
        {"name": "Tableau Training (Free)", "provider": "Tableau", "url": "https://www.tableau.com/learn/training/20201", "difficulty": "Beginner", "free": True},
    ],

    # Mobile
    "flutter": [
        {"name": "Flutter & Dart - The Complete Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/learn-flutter-dart-to-build-ios-android-apps/", "difficulty": "Beginner"},
    ],
    "react native": [
        {"name": "React Native - The Practical Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/react-native-the-practical-guide/", "difficulty": "Intermediate"},
    ],

    # Tools & Other
    "figma": [
        {"name": "Figma UI/UX Design Essentials", "provider": "Udemy", "url": "https://www.udemy.com/course/figma-ux-ui-design-user-experience-tutorial-course/", "difficulty": "Beginner"},
    ],
    "ui/ux": [
        {"name": "Google UX Design Professional Certificate", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-ux-design", "difficulty": "Beginner", "free": True},
    ],
    "agile": [
        {"name": "Agile with Atlassian Jira", "provider": "Coursera (Atlassian)", "url": "https://www.coursera.org/learn/agile-atlassian-jira", "difficulty": "Beginner", "free": True},
    ],
    "scrum": [
        {"name": "Agile with Atlassian Jira", "provider": "Coursera (Atlassian)", "url": "https://www.coursera.org/learn/agile-atlassian-jira", "difficulty": "Beginner", "free": True},
    ],
    "project management": [
        {"name": "Google Project Management Certificate", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-project-management", "difficulty": "Beginner", "free": True},
    ],
    "communication": [
        {"name": "Improving Communication Skills", "provider": "Coursera (UPenn)", "url": "https://www.coursera.org/learn/wharton-communication-skills", "difficulty": "Beginner", "free": True},
    ],
    "leadership": [
        {"name": "Inspired Leadership Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/inspired-leadership", "difficulty": "Beginner", "free": True},
    ],
    "graphql": [
        {"name": "GraphQL Full Course", "provider": "YouTube (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=ed8SzALpx1Q", "difficulty": "Intermediate", "free": True},
    ],
    "rest api": [
        {"name": "REST APIs with Flask and Python", "provider": "Udemy", "url": "https://www.udemy.com/course/rest-api-flask-and-python/", "difficulty": "Intermediate"},
    ],
    "microservices": [
        {"name": "Microservices with Node JS and React", "provider": "Udemy", "url": "https://www.udemy.com/course/microservices-with-node-js-and-react/", "difficulty": "Advanced"},
    ],
    "firebase": [
        {"name": "Firebase - Ultimate Beginner's Guide", "provider": "YouTube (Fireship)", "url": "https://www.youtube.com/watch?v=9kRgVxULbag", "difficulty": "Beginner", "free": True},
    ],
    "supabase": [
        {"name": "Supabase Crash Course", "provider": "YouTube (Traversy Media)", "url": "https://www.youtube.com/watch?v=7uKQBl9uZ00", "difficulty": "Beginner", "free": True},
    ],
}

# Search URL templates for skills not in the database
PLATFORM_SEARCH = [
    {"provider": "Coursera", "url": "https://www.coursera.org/search?query={q}", "icon": "🎓"},
    {"provider": "Udemy", "url": "https://www.udemy.com/courses/search/?q={q}", "icon": "📚"},
    {"provider": "YouTube", "url": "https://www.youtube.com/results?search_query={q}+full+course", "icon": "▶️"},
]


def recommend_courses(candidate_id: str) -> list:
    """Recommend courses based on skill gaps — uses AI when available, real links as fallback."""
    gaps = analyze_skill_gaps(candidate_id)
    missing = gaps.get("missing_skills", [])
    target_role = gaps.get("target_role", "software developer")
    strong = gaps.get("strong_skills", [])

    if not missing:
        return [{"message": "No skill gaps detected! You're well-prepared for your target role."}]

    # Try AI first
    prompt = f"""You are a career advisor. A candidate wants to become a "{target_role}".

They already know: {', '.join(strong) if strong else 'No skills listed'}
They are MISSING these skills: {', '.join(missing)}

For each missing skill, recommend 1-2 specific real courses or resources.

Return a JSON array like:
[
    {{
        "skill": "skill name",
        "courses": [
            {{
                "name": "exact course name",
                "provider": "Coursera/Udemy/YouTube/freeCodeCamp/etc",
                "url": "real URL to the course",
                "difficulty": "beginner/intermediate/advanced",
                "reason": "why this course is good for this skill"
            }}
        ]
    }}
]

Recommend REAL courses that actually exist. Prioritize free resources when available."""

    result = ask_gemini_json(prompt)

    if result and isinstance(result, list) and len(result) > 0:
        return result

    # ─── Fallback with real course links ───
    recommendations = []
    for skill in missing:
        skill_lower = skill.lower().strip()
        skill_display = skill.title() if len(skill) > 3 else skill.upper()

        if skill_lower in COURSE_DB:
            courses = []
            for c in COURSE_DB[skill_lower]:
                courses.append({
                    "name": c["name"],
                    "provider": c["provider"],
                    "url": c["url"],
                    "difficulty": c.get("difficulty", "Beginner"),
                    "reason": f"{'Free course — ' if c.get('free') else ''}Highly rated for learning {skill_display}",
                })
            recommendations.append({"skill": skill_display, "courses": courses})
        else:
            # Generate search links for platforms
            q = quote_plus(f"{skill} course")
            courses = [
                {
                    "name": f"Search: {skill_display} courses",
                    "provider": p["provider"],
                    "url": p["url"].format(q=q),
                    "difficulty": "Various",
                    "reason": f"Browse {p['provider']} for {skill_display} courses",
                }
                for p in PLATFORM_SEARCH
            ]
            recommendations.append({"skill": skill_display, "courses": courses})

    return recommendations
