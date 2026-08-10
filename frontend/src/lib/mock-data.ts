import type { AnalyzeResponse } from "./types";

export const MOCK_OPTIMIZED = `Built and maintained REST APIs and microservices with Python, PostgreSQL, AWS and Docker
Accelerated query performance through indexing and caching, reducing p95 latency by 40%
Led a team of 4 engineers shipping a payments service used by 20k customers
Cut deploy time by 30% by introducing automated testing and CI/CD pipelines`;

export const MOCK_RESULT: AnalyzeResponse = {
  score: {
    overall: 61,
    components: [
      {
        name: "keyword_match",
        weight: 0.4,
        score: 40,
        details: [
          "8 of 20 JD keywords found in the resume.",
          "Matched includes exact terms plus close semantic equivalents.",
        ],
      },
      {
        name: "format_compat",
        weight: 0.3,
        score: 87,
        details: ["2 potential ATS parsing issue(s) identified."],
      },
      {
        name: "section_coverage",
        weight: 0.15,
        score: 75,
        details: ["3/4 core sections detected (summary, experience, education, skills)."],
      },
      {
        name: "content_quality",
        weight: 0.15,
        score: 73,
        details: ["6 sentences contain metrics or quantified outcomes."],
      },
    ],
    methodology:
      "Weighted average: keyword match (40%) + format compatibility (30%) + section coverage (15%) + content quality (15%).",
  },
  missing_keywords: [
    {
      keyword: "REST APIs",
      in_resume: false,
      context:
        "Design and build scalable REST APIs and microservices in Python and Node.js.",
      category: "hard_skill",
      importance: "HIGH",
      jd_frequency: 3,
      why_it_matters:
        "This exact term appears 3 times in the JD, including in the very first responsibility. ATS systems rank candidates higher when the hiring manager's own wording shows up in your resume.",
      suggestion:
        "In your Experience section, rephrase one of your backend bullets to start with 'Built and maintained REST APIs...' — only if that is genuinely what you did.",
    },
    {
      keyword: "Kubernetes",
      in_resume: false,
      context: "Deploy on AWS with Docker and Kubernetes.",
      category: "tool",
      importance: "HIGH",
      jd_frequency: 2,
      why_it_matters:
        "Kubernetes is a hard requirement in the deployment section. If your team uses it, list it under Skills and mention a deployment you have done.",
      suggestion:
        "Add 'Docker, Kubernetes' to your Skills line and one deployment bullet, e.g. 'Managed CI/CD deploys to EKS with Docker and Kubernetes.'",
    },
    {
      keyword: "CI/CD",
      in_resume: false,
      context: "Implement CI/CD pipelines and unit testing.",
      category: "tool",
      importance: "MEDIUM",
      jd_frequency: 2,
      why_it_matters:
        "The JD asks for CI/CD pipelines. It's a common ATS-filtered term for platform roles.",
      suggestion:
        "If you have set up or used pipelines, add 'CI/CD' (e.g. 'Set up GitHub Actions CI/CD for tests and deploys').",
    },
    {
      keyword: "Redis",
      in_resume: false,
      context: "Work with PostgreSQL and Redis.",
      category: "tool",
      importance: "MEDIUM",
      jd_frequency: 1,
      why_it_matters:
        "Redis is named in the data layer requirement. Listing it under Skills is low-effort and directly addresses the JD.",
      suggestion:
        "Add Redis to your Skills section next to the other technologies you actually use.",
    },
    {
      keyword: "Node.js",
      in_resume: false,
      context: "Design and build scalable REST APIs and microservices in Python and Node.js.",
      category: "hard_skill",
      importance: "LOW",
      jd_frequency: 1,
      why_it_matters:
        "Node.js is one of the two languages named. Mention it only if you have real experience with it.",
      suggestion:
        "If you have used Node.js, note it in a project bullet. If not, skip it — honesty beats padding.",
    },
  ],
  present_keywords: [
    "Python",
    "PostgreSQL",
    "AWS",
    "Docker",
    "microservices",
    "unit testing",
    "Bachelor's degree",
    "Software Engineer",
  ],
  format_issues: [
    {
      type: "table",
      severity: "critical",
      title: "Skills listed in a table",
      description:
        "Your Skills section is laid out as a two-column table, which many ATS parsers read as one merged cell.",
      ats_impact: "Keywords inside tables can be mis-ordered or merged, so they fail to match the JD.",
      fix: "Convert the table to a single-column list (Skills: Python, SQL, Docker, ...) separated by commas or bullet points.",
    },
    {
      type: "font",
      severity: "warning",
      title: "Unusual font detected",
      description:
        "The resume uses a decorative font that may not be recognized by older parsers.",
      ats_impact: "Glyphs can fall back to a default font and shift layout, dropping text.",
      fix: "Switch to a standard font such as Calibri, Arial, or Helvetica, size 10-12.",
    },
  ],
  sections: [
    { name: "summary", present: true, words: 54 },
    { name: "experience", present: true, words: 320 },
    { name: "education", present: true, words: 40 },
    { name: "skills", present: true, words: 60 },
  ],
  resume_word_count: 474,
  jd_word_count: 186,
  format_summary: "Good foundation with room to improve.",
  headline: "Score 61/100. The biggest levers are below — usually keyword match and formatting.",
  scanned_at: new Date().toISOString(),
  resume_text:
    "John Smith - Senior Software Engineer\nSummary: Backend engineer with 6 years building APIs and data pipelines.\nExperience:\n- Built APIs with Python, PostgreSQL, AWS and Docker\n- Improved query performance with indexing and caching\n- Led a team of 4 engineers shipping a payments service\n- Reduced deploy time by 30% with automated testing\nSkills: Python, SQL, AWS, Docker, PostgreSQL, Git\nEducation: B.Sc. Computer Science",
  resume_bullets: [
    "Built APIs with Python, PostgreSQL, AWS and Docker",
    "Improved query performance with indexing and caching",
    "Led a team of 4 engineers shipping a payments service",
    "Reduced deploy time by 30% with automated testing",
  ],
};
