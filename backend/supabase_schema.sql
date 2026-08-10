-- Supabase schema for anonymized usage analytics.
-- Run this in the Supabase SQL editor. The table stores ONLY aggregate numbers.

create table if not exists analytics (
    id bigserial primary key,
    event text not null default 'scan_completed',
    ts double precision not null,
    client_id text not null,
    overall_score double precision,
    keyword_score double precision,
    format_score double precision,
    section_score double precision,
    content_score double precision,
    missing_keyword_count integer,
    format_issue_count integer,
    resume_words integer,
    jd_words integer
);

create index if not exists idx_analytics_ts on analytics (ts);

-- Optional row-level security: disable public access; the backend uses the
-- service-role key.
alter table analytics enable row level security;
