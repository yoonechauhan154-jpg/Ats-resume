"""A lightweight, curated lexicon of common resume skills.

Used as a fallback / enhancement to spaCy-based extraction. Kept in the open
so the scoring logic is transparent and explainable.
"""

from __future__ import annotations

# Programing languages, frameworks, tools. Order matters (longer first) so
# phrases like "machine learning" match before "learning".
HARD_SKILLS: list[str] = [
    # languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c sharp", "go",
    "golang", "rust", "ruby", "php", "swift", "kotlin", "scala", "sql", "pl/sql",
    "bash", "powershell", "shell", "dart", "r language", "matlab", "perl",
    "html", "css", "sass", "less", "graphql", "delphi", "cobol", "fortran",
    # frameworks / libraries
    "react", "react.js", "react native", "next.js", "vue", "vue.js", "angular",
    "svelte", "node.js", "express.js", "django", "flask", "fastapi", "spring",
    "spring boot", "rails", "laravel", "asp.net", ".net", "electron", "flutter",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "spark", "hadoop", "airflow", "kafka", "rabbitmq", "celery",
    "jquery", "bootstrap", "tailwind", "redux", "mobx", "graphql", "rest",
    "rest api", "graphql api", "microservices", "gatsby", "hugo", "opencv",
    # databases / storage
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "mssql", "sqlite", "mariadb",
    "neo4j", "firebase", "supabase", "bigquery", "redshift", "snowflake",
    "clickhouse", "influxdb", "cockroachdb", "cosmos db", "databricks",
    # cloud / devops / infra
    "aws", "amazon web services", "azure", "gcp", "google cloud", "cloud",
    "kubernetes", "k8s", "docker", "terraform", "ansible", "puppet", "chef",
    "jenkins", "github actions", "gitlab ci", "circleci", "travis", "argo",
    "helm", "istio", "prometheus", "grafana", "datadog", "new relic",
    "nginx", "haproxy", "caddy", "aws lambda", "serverless", "fargate",
    "ec2", "s3", "rds", "cloudfront", "route53", "iam", "vpc", "eks", "ecs",
    "azure devops", "azure functions", "azure pipelines", "cloud run",
    "cloud functions", "compute engine", "kubernetes engine", "gke", "vertex ai",
    # data / ml / ai
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "data science", "data analysis", "data engineering",
    "data pipeline", "etl", "data warehouse", "data lake", "feature engineering",
    "statistical analysis", "regression", "classification", "clustering",
    "recommendation systems", "recommender systems", "llm", "large language model",
    "prompt engineering", "rag", "retrieval-augmented generation", "fine-tuning",
    "fine tuning", "transformer", "bert", "gpt", "sentence-transformers",
    "embedding", "vector database", "pinecone", "weaviate", "qdrant", "milvus",
    "mlops", "model deployment", "a/b testing", "ab testing", "experimentation",
    "time series", "forecasting", "predictive modeling", "data visualization",
    "tableau", "power bi", "looker", "metabase", "jupyter", "notebook",
    "excel", "google sheets", "airtable",
    # testing
    "unit testing", "integration testing", "e2e", "end-to-end testing",
    "jest", "pytest", "junit", "mocha", "cypress", "playwright", "selenium",
    "testing library", "test-driven development", "tdd", "behavior-driven",
    "bdp", "qa", "quality assurance", "test automation",
    # tooling
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
    "notion", "figma", "sketch", "adobe xd", "photoshop", "illustrator",
    "postman", "swagger", "openapi", "grpc", "protobuf", "websocket",
    "docker compose", "makefile", "cmake", "gradle", "maven", "npm", "yarn",
    "pnpm", "pip", "poetry", "virtualenv", "vite", "webpack", "babel", "eslint",
    "prettier", "typescript compiler", "storybook", "lerna", "nx",
    # project management / methodologies
    "agile", "scrum", "kanban", "waterfall", "lean", "six sigma", "sdlc",
    "ci/cd", "continuous integration", "continuous deployment", "continuous delivery",
    "devops", "site reliability", "sre", "incident management", "on-call",
    # security
    "security", "cybersecurity", "owasp", "penetration testing", "vulnerability",
    "authentication", "authorization", "oauth", "jwt", "sso", "encryption",
    "zero trust", "siem", "soc", "threat modeling", "compliance", "gdpr",
    "hipaa", "sox", "iso 27001", "pci-dss",
    # networking
    "tcp/ip", "dns", "http", "https", "tls", "ssl", "vpn", "load balancing",
    "cdns", "restful", "api design", "message queues", "event-driven",
    # misc business / domain
    "seo", "sem", "content marketing", "email marketing", "growth marketing",
    "digital marketing", "product management", "business development",
    "sales", "salesforce", "hubspot", "zendesk", "intercom", "crm", "erp",
    "sap", "quickbooks", "xero", "stripe", "paypal", "braintree", "fintech",
    "blockchain", "smart contracts", "solidity", "web3", "defi", "cryptocurrency",
    "supply chain", "logistics", "inventory management", "procurement",
    "financial modeling", "budgeting", "forecasting", "roi analysis",
]

SOFT_SKILLS: list[str] = [
    "communication", "teamwork", "leadership", "problem solving", "problem-solving",
    "critical thinking", "creativity", "time management", "organization",
    "adaptability", "flexibility", "collaboration", "mentoring", "coaching",
    "stakeholder management", "cross-functional", "negotiation", "presentation",
    "public speaking", "written communication", "verbal communication",
    "attention to detail", "detail-oriented", "self-motivated", "self-starter",
    "initiative", "ownership", "accountability", "decision making", "analytical",
    "strategic thinking", "conflict resolution", "emotional intelligence",
    "empathy", "customer service", "client management", "vendor management",
    "project management", "prioritization", "multitasking", "deadline-driven",
    "results-oriented", "goal-oriented", "growth mindset", "continuous improvement",
    "documentation", "reporting", "data-driven", "remote collaboration",
]

DEGREE_KEYWORDS: list[str] = [
    "bachelor", "master", "phd", "mba", "associate", "b.s.", "m.s.", "m.sc.",
    "b.a.", "m.a.", "bsc", "msc", "beng", "meng", "bachelors", "masters",
    "doctorate", "graduate degree", "undergraduate",
]

CERTIFICATIONS: list[str] = [
    "aws certified", "azure certified", "gcp certified", "pmp", "cissp",
    "csm", "psm", "scrum master", "comptia", "ccna", "ceh", "aws solutions architect",
    "kubernetes certification", "cka", "ckad", "togaf", "itil", "cpa", "cfa",
    "google analytics", "google ads", "hubspot certified", "tableau certified",
    "six sigma green belt", "six sigma black belt", "pmp certification",
]

# Categories that explain *why* a keyword matters (rule-based fallback).
CATEGORY_EXPLANATIONS: dict[str, str] = {
    "hard_skill": (
        "Hard skills are the most common screening filters. ATS systems match "
        "exact terms from the job description against your resume, so an absent "
        "term can lower your rank even when you have the underlying ability."
    ),
    "soft_skill": (
        "Soft skills are often used as secondary screening keywords. Including "
        "them (only when truthful) improves alignment with the JD's language."
    ),
    "credential": (
        "Credentials and certifications are frequently hard pass/fail filters "
        "in ATS screening. Missing ones are checked automatically before a "
        "human ever sees the resume."
    ),
    "tool": (
        "Named tools and technologies are parsed as literal keywords. If you "
        "have used this tool, list it explicitly rather than describing it "
        "generically, because ATS matches exact strings, not synonyms."
    ),
}

SKILLS_BY_CATEGORY: dict[str, list[str]] = {
    "hard_skill": HARD_SKILLS,
    "tool": HARD_SKILLS,  # tools overlap with hard skills
    "soft_skill": SOFT_SKILLS,
    "credential": DEGREE_KEYWORDS + CERTIFICATIONS,
}
