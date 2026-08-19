-- ============================================================
-- Lock down the Supabase REST API
-- Run in: Supabase Dashboard -> SQL Editor -> New query -> Run
-- ============================================================
--
-- WHY THIS IS SAFE FOR YOUR APP
--
-- Supabase exposes every table in the `public` schema over a REST API
-- (PostgREST). Requests through that API run as the `anon` or
-- `authenticated` role. With Row-Level Security disabled, those roles can
-- read and write everything.
--
-- Your Flask app does NOT use that API. It connects straight to Postgres
-- as the `postgres` role, which owns these tables. In Postgres, a table
-- owner bypasses RLS unless FORCE ROW LEVEL SECURITY is set — and we are
-- deliberately NOT setting it. So:
--
--     REST API (anon)  -> blocked
--     Flask app        -> unaffected
--
-- Enabling RLS with no policies denies everything to non-owner roles,
-- which is exactly what we want here.
-- ============================================================


-- STEP 1: enable RLS on every table in the public schema
do $$
declare
  r record;
begin
  for r in
    select tablename
    from pg_tables
    where schemaname = 'public'
  loop
    execute format('alter table public.%I enable row level security', r.tablename);
    raise notice 'RLS enabled on %', r.tablename;
  end loop;
end $$;


-- STEP 2: verify — every row should show rls_enabled = true
select
  tablename,
  rowsecurity as rls_enabled
from pg_tables
where schemaname = 'public'
order by rowsecurity, tablename;


-- STEP 3: confirm no policies exist (none is correct — it means deny-all
-- for the API roles, while the owner still has full access)
select tablename, policyname
from pg_policies
where schemaname = 'public';


-- ============================================================
-- AFTER RUNNING: test the portal
--
--   1. Open https://portal.bharathashetra.org
--   2. Sign in as admin
--   3. Check the student list and payment roster still load
--
-- If anything breaks, roll back with:
--
--   do $$
--   declare r record;
--   begin
--     for r in select tablename from pg_tables where schemaname = 'public'
--     loop
--       execute format('alter table public.%I disable row level security', r.tablename);
--     end loop;
--   end $$;
--
-- ...then tell Claude what broke.
-- ============================================================
