export type Severity = "critical" | "warning" | "info";

export type Category = "hard_skill" | "soft_skill" | "credential" | "tool";

export interface ScoreComponent {
  name: string;
  weight: number;
  score: number;
  details: string[];
}

export interface ScoreBreakdown {
  overall: number;
  components: ScoreComponent[];
  methodology: string;
}

export interface KeywordHit {
  keyword: string;
  in_resume: boolean;
  context: string;
  category: Category;
  importance: "HIGH" | "MEDIUM" | "LOW";
  jd_frequency: number;
  why_it_matters: string;
  suggestion: string;
}

export interface FormatIssue {
  type: string;
  severity: Severity;
  title: string;
  description: string;
  ats_impact: string;
  fix: string;
}

export interface ResumeSection {
  name: string;
  present: boolean;
  words: number;
}

export interface AnalyzeResponse {
  score: ScoreBreakdown;
  missing_keywords: KeywordHit[];
  present_keywords: string[];
  format_issues: FormatIssue[];
  sections: ResumeSection[];
  resume_word_count: number;
  jd_word_count: number;
  format_summary: string;
  headline: string;
  scanned_at: string;
  resume_text: string;
  resume_bullets: string[];
}

export interface RewrittenBullet {
  original: string;
  rewritten: string;
  changed: string[];
  preserved: string[];
  reason: string;
}

export interface RewriteRequest {
  bullets: string[];
  jd: string;
  role: string;
  context: string;
}

export interface RewriteResponse {
  rewritten: RewrittenBullet[];
  rules_applied: string[];
  model_used: string;
}

export interface CoverLetterResponse {
  cover_letter: string;
  model_used: string;
  warning: string;
}
