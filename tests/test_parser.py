from src.TextExtraction.JobDescriptionExtraction import JobDescriptionParser
import json
from dotenv import load_dotenv


def test_parser_runs_on_sample():
    # Load environment variables
    load_dotenv()

    parser = JobDescriptionParser()
    sample_text = '''
    Principal Data Scientist
Aurora, CO · 1 week ago · 70 people clicked apply

 On-site
Matches your job preferences, workplace type is On-site.
 Full-time
Matches your job preferences, job type is Full-time.

Apply

Save
Save Principal Data Scientist at RefinedScience
How your profile and resume fit this job
Get AI-powered advice on this job and more exclusive features with Premium. Try Premium for $0



Tailor my resume to this job

Am I a good fit for this job?

How can I best position myself for this job?

About the job
This is a remote position. This role may have residence anywhere in the continental United States, but requires a willingness to travel to the RefinedScience location in (Aurora, CO) approximately once per month.

At RefinedScience, our mission is to advance care by bringing together the best science, data and minds – disease by disease, patient by patient, cell by cell to discover pathways to life beyond disease.

What We Are Looking For

We are seeking a highly skilled Principal Data Scientist to join our dynamic team. This role involves tackling complex data challenges, developing predictive models, and extracting valuable insights to inform strategic decisions.

The ideal candidate will have a strong background in data science, with proven experience in machine learning, statistical analysis, and big data technologies. You will lead projects from conception to deployment, mentor junior data scientists, and collaborate with cross-functional teams to drive innovation and improve our data-driven decision-making processes.

KEY ACTIVITIES 

Implement cutting edge statistical and machine learning methods to develop empirical models. Key focus areas include:
Developing statistical learning-based models
Developing inferential/causal models
Developing machine learning based predictive-and-interpretive models
Developing federated/distributed learning models
Implementing advanced artificial intelligence (AI) tools such as large language models to boost efficiency of data extraction and curation
Being able to process, manage, manipulate, and visualize large clinical data adhering to best practices
Generating real world evidence and clinical insights while validating model performances
Understanding complex clinical problems and solving them (empirically and intuitively)
Collaborate with academicians, clinicians, data managers, data engineers, data analysts, bioinformaticians, non-technical partners, business personnel, and other stakeholders.
Contribute to preparing scientific manuscripts
MUST HAVES

B.Sc. with 5+ years of working experience, or MSc / PhD with 1+ year postgraduate experience in data science, mathematics, statistics, biostatistics, computer science or related quantitative discipline.
Superb written and verbal communication skills
Demonstrable evidence of learning and scientific problem-solving skills
Thorough working knowledge of R/Quarto/Python and SQL
Experience in software (e.g., package) development for reproducibility
Experience in at-least one web application (R Shiny/JAVA/Tableau)
Applied knowledge of working in Linux, AWS, GCP, and GitHub
Thorough theoretical and applied understanding on at least three or more areas such as multistate survival analyses, mixed modeling, non-parametric modeling, longitudinal/time series modeling, meta-analysis/evidence synthesis, machine learning models (e.g., gradient boost, ensemble models, SVM, neural net, transformers, and their counterparts), distributed algorithms, federated algorithms, adversarial models, and Bayesian models.
Experience working in a collaborative environment being as a team player
Willingness to travel to RefinedScience location (Denver, CO) approximately once per month and travel up to 15%).

NICE TO HAVES

Proven track record of publication in major scientific journals, conferences or scientific proceedings.
Experience working with electronic health records (EHR) data
Experience in designing clinical trials (single-arm, synthetic, or randomized)
Experience working in early-stage Biotech environment

WHY YOU’LL LOVE REFINED SCIENCE

Team + Values

At RefinedScience, we seamlessly integrate top-tier clinical and biological data with expert knowledge to provide unparalleled insights. We maximize patient impact with these unique insights by optimizing clinical trial probability of success and time to actionable results. We work across biopharma and we are a trusted partner in achieving better results, faster – working together to unlock strategic advantage.

Our Values

Act with Purpose – We believe in rigor through deliberate and thoughtful actions
Be Curious – Curiosity is the spark that ignites innovation and growth
Take Ownership – True ownership leads to pride and commitment in the work we do
Invest in Relationships – Building strong connections is the foundation for effective collaboration and trust for long term success
Embrace Agility – We celebrate agile thinking, resilience, and adaptability

What We Offer

The target salary range is $170,000 to $210,000 annually.
Base pay offered may vary within the posted range based on several factors, including but not limited to education, job-related knowledge, skills, experience, and location.

Benefits

Medical, Dental and Vision insurance 
Life, AD&D, Short-term and Long-term Disability Insurance (none is 100% covered)
HSA Spending Accounts
22 Vacation days
10 Paid Holidays and Sick Time (120 hours per year)
401(K) Plan

At Refined Sciences, we believe diversity drives innovation. In order to commit to health for ALL PEOPLE and create positive impact, we’re building a culture where difference is valued. We take a holistic approach. We’re always growing our network of people, programs and tools all designed to help employees grow and manage their careers.

Benefits found in job post

Vision insurance
Disability insurance
401(k)
Job search faster with Premium
    '''
    result = parser.parse(sample_text)

    # Basic assertions
    assert result.get("job_title"), "job_title should not be empty"
    assert result.get("location"), "location should not be empty"
    assert "skills" in result and isinstance(result["skills"], list), "skills should be a list"
    assert "ats_score" in result and isinstance(result["ats_score"], dict), "ats_score should be a dict"

    # Save results for inspection
    with open("together_extracted.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n✅ Test passed and results saved to together_extracted.json")


if __name__ == "__main__":
    test_parser_runs_on_sample()