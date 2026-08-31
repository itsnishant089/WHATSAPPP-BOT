-- HSBTE LEET WhatsApp AI backend — Supabase PostgreSQL schema
-- Run in the Supabase SQL editor. Do not store secrets in this file.

create extension if not exists pgcrypto;

create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    whatsapp_id text unique not null,
    phone_number text,
    profile_name text,
    first_seen_at timestamptz,
    last_seen_at timestamptz,
    is_active boolean default true,
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists messages (
    id uuid primary key default gen_random_uuid(),
    whatsapp_message_id text unique not null,
    whatsapp_user_id text not null,
    direction text not null check (direction in ('incoming', 'outgoing')),
    message_type text,
    message_text text,
    ai_response text,
    status text not null default 'received'
        check (status in ('received', 'processing', 'processed', 'failed')),
    timestamp timestamptz,
    created_at timestamptz default now(),
    metadata jsonb default '{}'::jsonb
);

create table if not exists conversation_memory (
    id uuid primary key default gen_random_uuid(),
    whatsapp_user_id text not null,
    role text not null check (role in ('user', 'assistant', 'system')),
    content text not null,
    message_id uuid,
    created_at timestamptz default now()
);

create table if not exists conversation_summaries (
    id uuid primary key default gen_random_uuid(),
    whatsapp_user_id text not null,
    summary text not null,
    created_at timestamptz default now()
);

create table if not exists users_preferences (
    id uuid primary key default gen_random_uuid(),
    whatsapp_user_id text unique not null,
    language text,
    branch text,
    target_exam text,
    state text,
    college text,
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists webhook_events (
    id uuid primary key default gen_random_uuid(),
    event_id text unique,
    payload_hash text,
    event_type text,
    processed boolean default false,
    created_at timestamptz default now()
);

create table if not exists ai_logs (
    id uuid primary key default gen_random_uuid(),
    whatsapp_user_id text,
    model text,
    input_tokens integer,
    output_tokens integer,
    latency_ms integer,
    status text,
    error_code text,
    created_at timestamptz default now()
);

-- Optional: enable later for RAG without rewriting the app
-- create extension if not exists vector;
-- create table if not exists knowledge_embeddings (
--     id uuid primary key default gen_random_uuid(),
--     source_file text,
--     content text not null,
--     metadata jsonb default '{}'::jsonb,
--     embedding vector(768)
-- );

create index if not exists idx_users_whatsapp_id on users (whatsapp_id);
create index if not exists idx_messages_whatsapp_message_id on messages (whatsapp_message_id);
create index if not exists idx_messages_whatsapp_user_id on messages (whatsapp_user_id);
create index if not exists idx_messages_created_at on messages (created_at);
create index if not exists idx_memory_user on conversation_memory (whatsapp_user_id);
create index if not exists idx_memory_created on conversation_memory (created_at);
create index if not exists idx_summaries_user on conversation_summaries (whatsapp_user_id);
create index if not exists idx_webhook_event_id on webhook_events (event_id);
create index if not exists idx_ai_logs_user on ai_logs (whatsapp_user_id);

-- Example retention (optional). Keep recent context; adjust MESSAGE_RETENTION_DAYS in app config.
-- delete from conversation_memory
-- where created_at < now() - interval '180 days';
