# pylint: disable=line-too-long,missing-module-docstring




prompt_data = {
    "ATS_RULES": {
        "ats_optimization_rules": {
            "general": {
                "rules": [
                    "Use standard section headers (e.g., 'Work Experience' not 'Professional Journey')",
                    "Avoid graphics/icons/tables",
                    "Use reverse chronological format",
                    "Include 3-6 relevant keywords from job description",
                    "Use simple fonts (Arial, Calibri, Times New Roman)",
                    "Maintain 1-inch margins",
                    "Save as PDF with 'FirstName_LastName_Resume.pdf' format"
                ]
            },
            "name": {
                "rules": [
                    "Place at top-center in 16-18pt font",
                    "No special characters or emojis",
                    "Match exactly with LinkedIn profile"
                ]
            },
            "contact": {
                "rules": [
                    "Include city/state matching employer's location when possible",
                    "Use clean LinkedIn URL (linkedin.com/in/name)",
                    "Remove hyperlink formatting from email"
                ]
            },
            "work_experience": {
                "rules": [
                    "List company names in bold before positions",
                    "Include 4-6 bullet points per recent role",
                    "Mirror language from job description requirements",
                    "Use industry-standard job titles",
                    "Add 2-3 company description keywords"
                ]
            },
            "education": {
                "rules": [
                    "List degrees without minor unless relevant",
                    "Spell out university names completely",
                    "Place education after experience for 2+ years professional work"
                ]
            },
            "technical_projects": {
                "rules": [
                    "Include technologies from job description",
                    "List client/stakeholder if applicable",
                    "Show progression from ideation to deployment"
                ]
            },
            "skills": {
                "rules": [
                    "List hard skills before soft skills",
                    "Include certification expiration dates if applicable",
                    "Match 75% of job description's required skills"
                ]
            }
        },
        "llm_output_structure": {
            "resume_data": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Formatted resume text following all rules"
                    },
                    "formatting_metadata": {
                        "type": "object",
                        "properties": {
                            "color_coding": {
                                "type": "object",
                                "properties": {
                                    "pink": {"type": "array", "items": {"type": "string"}},
                                    "yellow": {"type": "array", "items": {"type": "string"}},
                                    "blue": {"type": "array", "items": {"type": "string"}},
                                    "green": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "keyword_density": {
                                "type": "object",
                                "properties": {
                                    "primary_keywords": {"type": "array", "items": {"type": "string"}},
                                    "secondary_keywords": {"type": "array", "items": {"type": "string"}},
                                    "match_percentage": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            },
            "humanized_explanation": {
                "type": "string",
                "description": "Natural language summary of optimizations made in conversational tone"
            }
        }
    },

    "LLM_FILLING_GUIDELINES_WITH_STYLE": {
        "general": {
            "tone": "Professional, results-oriented, concise",
            "bullet_point_style": "Each responsibility must begin with a strong action verb and focus on impact or metrics where possible",
            "metrics_usage": "Include specific metrics (e.g., 300+, 25%, $10,000) when available to emphasize achievement",
            "tense": {
                "current_role": "present tense",
                "past_roles": "past tense"
            },
            "formatting_cues": {
                "bold_sections": [
                    "WORK EXPERIENCE",
                    "EDUCATION",
                    "LEADERSHIP EXPERIENCE",
                    "SKILLS & INTERESTS"
                ],
                "highlight_colors_meaning": {
                    "red/pink": "action verbs",
                    "yellow": "tools/technologies/platforms",
                    "blue": "quantified outcomes or metrics",
                    "green": "collaboration and team contributions"
                }
            }
        },
        "name": {
            "type": "string",
            "rules": [
                "Use full legal name",
                "Capitalize all first letters (e.g., Jonathan Javier)"
            ]
        },
        "contact": {
            "location": "City, State",
            "linkedin": "Clickable full LinkedIn URL",
            "phone": "Include country code if international",
            "email": "Professional email, no casual or nickname addresses",
            "website": "Portfolio or personal site (optional)",
            "rules": [
                "Present contact in a single line separated by pipes or minimal punctuation",
                "No unnecessary labels (e.g., 'Email:')"
            ]
        },
        "education": {
            "university": "Official university name",
            "degree": "Full degree title (e.g., BS in Business Administration - Finance)",
            "gpa": "Optional; only include if ≥3.0",
            "graduation_date": "Month YYYY or just YYYY",
            "awards": [
                "Include scholarships, honors, leadership roles, and dean's list mentions"
            ],
            "rules": [
                "Show honors and involvement under bullet points",
                "Group awards inline in a concise format",
                "Education should be listed before experience unless professional experience is more relevant",
                "List all institutions and degrees using only the date of degree completion (e.g., May 2025)",
                "Order entries in reverse chronological order",
                "Format study abroad like home institution and provide context if the school is not well known",
                "Remove high school information after sophomore year; optionally include in ADDITIONAL INFORMATION",
                "Transfer schools are optional unless showcasing specialized coursework",
                "Include GPA if 3.5+ or if employer requires it",
                "Include only relevant, advanced coursework—not introductory classes",
                "Scholarships, competitions, and projects can go in Education or another section",
                "Do not include dates with merit awards unless placing them in ADDITIONAL INFORMATION"
            ]
        },
        "work_experience": {
            "structure_per_entry": {
                "company": "Company name",
                "title": "Role title (e.g., Operations Specialist - Product Ops)",
                "location": "City, State",
                "dates": "Month YYYY – Month YYYY or 'Present'",
                "responsibilities": [
                    "Use 2–5 bullets",
                    "Start with action verbs (highlighted in pink/red)",
                    "Mention tools/platforms (highlighted in yellow)",
                    "Emphasize metrics or outcomes (highlighted in blue)",
                    "Mention team/collaboration efforts (highlighted in green)"
                ]
            },
            "rules": [
                "Customize descriptions to match target job where applicable",
                "Highlight achievements, improvements, or innovations",
                "Avoid generic descriptions like 'Did tasks'"
            ]
        },
        "leadership_experience": {
            "structure_per_entry": {
                "organization": "Full name of club/association",
                "title": "Role title (e.g., Director of Professional Development)",
                "location": "City, State",
                "dates": "Month YYYY – Month YYYY",
                "responsibilities": [
                    "Use 1–3 impactful bullets",
                    "Mention number of members impacted, events organized, or partners involved",
                    "Highlight leadership and coordination",
                    "Describe the outcome of initiatives, programs, or events led or influenced",
                    "Reference any collaboration with faculty, community, or organizations where applicable"
                ]
            },
            "rules": [
                "Quantify leadership achievements if possible",
                "Focus on community, initiative, or organizational outcomes",
                "Use a clear section title that reflects the content, such as Leadership or Volunteer & Service Learning",
                "Place the section between RELEVANT EXPERIENCE and ADDITIONAL INFORMATION if used",
                "Use a consistent and clean format: bold organization/role and align dates to left/right margins",
                "Bullet points should emphasize impact, results, and the value to the organization or group"
            ]
        },
        "technical_projects": {
            "structure_per_project": {
                "project_name": "Clear and descriptive",
                "description": "1–2 sentence overview of the problem solved or goal",
                "technologies_used": [
                    "List of tools/frameworks/languages used",
                    "Group similar tools (e.g., frontend, backend, databases)"
                ],
                "outcomes": "Clear, measurable result or deployment summary"
            },
            "rules": [
                "Project must reflect real contributions",
                "Focus on functionality, tech stack, and success"
            ]
        },
        "skills_and_interests": {
            "skills": [
                "Group by type (Languages, Frameworks, Tools, etc.)",
                "Avoid redundant or outdated skills"
            ],
            "rules": [
                "Skills listed should match the tools mentioned in resume where possible"
            ]
        }
    },

    "LLM_FILLING_GUIDELINES_WITH_STYLE_AND_LIMITS": {
        "general": {
            "max_total_resume_length": 4000,
            "tone": "Professional, concise, result-driven",
            "bullet_point_style": "Start with a strong action verb, include metrics and outcomes",
            "tense": {
                "current_role": "present",
                "past_roles": "past"
            },
            "formatting_colors_meaning": {
                "pink": "action verbs",
                "yellow": "tools/technologies",
                "blue": "metrics/outcomes",
                "green": "team/collaboration"
            }
        },
        "name": {
            "max_length": 50,
            "rules": ["Use full name, properly capitalized"]
        },
        "contact": {
            "location": {"type": "string", "max_length": 30},
            "linkedin": {"type": "url", "max_length": 100},
            "phone": {"type": "string", "max_length": 20},
            "email": {"type": "string", "max_length": 50},
            "website": {"type": "url", "max_length": 100}
        },
        "education": {
            "university": {"type": "string", "max_length": 80},
            "degree": {"type": "string", "max_length": 80},
            "gpa": {"type": "string", "max_length": 10},
            "graduation_date": {"type": "string", "max_length": 20},
            "awards": {
                "type": "array",
                "max_items": 3,
                "max_item_length": 80
            }
        },
        "work_experience": {
            "max_entries": 3,
            "company": {"type": "string", "max_length": 50},
            "title": {"type": "string", "max_length": 60},
            "location": {"type": "string", "max_length": 30},
            "dates": {"type": "string", "max_length": 25},
            "responsibilities": {
                "type": "array",
                "max_items": 4,
                "max_item_length": 160,
                "min_item_length": 80
            }
        },
        "leadership_experience": {
            "max_entries": 2,
            "organization": {"type": "string", "max_length": 60},
            "title": {"type": "string", "max_length": 60},
            "location": {"type": "string", "max_length": 30},
            "dates": {"type": "string", "max_length": 25},
            "responsibilities": {
                "type": "array",
                "max_items": 3,
                "max_item_length": 140
            }
        },
        "technical_projects": {
            "max_entries": 2,
            "project_name": {"type": "string", "max_length": 50},
            "description": {"type": "string", "max_length": 150},
            "technologies_used": {
                "type": "array",
                "max_items": 6,
                "max_item_length": 20
            },
            "outcomes": {"type": "string", "max_length": 150}
        },
        "skills_and_interests": {
            "skills": {
                "type": "array",
                "max_items": 10,
                "max_item_length": 30
            }
        }
    },

    "RESUME": {
        "name": None,
        "contact": {
            "location": None,
            "linkedin": None,
            "phone": None,
            "email": None,
            "website": None
        },
        "education": {
            "university": None,
            "degree": None,
            "gpa": None,
            "graduation_date": None,
            "awards": []
        },
        "work_experience": [
            {
                "company": None,
                "title": None,
                "location": None,
                "dates": None,
                "responsibilities": []
            }
        ],
        "leadership_experience": [
            {
                "organization": None,
                "title": None,
                "location": None,
                "dates": None,
                "responsibilities": []
            }
        ],
        "technical_projects": [
            {
                "project_name": None,
                "description": None,
                "technologies_used": [],
                "outcomes": None
            }
        ],
        "skills_and_interests": {
            "skills": []
        }
    },

    "RESUME_EXAMPLE_OUTPUT": {
        "name": "Jonathan Javier",
        "contact": "Scranton, PA | https://www.linkedin.com/in/jonathanjavier | +1-866-663-2783 | StopRejectingMe@Companies | Wonsulting.com",
        "education": {
            "university": "University of California, Riverside",
            "degree": "BS in Business Administration - Finance",
            "gpa": "3.5",
            "graduation_date": "June 2017",
            "awards": [
                "Honors Program",
                "ALPFA",
                "ASUCR",
                "Dean’s Honors List",
                "Chancellor’s Honors List",
                "Cum Laude"
            ]
        },
        "work_experience": [
            {
                "company": "Snap, Inc. (Snapchat)",
                "title": "Operations Specialist - Product Ops",
                "location": "Santa Monica, CA",
                "dates": "August 2017 – Present",
                "responsibilities": [
                    "Researched user trends to implement Go-To-Market strategies for new updates, improving operations satisfaction by 17%",
                    "Developed training materials and workflows using Cheetah, Zendesk, Confluence, and Jira for macro language processes and infographics",
                    "Created Snapinars for issue resolutions including password resets, increasing platform efficiency",
                    "Solved 300+ customer inquiries weekly through CRM platforms, enhancing customer service operations"
                ]
            },
            {
                "company": "Goodwin’s Organics",
                "title": "Marketing & Strategy Intern",
                "location": "Riverside, CA",
                "dates": "January 2017 – June 2017",
                "responsibilities": [
                    "Generated reports using Excel and PowerPoint to analyze trends and target markets, increasing customer retention by 15% YTD",
                    "Collaborated with senior leadership and used social media strategies to gain 350+ weekly followers",
                    "Strategized a niche market approach, increasing class attendance by 25% weekly"
                ]
            },
            {
                "company": "Kohl’s",
                "title": "Operations Management Intern",
                "location": "Los Angeles, CA",
                "dates": "June 2016 – August 2016",
                "responsibilities": [
                    "Analyzed financial statements and dashboards to identify areas for product efficiency and labor optimization",
                    "Collaborated with finance and customer success teams to increase survey submissions by 10%",
                    "Evaluated 100+ employees to enhance productivity by 23% daily"
                ]
            },
            {
                "company": "Sherwin-Williams",
                "title": "Operations/Finance Intern",
                "location": "Huntington Beach, CA",
                "dates": "May 2015 – August 2015",
                "responsibilities": [
                    "Presented strategic recommendations and collaborated with 3+ interns, ranking #1 in the Western Region",
                    "Reviewed P&L monthly to identify high/low penetration paints, increasing delivery efficiency by 17%",
                    "Maintained customer relationships with 100+ DIY customers, helping to exceed sales goals by 11% MTD"
                ]
            }
        ],
        "leadership_experience": [
            {
                "organization": "Association of Latino Professionals For America (ALPFA)",
                "title": "Director of Professional Development (OC)",
                "location": "Riverside, CA",
                "dates": "April 2017 – Present",
                "responsibilities": [
                    "Partnered with 100+ professionals from companies like Deloitte, KPMG, and Vanguard to host events with 50+ attendees",
                    "Brought 10+ accounting firms to UC Riverside to recruit 250+ students"
                ]
            },
            {
                "organization": "Associated Students of UC Riverside (Student Government)",
                "title": "Elected CHASS Senator",
                "location": "Riverside, CA",
                "dates": "May 2016 – June 2017",
                "responsibilities": [
                    "Managed a $1.6M budget and allocated $10,000+ weekly to student organizations and initiatives",
                    "Organized impactful projects like the Academic TestBank System and ASUCR Career Fair, reaching 22,000+ students"
                ]
            }
        ],
        "skills_and_interests": {
            "skills": {
                "Tools": [
                    "Excel",
                    "PowerPoint",
                    "CRM (Zendesk, Confluence, JIRA)",
                    "G-Suite"
                ],
                "Technical": [
                    "SQL (Class)"
                ]
            }
        }
    }
}

if __name__ == "__main__":
    # Simple check to ensure it runs
    import json
    print(json.dumps(prompt_data, indent=2))
