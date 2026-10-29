\restrict dbmate

-- Dumped from database version 18.6 (fd34222)
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: companies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.companies (
    id bigint NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    ats text NOT NULL,
    ats_token text NOT NULL,
    hq_country character(2),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT companies_ats_check CHECK ((ats = ANY (ARRAY['greenhouse'::text, 'lever'::text, 'ashby'::text])))
);


--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.companies ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.companies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: fetch_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fetch_runs (
    id bigint NOT NULL,
    company_id bigint NOT NULL,
    started_at timestamp with time zone NOT NULL,
    finished_at timestamp with time zone,
    status text,
    jobs_seen integer,
    error text,
    CONSTRAINT fetch_runs_status_check CHECK ((status = ANY (ARRAY['ok'::text, 'failed'::text])))
);


--
-- Name: fetch_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.fetch_runs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.fetch_runs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: job_locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.job_locations (
    id bigint NOT NULL,
    job_id bigint NOT NULL,
    country character(2),
    region text,
    city text,
    is_primary boolean DEFAULT false NOT NULL
);


--
-- Name: job_locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.job_locations ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.job_locations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    id bigint NOT NULL,
    company_id bigint NOT NULL,
    source text NOT NULL,
    source_id text NOT NULL,
    title text NOT NULL,
    url text,
    description_text text,
    location_raw text,
    workplace_type text DEFAULT 'unknown'::text NOT NULL,
    salary_min numeric,
    salary_max numeric,
    salary_currency character(3),
    salary_period text,
    salary_source text DEFAULT 'none'::text NOT NULL,
    posted_at timestamp with time zone,
    first_seen_at timestamp with time zone NOT NULL,
    last_seen_at timestamp with time zone NOT NULL,
    closed_at timestamp with time zone,
    CONSTRAINT jobs_check CHECK ((salary_min <= salary_max)),
    CONSTRAINT jobs_check1 CHECK (((salary_source <> 'none'::text) OR ((salary_min IS NULL) AND (salary_max IS NULL)))),
    CONSTRAINT jobs_salary_min_check CHECK ((salary_min >= (0)::numeric)),
    CONSTRAINT jobs_salary_period_check CHECK ((salary_period = ANY (ARRAY['year'::text, 'hour'::text]))),
    CONSTRAINT jobs_salary_source_check CHECK ((salary_source = ANY (ARRAY['structured'::text, 'text'::text, 'none'::text]))),
    CONSTRAINT jobs_workplace_type_check CHECK ((workplace_type = ANY (ARRAY['onsite'::text, 'hybrid'::text, 'remote'::text, 'unknown'::text])))
);


--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.jobs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.jobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: raw_postings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.raw_postings (
    source text NOT NULL,
    source_id text NOT NULL,
    company_id bigint NOT NULL,
    payload jsonb NOT NULL,
    payload_hash text NOT NULL,
    changed_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


--
-- Name: companies companies_ats_ats_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_ats_ats_token_key UNIQUE (ats, ats_token);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: companies companies_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_slug_key UNIQUE (slug);


--
-- Name: fetch_runs fetch_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fetch_runs
    ADD CONSTRAINT fetch_runs_pkey PRIMARY KEY (id);


--
-- Name: job_locations job_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_locations
    ADD CONSTRAINT job_locations_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_source_source_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_source_source_id_key UNIQUE (source, source_id);


--
-- Name: raw_postings raw_postings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raw_postings
    ADD CONSTRAINT raw_postings_pkey PRIMARY KEY (source, source_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: fetch_runs_company_started_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fetch_runs_company_started_idx ON public.fetch_runs USING btree (company_id, started_at DESC);


--
-- Name: job_locations_country_region_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX job_locations_country_region_idx ON public.job_locations USING btree (country, region);


--
-- Name: job_locations_job_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX job_locations_job_id_idx ON public.job_locations USING btree (job_id);


--
-- Name: job_locations_one_primary_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX job_locations_one_primary_idx ON public.job_locations USING btree (job_id) WHERE is_primary;


--
-- Name: jobs_company_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX jobs_company_id_idx ON public.jobs USING btree (company_id);


--
-- Name: jobs_open_last_seen_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX jobs_open_last_seen_idx ON public.jobs USING btree (last_seen_at) WHERE (closed_at IS NULL);


--
-- Name: fetch_runs fetch_runs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fetch_runs
    ADD CONSTRAINT fetch_runs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: job_locations job_locations_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.job_locations
    ADD CONSTRAINT job_locations_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: jobs jobs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: raw_postings raw_postings_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raw_postings
    ADD CONSTRAINT raw_postings_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- PostgreSQL database dump complete
--

\unrestrict dbmate


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20261029013941'),
    ('20261029040819');
