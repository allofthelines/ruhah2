--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.3 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: _heroku; Type: SCHEMA; Schema: -; Owner: heroku_admin
--

CREATE SCHEMA _heroku;


ALTER SCHEMA _heroku OWNER TO heroku_admin;

--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: create_ext(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.create_ext() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  databaseowner TEXT;

  r RECORD;

BEGIN

  IF tg_tag = 'CREATE EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        CONTINUE WHEN r.command_tag != 'CREATE EXTENSION' OR r.object_type != 'extension';

        schemaname = (
            SELECT n.nspname
            FROM pg_catalog.pg_extension AS e
            INNER JOIN pg_catalog.pg_namespace AS n
            ON e.extnamespace = n.oid
            WHERE e.oid = r.objid
        );

        databaseowner = (
            SELECT pg_catalog.pg_get_userbyid(d.datdba)
            FROM pg_catalog.pg_database d
            WHERE d.datname = current_database()
        );
        --RAISE NOTICE 'Record for event trigger %, objid: %,tag: %, current_user: %, schema: %, database_owenr: %', r.object_identity, r.objid, tg_tag, current_user, schemaname, databaseowner;
        IF r.object_identity = 'address_standardizer_data_us' THEN
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_gaz TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_lex TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_rules TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'amcheck' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.bt_index_check TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.bt_index_parent_check TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'dict_int' THEN
            EXECUTE format('ALTER TEXT SEARCH DICTIONARY %I.intdict OWNER TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'pg_partman' THEN
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.part_config TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.part_config_sub TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.custom_time_partitions TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'pg_stat_statements' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.pg_stat_statements_reset TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'postgis' THEN
            PERFORM _heroku.postgis_after_create();
        ELSIF r.object_identity = 'postgis_raster' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT SELECT ON TABLE %I.raster_columns TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT ON TABLE %I.raster_overviews TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'postgis_topology' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT USAGE ON SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA topology TO %I;', databaseowner);
        ELSIF r.object_identity = 'postgis_tiger_geocoder' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT USAGE ON SCHEMA tiger TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tiger TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tiger TO %I;', databaseowner);

            EXECUTE format('GRANT USAGE ON SCHEMA tiger_data TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tiger_data TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tiger_data TO %I;', databaseowner);
        END IF;
    END LOOP;
  END IF;
END;
$$;


ALTER FUNCTION _heroku.create_ext() OWNER TO heroku_admin;

--
-- Name: drop_ext(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.drop_ext() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  databaseowner TEXT;

  r RECORD;

BEGIN

  IF tg_tag = 'DROP EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_dropped_objects()
    LOOP
      CONTINUE WHEN r.object_type != 'extension';

      databaseowner = (
            SELECT pg_catalog.pg_get_userbyid(d.datdba)
            FROM pg_catalog.pg_database d
            WHERE d.datname = current_database()
      );

      --RAISE NOTICE 'Record for event trigger %, objid: %,tag: %, current_user: %, database_owner: %, schemaname: %', r.object_identity, r.objid, tg_tag, current_user, databaseowner, r.schema_name;

      IF r.object_identity = 'postgis_topology' THEN
          EXECUTE format('DROP SCHEMA IF EXISTS topology');
      END IF;
    END LOOP;

  END IF;
END;
$$;


ALTER FUNCTION _heroku.drop_ext() OWNER TO heroku_admin;

--
-- Name: extension_before_drop(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.extension_before_drop() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  query TEXT;

BEGIN
  query = (SELECT current_query());

  -- RAISE NOTICE 'executing extension_before_drop: tg_event: %, tg_tag: %, current_user: %, session_user: %, query: %', tg_event, tg_tag, current_user, session_user, query;
  IF tg_tag = 'DROP EXTENSION' and not pg_has_role(session_user, 'rds_superuser', 'MEMBER') THEN
    -- DROP EXTENSION [ IF EXISTS ] name [, ...] [ CASCADE | RESTRICT ]
    IF (regexp_match(query, 'DROP\s+EXTENSION\s+(IF\s+EXISTS)?.*(plpgsql)', 'i') IS NOT NULL) THEN
      RAISE EXCEPTION 'The plpgsql extension is required for database management and cannot be dropped.';
    END IF;
  END IF;
END;
$$;


ALTER FUNCTION _heroku.extension_before_drop() OWNER TO heroku_admin;

--
-- Name: postgis_after_create(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.postgis_after_create() RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    schemaname TEXT;
    databaseowner TEXT;
BEGIN
    schemaname = (
        SELECT n.nspname
        FROM pg_catalog.pg_extension AS e
        INNER JOIN pg_catalog.pg_namespace AS n ON e.extnamespace = n.oid
        WHERE e.extname = 'postgis'
    );
    databaseowner = (
        SELECT pg_catalog.pg_get_userbyid(d.datdba)
        FROM pg_catalog.pg_database d
        WHERE d.datname = current_database()
    );

    EXECUTE format('GRANT EXECUTE ON FUNCTION %I.st_tileenvelope TO %I;', schemaname, databaseowner);
    EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.spatial_ref_sys TO %I;', schemaname, databaseowner);
END;
$$;


ALTER FUNCTION _heroku.postgis_after_create() OWNER TO heroku_admin;

--
-- Name: validate_extension(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.validate_extension() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  r RECORD;

BEGIN

  IF tg_tag = 'CREATE EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
      CONTINUE WHEN r.command_tag != 'CREATE EXTENSION' OR r.object_type != 'extension';

      schemaname = (
        SELECT n.nspname
        FROM pg_catalog.pg_extension AS e
        INNER JOIN pg_catalog.pg_namespace AS n
        ON e.extnamespace = n.oid
        WHERE e.oid = r.objid
      );

      IF schemaname = '_heroku' THEN
        RAISE EXCEPTION 'Creating extensions in the _heroku schema is not allowed';
      END IF;
    END LOOP;
  END IF;
END;
$$;


ALTER FUNCTION _heroku.validate_extension() OWNER TO heroku_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts_customer; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_customer (
    id bigint NOT NULL,
    top_size_xyz character varying(10),
    bottom_size_xyz character varying(10),
    size_waist_inches character varying(10),
    shoe_size_eu character varying(10),
    shoe_size_uk character varying(10),
    height integer,
    weight integer,
    birth_year integer,
    user_id bigint NOT NULL
);


ALTER TABLE public.accounts_customer OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_customer ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_customuser; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_customuser (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    is_stylist character varying(10) NOT NULL,
    is_customer character varying(10) NOT NULL,
    is_seller character varying(10) NOT NULL,
    bio character varying(150),
    name character varying(30),
    pfp character varying(100),
    profile_visibility character varying(20) NOT NULL,
    credits integer NOT NULL,
    trending_mode character varying(10) NOT NULL,
    lifeform character varying(10) NOT NULL,
    studio_visibility character varying(15) NOT NULL,
    email_change_requested_at timestamp with time zone,
    is_email_confirmed boolean NOT NULL,
    new_email character varying(254)
);


ALTER TABLE public.accounts_customuser OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_customuser_groups; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_customuser_groups (
    id bigint NOT NULL,
    customuser_id bigint NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.accounts_customuser_groups OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_customuser_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_customuser_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customuser_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_customuser_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_customuser ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customuser_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_customuser_studio_styles; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_customuser_studio_styles (
    id bigint NOT NULL,
    customuser_id bigint NOT NULL,
    style_id bigint NOT NULL
);


ALTER TABLE public.accounts_customuser_studio_styles OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_customuser_studio_styles_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_customuser_studio_styles ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customuser_studio_styles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_customuser_trending_styles; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_customuser_trending_styles (
    id bigint NOT NULL,
    customuser_id bigint NOT NULL,
    style_id bigint NOT NULL
);


ALTER TABLE public.accounts_customuser_trending_styles OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_customuser_trending_styles_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_customuser_trending_styles ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customuser_trending_styles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_customuser_user_permissions; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_customuser_user_permissions (
    id bigint NOT NULL,
    customuser_id bigint NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.accounts_customuser_user_permissions OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_customuser_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_customuser_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_customuser_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_gridpicupload; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_gridpicupload (
    id bigint NOT NULL,
    gridpic_img character varying(100) NOT NULL,
    gridpic_processed_img character varying(100),
    timedate_uploaded timestamp with time zone NOT NULL,
    deleted_by_uploader character varying(10) NOT NULL,
    timedate_deleted_by_uploader timestamp with time zone,
    uploader_id_id bigint NOT NULL
);


ALTER TABLE public.accounts_gridpicupload OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_gridpicupload_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_gridpicupload ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_gridpicupload_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_invitecode; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_invitecode (
    id bigint NOT NULL,
    invite_code character varying(20) NOT NULL,
    is_used boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    invitee_id bigint,
    inviter_id bigint
);


ALTER TABLE public.accounts_invitecode OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_invitecode_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_invitecode ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_invitecode_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_portraitupload; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_portraitupload (
    id bigint NOT NULL,
    portrait_img character varying(100) NOT NULL,
    ticket_id_int integer,
    timedate_created timestamp with time zone NOT NULL,
    status character varying(10) NOT NULL,
    outfit_id_id bigint,
    wearer_id_id bigint NOT NULL
);


ALTER TABLE public.accounts_portraitupload OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_portraitupload_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_portraitupload ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_portraitupload_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_stylist; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_stylist (
    id bigint NOT NULL,
    credits integer NOT NULL,
    user_id bigint NOT NULL
);


ALTER TABLE public.accounts_stylist OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_stylist_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_stylist ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_stylist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_userfollows; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_userfollows (
    id bigint NOT NULL,
    created timestamp with time zone NOT NULL,
    user_from_id bigint NOT NULL,
    user_to_id bigint NOT NULL
);


ALTER TABLE public.accounts_userfollows OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_userfollows_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_userfollows ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_userfollows_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_useritemcart; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_useritemcart (
    id bigint NOT NULL,
    buyer_id bigint,
    item_id bigint,
    styler_id bigint,
    price double precision,
    size character varying(10)
);


ALTER TABLE public.accounts_useritemcart OWNER TO u2m4eitidqus9h;

--
-- Name: accounts_useritemcart_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_useritemcart ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_useritemcart_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_useritemlikes; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.accounts_useritemlikes (
    id bigint NOT NULL,
    item_id bigint,
    styler_id bigint,
    liker_id bigint,
    liked_at timestamp with time zone
);


ALTER TABLE public.accounts_useritemlikes OWNER TO u2m4eitidqus9h;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO u2m4eitidqus9h;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO u2m4eitidqus9h;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO u2m4eitidqus9h;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: box_order; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.box_order (
    id bigint NOT NULL,
    type character varying(5) NOT NULL,
    ticket_id_id bigint,
    money double precision,
    status character varying(10),
    address_customer character varying(100),
    address_fumio character varying(100),
    "timestamp" timestamp with time zone,
    creator_id_id bigint
);


ALTER TABLE public.box_order OWNER TO u2m4eitidqus9h;

--
-- Name: box_order_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.box_order ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.box_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: box_order_items; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.box_order_items (
    id bigint NOT NULL,
    order_id bigint NOT NULL,
    item_id bigint NOT NULL
);


ALTER TABLE public.box_order_items OWNER TO u2m4eitidqus9h;

--
-- Name: box_order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.box_order_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.box_order_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: box_return; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.box_return (
    id bigint NOT NULL,
    order_id_id bigint,
    "timestamp" timestamp with time zone NOT NULL,
    money double precision,
    status character varying(10) NOT NULL,
    address_customer character varying(100),
    address_fumio character varying(100),
    returner_id_id bigint
);


ALTER TABLE public.box_return OWNER TO u2m4eitidqus9h;

--
-- Name: box_return_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.box_return ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.box_return_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: box_ticket; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.box_ticket (
    id bigint NOT NULL,
    style2_id bigint,
    occasion character varying(100),
    condition character varying(100),
    price character varying(100),
    notes text NOT NULL,
    status character varying(10) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    outfit1_id bigint,
    outfit2_id bigint,
    current_outfits integer NOT NULL,
    maximum_outfits integer NOT NULL,
    size_bottom_xyz character varying(3),
    size_shoe_eu character varying(10),
    size_top_xyz character varying(3),
    size_waist_inches character varying(10),
    creator_id_id bigint,
    size_shoe_uk character varying(10),
    style1_id bigint,
    asktype character varying(30) NOT NULL,
    creator_profile_visibility character varying(10),
    catalogue character varying(30) NOT NULL,
    boxcuratedby character varying(30) NOT NULL
);


ALTER TABLE public.box_ticket OWNER TO u2m4eitidqus9h;

--
-- Name: box_ticket_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.box_ticket ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.box_ticket_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: box_ticket_outfits_all; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.box_ticket_outfits_all (
    id bigint NOT NULL,
    ticket_id bigint NOT NULL,
    outfit_id bigint NOT NULL
);


ALTER TABLE public.box_ticket_outfits_all OWNER TO u2m4eitidqus9h;

--
-- Name: box_ticket_outfits_all_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.box_ticket_outfits_all ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.box_ticket_outfits_all_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: box_ticket_stylists_all; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.box_ticket_stylists_all (
    id bigint NOT NULL,
    ticket_id bigint NOT NULL,
    customuser_id bigint NOT NULL
);


ALTER TABLE public.box_ticket_stylists_all OWNER TO u2m4eitidqus9h;

--
-- Name: box_ticket_stylists_all_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.box_ticket_stylists_all ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.box_ticket_stylists_all_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO u2m4eitidqus9h;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO u2m4eitidqus9h;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO u2m4eitidqus9h;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO u2m4eitidqus9h;

--
-- Name: outfit_table; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.outfit_table (
    id bigint NOT NULL,
    rating integer NOT NULL,
    image character varying(100) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    maker_id_id bigint,
    ticket_id_id bigint,
    portrait character varying(100),
    maker_grid_visibility character varying(10)
);


ALTER TABLE public.outfit_table OWNER TO u2m4eitidqus9h;

--
-- Name: outfit_table_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.outfit_table ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.outfit_table_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: outfit_table_items; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.outfit_table_items (
    id bigint NOT NULL,
    outfit_id bigint NOT NULL,
    item_id bigint NOT NULL
);


ALTER TABLE public.outfit_table_items OWNER TO u2m4eitidqus9h;

--
-- Name: outfit_table_items_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.outfit_table_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.outfit_table_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_ecommercestore; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_ecommercestore (
    id bigint NOT NULL,
    name character varying(255),
    api_key character varying(255),
    api_secret character varying(255),
    api_access_token character varying(255),
    shop_url character varying(255),
    size_mapping text,
    address_city character varying(50),
    address_country character varying(50),
    address_postal_code character varying(50),
    address_street_1 character varying(255),
    address_street_2 character varying(255),
    api_store_id character varying(255),
    platform character varying(50)
);


ALTER TABLE public.studio_ecommercestore OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_item (
    id bigint NOT NULL,
    name character varying(255),
    condition character varying(10),
    location character varying(255),
    image character varying(100),
    itemid character varying(30),
    cat character varying(20) NOT NULL,
    tags character varying(255),
    price double precision,
    ecommerce_product_id character varying(255),
    ecommerce_store_id bigint,
    modality character varying(20) NOT NULL
);


ALTER TABLE public.studio_item OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_item ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_item_sizes_shoe_eu; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_item_sizes_shoe_eu (
    id bigint NOT NULL,
    item_id bigint NOT NULL,
    sizeshoeeucategory_id bigint NOT NULL
);


ALTER TABLE public.studio_item_sizes_shoe_eu OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_sizes_shoe_eu_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_item_sizes_shoe_eu ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_item_sizes_shoe_eu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_item_sizes_shoe_uk; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_item_sizes_shoe_uk (
    id bigint NOT NULL,
    item_id bigint NOT NULL,
    sizeshoeukcategory_id bigint NOT NULL
);


ALTER TABLE public.studio_item_sizes_shoe_uk OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_sizes_shoe_uk_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_item_sizes_shoe_uk ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_item_sizes_shoe_uk_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_item_sizes_xyz; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_item_sizes_xyz (
    id bigint NOT NULL,
    item_id bigint NOT NULL,
    sizecategory_id bigint NOT NULL
);


ALTER TABLE public.studio_item_sizes_xyz OWNER TO u2m4eitidqus9h;

--
-- Name: studio_sizecategory; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_sizecategory (
    id bigint NOT NULL,
    name character varying(10) NOT NULL
);


ALTER TABLE public.studio_sizecategory OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_sizes_view; Type: VIEW; Schema: public; Owner: u2m4eitidqus9h
--

CREATE VIEW public.studio_item_sizes_view AS
 SELECT s.id,
    s.item_id,
    i.name AS item_name,
    i.cat AS item_category,
    s.sizecategory_id,
    sc.name AS sizecategory_name
   FROM ((public.studio_item_sizes_xyz s
     JOIN public.studio_item i ON ((s.item_id = i.id)))
     JOIN public.studio_sizecategory sc ON ((s.sizecategory_id = sc.id)))
  ORDER BY s.id;


ALTER VIEW public.studio_item_sizes_view OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_sizes_waist_inches; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_item_sizes_waist_inches (
    id bigint NOT NULL,
    item_id bigint NOT NULL,
    sizewaistinchcategory_id bigint NOT NULL
);


ALTER TABLE public.studio_item_sizes_waist_inches OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_sizes_waist_inches_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_item_sizes_waist_inches ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_item_sizes_waist_inches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_item_sizes_xyz_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_item_sizes_xyz ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_item_sizes_xyz_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_item_taglist; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_item_taglist (
    id bigint NOT NULL,
    item_id bigint NOT NULL,
    tag_id bigint NOT NULL
);


ALTER TABLE public.studio_item_taglist OWNER TO u2m4eitidqus9h;

--
-- Name: studio_item_taglist_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_item_taglist ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_item_taglist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_shopifystore_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_ecommercestore ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_shopifystore_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_sizecategory_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_sizecategory ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_sizecategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_sizeshoeeucategory; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_sizeshoeeucategory (
    id bigint NOT NULL,
    size character varying(10) NOT NULL
);


ALTER TABLE public.studio_sizeshoeeucategory OWNER TO u2m4eitidqus9h;

--
-- Name: studio_sizeshoeeucategory_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_sizeshoeeucategory ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_sizeshoeeucategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_sizeshoeukcategory; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_sizeshoeukcategory (
    id bigint NOT NULL,
    size character varying(10) NOT NULL
);


ALTER TABLE public.studio_sizeshoeukcategory OWNER TO u2m4eitidqus9h;

--
-- Name: studio_sizeshoeukcategory_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_sizeshoeukcategory ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_sizeshoeukcategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_sizewaistinchcategory; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_sizewaistinchcategory (
    id bigint NOT NULL,
    size character varying(10) NOT NULL
);


ALTER TABLE public.studio_sizewaistinchcategory OWNER TO u2m4eitidqus9h;

--
-- Name: studio_sizewaistinchcategory_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_sizewaistinchcategory ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_sizewaistinchcategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_studiooutfittemp; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_studiooutfittemp (
    id bigint NOT NULL,
    item1img character varying(100) NOT NULL,
    item1id character varying(20) NOT NULL,
    item2img character varying(100) NOT NULL,
    item2id character varying(20) NOT NULL,
    item3img character varying(100) NOT NULL,
    item3id character varying(20) NOT NULL,
    item4img character varying(100) NOT NULL,
    item4id character varying(20) NOT NULL,
    ticket_id bigint,
    user_id bigint
);


ALTER TABLE public.studio_studiooutfittemp OWNER TO u2m4eitidqus9h;

--
-- Name: studio_studiooutfittemp_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_studiooutfittemp ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_studiooutfittemp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_style; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_style (
    id bigint NOT NULL,
    style_name character varying(100) NOT NULL
);


ALTER TABLE public.studio_style OWNER TO u2m4eitidqus9h;

--
-- Name: studio_style_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_style ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_style_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: studio_tag; Type: TABLE; Schema: public; Owner: u2m4eitidqus9h
--

CREATE TABLE public.studio_tag (
    id bigint NOT NULL,
    tag_name character varying(100) NOT NULL,
    tag_type character varying(100) NOT NULL
);


ALTER TABLE public.studio_tag OWNER TO u2m4eitidqus9h;

--
-- Name: studio_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.studio_tag ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.studio_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: user_item_likes_id_seq; Type: SEQUENCE; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE public.accounts_useritemlikes ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.user_item_likes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: accounts_customer accounts_customer_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customer
    ADD CONSTRAINT accounts_customer_pkey PRIMARY KEY (id);


--
-- Name: accounts_customer accounts_customer_user_id_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customer
    ADD CONSTRAINT accounts_customer_user_id_key UNIQUE (user_id);


--
-- Name: accounts_customuser_groups accounts_customuser_groups_customuser_id_group_id_c074bdcb_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_groups
    ADD CONSTRAINT accounts_customuser_groups_customuser_id_group_id_c074bdcb_uniq UNIQUE (customuser_id, group_id);


--
-- Name: accounts_customuser_groups accounts_customuser_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_groups
    ADD CONSTRAINT accounts_customuser_groups_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser accounts_customuser_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser
    ADD CONSTRAINT accounts_customuser_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser_studio_styles accounts_customuser_stud_customuser_id_style_id_89258a3b_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_studio_styles
    ADD CONSTRAINT accounts_customuser_stud_customuser_id_style_id_89258a3b_uniq UNIQUE (customuser_id, style_id);


--
-- Name: accounts_customuser_studio_styles accounts_customuser_studio_styles_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_studio_styles
    ADD CONSTRAINT accounts_customuser_studio_styles_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser_trending_styles accounts_customuser_tren_customuser_id_style_id_4023b074_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_trending_styles
    ADD CONSTRAINT accounts_customuser_tren_customuser_id_style_id_4023b074_uniq UNIQUE (customuser_id, style_id);


--
-- Name: accounts_customuser_trending_styles accounts_customuser_trending_styles_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_trending_styles
    ADD CONSTRAINT accounts_customuser_trending_styles_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser_user_permissions accounts_customuser_user_customuser_id_permission_9632a709_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_user_permissions
    ADD CONSTRAINT accounts_customuser_user_customuser_id_permission_9632a709_uniq UNIQUE (customuser_id, permission_id);


--
-- Name: accounts_customuser_user_permissions accounts_customuser_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_user_permissions
    ADD CONSTRAINT accounts_customuser_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser accounts_customuser_username_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser
    ADD CONSTRAINT accounts_customuser_username_key UNIQUE (username);


--
-- Name: accounts_gridpicupload accounts_gridpicupload_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_gridpicupload
    ADD CONSTRAINT accounts_gridpicupload_pkey PRIMARY KEY (id);


--
-- Name: accounts_invitecode accounts_invitecode_invide_code_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_invitecode
    ADD CONSTRAINT accounts_invitecode_invide_code_key UNIQUE (invite_code);


--
-- Name: accounts_invitecode accounts_invitecode_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_invitecode
    ADD CONSTRAINT accounts_invitecode_pkey PRIMARY KEY (id);


--
-- Name: accounts_portraitupload accounts_portraitupload_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_portraitupload
    ADD CONSTRAINT accounts_portraitupload_pkey PRIMARY KEY (id);


--
-- Name: accounts_stylist accounts_stylist_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_stylist
    ADD CONSTRAINT accounts_stylist_pkey PRIMARY KEY (id);


--
-- Name: accounts_stylist accounts_stylist_user_id_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_stylist
    ADD CONSTRAINT accounts_stylist_user_id_key UNIQUE (user_id);


--
-- Name: accounts_userfollows accounts_userfollows_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_userfollows
    ADD CONSTRAINT accounts_userfollows_pkey PRIMARY KEY (id);


--
-- Name: accounts_userfollows accounts_userfollows_user_from_id_user_to_id_580e77c0_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_userfollows
    ADD CONSTRAINT accounts_userfollows_user_from_id_user_to_id_580e77c0_uniq UNIQUE (user_from_id, user_to_id);


--
-- Name: accounts_useritemcart accounts_useritemcart_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemcart
    ADD CONSTRAINT accounts_useritemcart_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: box_order_items box_order_items_order_id_item_id_05f50c98_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order_items
    ADD CONSTRAINT box_order_items_order_id_item_id_05f50c98_uniq UNIQUE (order_id, item_id);


--
-- Name: box_order_items box_order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order_items
    ADD CONSTRAINT box_order_items_pkey PRIMARY KEY (id);


--
-- Name: box_order box_order_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order
    ADD CONSTRAINT box_order_pkey PRIMARY KEY (id);


--
-- Name: box_return box_return_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_return
    ADD CONSTRAINT box_return_pkey PRIMARY KEY (id);


--
-- Name: box_ticket_outfits_all box_ticket_outfits_all_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_outfits_all
    ADD CONSTRAINT box_ticket_outfits_all_pkey PRIMARY KEY (id);


--
-- Name: box_ticket_outfits_all box_ticket_outfits_all_ticket_id_outfit_id_77064bdc_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_outfits_all
    ADD CONSTRAINT box_ticket_outfits_all_ticket_id_outfit_id_77064bdc_uniq UNIQUE (ticket_id, outfit_id);


--
-- Name: box_ticket box_ticket_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket
    ADD CONSTRAINT box_ticket_pkey PRIMARY KEY (id);


--
-- Name: box_ticket_stylists_all box_ticket_stylists_all_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_stylists_all
    ADD CONSTRAINT box_ticket_stylists_all_pkey PRIMARY KEY (id);


--
-- Name: box_ticket_stylists_all box_ticket_stylists_all_ticket_id_customuser_id_29fd01cb_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_stylists_all
    ADD CONSTRAINT box_ticket_stylists_all_ticket_id_customuser_id_29fd01cb_uniq UNIQUE (ticket_id, customuser_id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: outfit_table_items outfit_table_items_outfit_id_item_id_07aba569_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table_items
    ADD CONSTRAINT outfit_table_items_outfit_id_item_id_07aba569_uniq UNIQUE (outfit_id, item_id);


--
-- Name: outfit_table_items outfit_table_items_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table_items
    ADD CONSTRAINT outfit_table_items_pkey PRIMARY KEY (id);


--
-- Name: outfit_table outfit_table_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table
    ADD CONSTRAINT outfit_table_pkey PRIMARY KEY (id);


--
-- Name: studio_item studio_item_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item
    ADD CONSTRAINT studio_item_pkey PRIMARY KEY (id);


--
-- Name: studio_item_sizes_shoe_eu studio_item_sizes_shoe_e_item_id_sizeshoeeucatego_a1c872fc_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_eu
    ADD CONSTRAINT studio_item_sizes_shoe_e_item_id_sizeshoeeucatego_a1c872fc_uniq UNIQUE (item_id, sizeshoeeucategory_id);


--
-- Name: studio_item_sizes_shoe_eu studio_item_sizes_shoe_eu_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_eu
    ADD CONSTRAINT studio_item_sizes_shoe_eu_pkey PRIMARY KEY (id);


--
-- Name: studio_item_sizes_shoe_uk studio_item_sizes_shoe_u_item_id_sizeshoeukcatego_3525dfc6_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_uk
    ADD CONSTRAINT studio_item_sizes_shoe_u_item_id_sizeshoeukcatego_3525dfc6_uniq UNIQUE (item_id, sizeshoeukcategory_id);


--
-- Name: studio_item_sizes_shoe_uk studio_item_sizes_shoe_uk_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_uk
    ADD CONSTRAINT studio_item_sizes_shoe_uk_pkey PRIMARY KEY (id);


--
-- Name: studio_item_sizes_waist_inches studio_item_sizes_waist__item_id_sizewaistinchcat_0679ca7a_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_waist_inches
    ADD CONSTRAINT studio_item_sizes_waist__item_id_sizewaistinchcat_0679ca7a_uniq UNIQUE (item_id, sizewaistinchcategory_id);


--
-- Name: studio_item_sizes_waist_inches studio_item_sizes_waist_inches_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_waist_inches
    ADD CONSTRAINT studio_item_sizes_waist_inches_pkey PRIMARY KEY (id);


--
-- Name: studio_item_sizes_xyz studio_item_sizes_xyz_item_id_sizecategory_id_61af94f4_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_xyz
    ADD CONSTRAINT studio_item_sizes_xyz_item_id_sizecategory_id_61af94f4_uniq UNIQUE (item_id, sizecategory_id);


--
-- Name: studio_item_sizes_xyz studio_item_sizes_xyz_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_xyz
    ADD CONSTRAINT studio_item_sizes_xyz_pkey PRIMARY KEY (id);


--
-- Name: studio_item_taglist studio_item_taglist_item_id_tag_id_3699882e_uniq; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_taglist
    ADD CONSTRAINT studio_item_taglist_item_id_tag_id_3699882e_uniq UNIQUE (item_id, tag_id);


--
-- Name: studio_item_taglist studio_item_taglist_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_taglist
    ADD CONSTRAINT studio_item_taglist_pkey PRIMARY KEY (id);


--
-- Name: studio_ecommercestore studio_shopifystore_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_ecommercestore
    ADD CONSTRAINT studio_shopifystore_pkey PRIMARY KEY (id);


--
-- Name: studio_sizecategory studio_sizecategory_name_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizecategory
    ADD CONSTRAINT studio_sizecategory_name_key UNIQUE (name);


--
-- Name: studio_sizecategory studio_sizecategory_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizecategory
    ADD CONSTRAINT studio_sizecategory_pkey PRIMARY KEY (id);


--
-- Name: studio_sizeshoeeucategory studio_sizeshoeeucategory_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizeshoeeucategory
    ADD CONSTRAINT studio_sizeshoeeucategory_pkey PRIMARY KEY (id);


--
-- Name: studio_sizeshoeeucategory studio_sizeshoeeucategory_size_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizeshoeeucategory
    ADD CONSTRAINT studio_sizeshoeeucategory_size_key UNIQUE (size);


--
-- Name: studio_sizeshoeukcategory studio_sizeshoeukcategory_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizeshoeukcategory
    ADD CONSTRAINT studio_sizeshoeukcategory_pkey PRIMARY KEY (id);


--
-- Name: studio_sizeshoeukcategory studio_sizeshoeukcategory_size_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizeshoeukcategory
    ADD CONSTRAINT studio_sizeshoeukcategory_size_key UNIQUE (size);


--
-- Name: studio_sizewaistinchcategory studio_sizewaistinchcategory_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizewaistinchcategory
    ADD CONSTRAINT studio_sizewaistinchcategory_pkey PRIMARY KEY (id);


--
-- Name: studio_sizewaistinchcategory studio_sizewaistinchcategory_size_key; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_sizewaistinchcategory
    ADD CONSTRAINT studio_sizewaistinchcategory_size_key UNIQUE (size);


--
-- Name: studio_studiooutfittemp studio_studiooutfittemp_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_studiooutfittemp
    ADD CONSTRAINT studio_studiooutfittemp_pkey PRIMARY KEY (id);


--
-- Name: studio_style studio_style_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_style
    ADD CONSTRAINT studio_style_pkey PRIMARY KEY (id);


--
-- Name: studio_tag studio_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_tag
    ADD CONSTRAINT studio_tag_pkey PRIMARY KEY (id);


--
-- Name: accounts_useritemlikes user_item_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemlikes
    ADD CONSTRAINT user_item_likes_pkey PRIMARY KEY (id);


--
-- Name: accounts_customuser_groups_customuser_id_bc55088e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_groups_customuser_id_bc55088e ON public.accounts_customuser_groups USING btree (customuser_id);


--
-- Name: accounts_customuser_groups_group_id_86ba5f9e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_groups_group_id_86ba5f9e ON public.accounts_customuser_groups USING btree (group_id);


--
-- Name: accounts_customuser_studio_styles_customuser_id_faf3667f; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_studio_styles_customuser_id_faf3667f ON public.accounts_customuser_studio_styles USING btree (customuser_id);


--
-- Name: accounts_customuser_studio_styles_style_id_24b87f8a; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_studio_styles_style_id_24b87f8a ON public.accounts_customuser_studio_styles USING btree (style_id);


--
-- Name: accounts_customuser_trending_styles_customuser_id_15ec1e16; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_trending_styles_customuser_id_15ec1e16 ON public.accounts_customuser_trending_styles USING btree (customuser_id);


--
-- Name: accounts_customuser_trending_styles_style_id_4f1f5255; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_trending_styles_style_id_4f1f5255 ON public.accounts_customuser_trending_styles USING btree (style_id);


--
-- Name: accounts_customuser_user_permissions_customuser_id_0deaefae; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_user_permissions_customuser_id_0deaefae ON public.accounts_customuser_user_permissions USING btree (customuser_id);


--
-- Name: accounts_customuser_user_permissions_permission_id_aea3d0e5; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_user_permissions_permission_id_aea3d0e5 ON public.accounts_customuser_user_permissions USING btree (permission_id);


--
-- Name: accounts_customuser_username_722f3555_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_customuser_username_722f3555_like ON public.accounts_customuser USING btree (username varchar_pattern_ops);


--
-- Name: accounts_gridpicupload_uploader_id_id_b18a103b; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_gridpicupload_uploader_id_id_b18a103b ON public.accounts_gridpicupload USING btree (uploader_id_id);


--
-- Name: accounts_invitecode_invide_code_4f00a3d8_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_invitecode_invide_code_4f00a3d8_like ON public.accounts_invitecode USING btree (invite_code varchar_pattern_ops);


--
-- Name: accounts_invitecode_invitee_id_cab4364e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_invitecode_invitee_id_cab4364e ON public.accounts_invitecode USING btree (invitee_id);


--
-- Name: accounts_invitecode_inviter_id_a90ca96f; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_invitecode_inviter_id_a90ca96f ON public.accounts_invitecode USING btree (inviter_id);


--
-- Name: accounts_portraitupload_outfit_id_id_1eb81bcf; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_portraitupload_outfit_id_id_1eb81bcf ON public.accounts_portraitupload USING btree (outfit_id_id);


--
-- Name: accounts_portraitupload_wearer_id_id_9f0bab96; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_portraitupload_wearer_id_id_9f0bab96 ON public.accounts_portraitupload USING btree (wearer_id_id);


--
-- Name: accounts_userfollows_user_from_id_d811b0c8; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_userfollows_user_from_id_d811b0c8 ON public.accounts_userfollows USING btree (user_from_id);


--
-- Name: accounts_userfollows_user_to_id_e8a64c34; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_userfollows_user_to_id_e8a64c34 ON public.accounts_userfollows USING btree (user_to_id);


--
-- Name: accounts_useritemcart_buyer_id_1ea1aec9; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_useritemcart_buyer_id_1ea1aec9 ON public.accounts_useritemcart USING btree (buyer_id);


--
-- Name: accounts_useritemcart_item_id_987c50eb; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_useritemcart_item_id_987c50eb ON public.accounts_useritemcart USING btree (item_id);


--
-- Name: accounts_useritemcart_styler_id_ea8c20c2; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX accounts_useritemcart_styler_id_ea8c20c2 ON public.accounts_useritemcart USING btree (styler_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: box_order_creator_id_id_5e8c2ce7; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_order_creator_id_id_5e8c2ce7 ON public.box_order USING btree (creator_id_id);


--
-- Name: box_order_items_item_id_59252d7e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_order_items_item_id_59252d7e ON public.box_order_items USING btree (item_id);


--
-- Name: box_order_items_order_id_c7fe9010; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_order_items_order_id_c7fe9010 ON public.box_order_items USING btree (order_id);


--
-- Name: box_order_ticket_id_id_1a0761f7; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_order_ticket_id_id_1a0761f7 ON public.box_order USING btree (ticket_id_id);


--
-- Name: box_return_order_id_id_25600e2e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_return_order_id_id_25600e2e ON public.box_return USING btree (order_id_id);


--
-- Name: box_return_returner_id_id_da4c4f43; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_return_returner_id_id_da4c4f43 ON public.box_return USING btree (returner_id_id);


--
-- Name: box_ticket_creator_id_id_543a2607; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_creator_id_id_543a2607 ON public.box_ticket USING btree (creator_id_id);


--
-- Name: box_ticket_outfit1_id_18acb247; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_outfit1_id_18acb247 ON public.box_ticket USING btree (outfit1_id);


--
-- Name: box_ticket_outfit2_id_15393545; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_outfit2_id_15393545 ON public.box_ticket USING btree (outfit2_id);


--
-- Name: box_ticket_outfits_all_outfit_id_62f4fa7e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_outfits_all_outfit_id_62f4fa7e ON public.box_ticket_outfits_all USING btree (outfit_id);


--
-- Name: box_ticket_outfits_all_ticket_id_3267b5c9; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_outfits_all_ticket_id_3267b5c9 ON public.box_ticket_outfits_all USING btree (ticket_id);


--
-- Name: box_ticket_style1_id_92bcaabd; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_style1_id_92bcaabd ON public.box_ticket USING btree (style1_id);


--
-- Name: box_ticket_style2_id_7a84ce55; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_style2_id_7a84ce55 ON public.box_ticket USING btree (style2_id);


--
-- Name: box_ticket_stylists_all_customuser_id_bc9b4441; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_stylists_all_customuser_id_bc9b4441 ON public.box_ticket_stylists_all USING btree (customuser_id);


--
-- Name: box_ticket_stylists_all_ticket_id_c6168cac; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX box_ticket_stylists_all_ticket_id_c6168cac ON public.box_ticket_stylists_all USING btree (ticket_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: outfit_table_items_item_id_81080f12; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX outfit_table_items_item_id_81080f12 ON public.outfit_table_items USING btree (item_id);


--
-- Name: outfit_table_items_outfit_id_3c6dcc46; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX outfit_table_items_outfit_id_3c6dcc46 ON public.outfit_table_items USING btree (outfit_id);


--
-- Name: outfit_table_maker_id_id_48df3afd; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX outfit_table_maker_id_id_48df3afd ON public.outfit_table USING btree (maker_id_id);


--
-- Name: outfit_table_ticket_id_id_d5c3777b; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX outfit_table_ticket_id_id_d5c3777b ON public.outfit_table USING btree (ticket_id_id);


--
-- Name: studio_item_shopify_store_id_91c3d0f8; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_shopify_store_id_91c3d0f8 ON public.studio_item USING btree (ecommerce_store_id);


--
-- Name: studio_item_sizes_shoe_eu_item_id_83ecbde6; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_shoe_eu_item_id_83ecbde6 ON public.studio_item_sizes_shoe_eu USING btree (item_id);


--
-- Name: studio_item_sizes_shoe_eu_sizeshoeeucategory_id_218f546c; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_shoe_eu_sizeshoeeucategory_id_218f546c ON public.studio_item_sizes_shoe_eu USING btree (sizeshoeeucategory_id);


--
-- Name: studio_item_sizes_shoe_uk_item_id_896df26b; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_shoe_uk_item_id_896df26b ON public.studio_item_sizes_shoe_uk USING btree (item_id);


--
-- Name: studio_item_sizes_shoe_uk_sizeshoeukcategory_id_40bbdd4d; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_shoe_uk_sizeshoeukcategory_id_40bbdd4d ON public.studio_item_sizes_shoe_uk USING btree (sizeshoeukcategory_id);


--
-- Name: studio_item_sizes_waist_in_sizewaistinchcategory_id_1905fea0; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_waist_in_sizewaistinchcategory_id_1905fea0 ON public.studio_item_sizes_waist_inches USING btree (sizewaistinchcategory_id);


--
-- Name: studio_item_sizes_waist_inches_item_id_716f2b77; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_waist_inches_item_id_716f2b77 ON public.studio_item_sizes_waist_inches USING btree (item_id);


--
-- Name: studio_item_sizes_xyz_item_id_5724c172; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_xyz_item_id_5724c172 ON public.studio_item_sizes_xyz USING btree (item_id);


--
-- Name: studio_item_sizes_xyz_sizecategory_id_9e97caf6; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_sizes_xyz_sizecategory_id_9e97caf6 ON public.studio_item_sizes_xyz USING btree (sizecategory_id);


--
-- Name: studio_item_taglist_item_id_dd8bd9e7; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_taglist_item_id_dd8bd9e7 ON public.studio_item_taglist USING btree (item_id);


--
-- Name: studio_item_taglist_tag_id_def765ac; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_item_taglist_tag_id_def765ac ON public.studio_item_taglist USING btree (tag_id);


--
-- Name: studio_sizecategory_name_b9eeea07_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_sizecategory_name_b9eeea07_like ON public.studio_sizecategory USING btree (name varchar_pattern_ops);


--
-- Name: studio_sizeshoeeucategory_size_833ebf14_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_sizeshoeeucategory_size_833ebf14_like ON public.studio_sizeshoeeucategory USING btree (size varchar_pattern_ops);


--
-- Name: studio_sizeshoeukcategory_size_dbb77d5f_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_sizeshoeukcategory_size_dbb77d5f_like ON public.studio_sizeshoeukcategory USING btree (size varchar_pattern_ops);


--
-- Name: studio_sizewaistinchcategory_size_53af147f_like; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_sizewaistinchcategory_size_53af147f_like ON public.studio_sizewaistinchcategory USING btree (size varchar_pattern_ops);


--
-- Name: studio_studiooutfittemp_ticket_id_12d723fd; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_studiooutfittemp_ticket_id_12d723fd ON public.studio_studiooutfittemp USING btree (ticket_id);


--
-- Name: studio_studiooutfittemp_user_id_fbd145ab; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX studio_studiooutfittemp_user_id_fbd145ab ON public.studio_studiooutfittemp USING btree (user_id);


--
-- Name: user_item_likes_item_id_c245e38a; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX user_item_likes_item_id_c245e38a ON public.accounts_useritemlikes USING btree (item_id);


--
-- Name: user_item_likes_liker_id_3db3e01e; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX user_item_likes_liker_id_3db3e01e ON public.accounts_useritemlikes USING btree (liker_id);


--
-- Name: user_item_likes_styler_id_b7f48007; Type: INDEX; Schema: public; Owner: u2m4eitidqus9h
--

CREATE INDEX user_item_likes_styler_id_b7f48007 ON public.accounts_useritemlikes USING btree (styler_id);


--
-- Name: accounts_customer accounts_customer_user_id_11606857_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customer
    ADD CONSTRAINT accounts_customer_user_id_11606857_fk_accounts_customuser_id FOREIGN KEY (user_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_user_permissions accounts_customuser__customuser_id_0deaefae_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_user_permissions
    ADD CONSTRAINT accounts_customuser__customuser_id_0deaefae_fk_accounts_ FOREIGN KEY (customuser_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_trending_styles accounts_customuser__customuser_id_15ec1e16_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_trending_styles
    ADD CONSTRAINT accounts_customuser__customuser_id_15ec1e16_fk_accounts_ FOREIGN KEY (customuser_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_groups accounts_customuser__customuser_id_bc55088e_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_groups
    ADD CONSTRAINT accounts_customuser__customuser_id_bc55088e_fk_accounts_ FOREIGN KEY (customuser_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_studio_styles accounts_customuser__customuser_id_faf3667f_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_studio_styles
    ADD CONSTRAINT accounts_customuser__customuser_id_faf3667f_fk_accounts_ FOREIGN KEY (customuser_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_user_permissions accounts_customuser__permission_id_aea3d0e5_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_user_permissions
    ADD CONSTRAINT accounts_customuser__permission_id_aea3d0e5_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_studio_styles accounts_customuser__style_id_24b87f8a_fk_studio_st; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_studio_styles
    ADD CONSTRAINT accounts_customuser__style_id_24b87f8a_fk_studio_st FOREIGN KEY (style_id) REFERENCES public.studio_style(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_trending_styles accounts_customuser__style_id_4f1f5255_fk_studio_st; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_trending_styles
    ADD CONSTRAINT accounts_customuser__style_id_4f1f5255_fk_studio_st FOREIGN KEY (style_id) REFERENCES public.studio_style(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_customuser_groups accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_customuser_groups
    ADD CONSTRAINT accounts_customuser_groups_group_id_86ba5f9e_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_gridpicupload accounts_gridpicuplo_uploader_id_id_b18a103b_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_gridpicupload
    ADD CONSTRAINT accounts_gridpicuplo_uploader_id_id_b18a103b_fk_accounts_ FOREIGN KEY (uploader_id_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_invitecode accounts_invitecode_invitee_id_cab4364e_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_invitecode
    ADD CONSTRAINT accounts_invitecode_invitee_id_cab4364e_fk_accounts_ FOREIGN KEY (invitee_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_invitecode accounts_invitecode_inviter_id_a90ca96f_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_invitecode
    ADD CONSTRAINT accounts_invitecode_inviter_id_a90ca96f_fk_accounts_ FOREIGN KEY (inviter_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_portraitupload accounts_portraitupl_outfit_id_id_1eb81bcf_fk_outfit_ta; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_portraitupload
    ADD CONSTRAINT accounts_portraitupl_outfit_id_id_1eb81bcf_fk_outfit_ta FOREIGN KEY (outfit_id_id) REFERENCES public.outfit_table(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_portraitupload accounts_portraitupl_wearer_id_id_9f0bab96_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_portraitupload
    ADD CONSTRAINT accounts_portraitupl_wearer_id_id_9f0bab96_fk_accounts_ FOREIGN KEY (wearer_id_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_stylist accounts_stylist_user_id_aa195999_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_stylist
    ADD CONSTRAINT accounts_stylist_user_id_aa195999_fk_accounts_customuser_id FOREIGN KEY (user_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_userfollows accounts_userfollows_user_from_id_d811b0c8_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_userfollows
    ADD CONSTRAINT accounts_userfollows_user_from_id_d811b0c8_fk_accounts_ FOREIGN KEY (user_from_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_userfollows accounts_userfollows_user_to_id_e8a64c34_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_userfollows
    ADD CONSTRAINT accounts_userfollows_user_to_id_e8a64c34_fk_accounts_ FOREIGN KEY (user_to_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_useritemcart accounts_useritemcar_buyer_id_1ea1aec9_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemcart
    ADD CONSTRAINT accounts_useritemcar_buyer_id_1ea1aec9_fk_accounts_ FOREIGN KEY (buyer_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_useritemcart accounts_useritemcar_styler_id_ea8c20c2_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemcart
    ADD CONSTRAINT accounts_useritemcar_styler_id_ea8c20c2_fk_accounts_ FOREIGN KEY (styler_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_useritemcart accounts_useritemcart_item_id_987c50eb_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemcart
    ADD CONSTRAINT accounts_useritemcart_item_id_987c50eb_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_order box_order_creator_id_id_5e8c2ce7_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order
    ADD CONSTRAINT box_order_creator_id_id_5e8c2ce7_fk_accounts_customuser_id FOREIGN KEY (creator_id_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_order_items box_order_items_item_id_59252d7e_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order_items
    ADD CONSTRAINT box_order_items_item_id_59252d7e_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_order_items box_order_items_order_id_c7fe9010_fk_box_order_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order_items
    ADD CONSTRAINT box_order_items_order_id_c7fe9010_fk_box_order_id FOREIGN KEY (order_id) REFERENCES public.box_order(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_order box_order_ticket_id_id_1a0761f7_fk_box_ticket_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_order
    ADD CONSTRAINT box_order_ticket_id_id_1a0761f7_fk_box_ticket_id FOREIGN KEY (ticket_id_id) REFERENCES public.box_ticket(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_return box_return_order_id_id_25600e2e_fk_box_order_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_return
    ADD CONSTRAINT box_return_order_id_id_25600e2e_fk_box_order_id FOREIGN KEY (order_id_id) REFERENCES public.box_order(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_return box_return_returner_id_id_da4c4f43_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_return
    ADD CONSTRAINT box_return_returner_id_id_da4c4f43_fk_accounts_customuser_id FOREIGN KEY (returner_id_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket box_ticket_creator_id_id_543a2607_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket
    ADD CONSTRAINT box_ticket_creator_id_id_543a2607_fk_accounts_customuser_id FOREIGN KEY (creator_id_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket box_ticket_outfit1_id_18acb247_fk_outfit_table_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket
    ADD CONSTRAINT box_ticket_outfit1_id_18acb247_fk_outfit_table_id FOREIGN KEY (outfit1_id) REFERENCES public.outfit_table(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket box_ticket_outfit2_id_15393545_fk_outfit_table_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket
    ADD CONSTRAINT box_ticket_outfit2_id_15393545_fk_outfit_table_id FOREIGN KEY (outfit2_id) REFERENCES public.outfit_table(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket_outfits_all box_ticket_outfits_all_outfit_id_62f4fa7e_fk_outfit_table_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_outfits_all
    ADD CONSTRAINT box_ticket_outfits_all_outfit_id_62f4fa7e_fk_outfit_table_id FOREIGN KEY (outfit_id) REFERENCES public.outfit_table(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket_outfits_all box_ticket_outfits_all_ticket_id_3267b5c9_fk_box_ticket_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_outfits_all
    ADD CONSTRAINT box_ticket_outfits_all_ticket_id_3267b5c9_fk_box_ticket_id FOREIGN KEY (ticket_id) REFERENCES public.box_ticket(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket box_ticket_style1_id_92bcaabd_fk_studio_style_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket
    ADD CONSTRAINT box_ticket_style1_id_92bcaabd_fk_studio_style_id FOREIGN KEY (style1_id) REFERENCES public.studio_style(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket box_ticket_style2_id_7a84ce55_fk_studio_style_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket
    ADD CONSTRAINT box_ticket_style2_id_7a84ce55_fk_studio_style_id FOREIGN KEY (style2_id) REFERENCES public.studio_style(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket_stylists_all box_ticket_stylists__customuser_id_bc9b4441_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_stylists_all
    ADD CONSTRAINT box_ticket_stylists__customuser_id_bc9b4441_fk_accounts_ FOREIGN KEY (customuser_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: box_ticket_stylists_all box_ticket_stylists_all_ticket_id_c6168cac_fk_box_ticket_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.box_ticket_stylists_all
    ADD CONSTRAINT box_ticket_stylists_all_ticket_id_c6168cac_fk_box_ticket_id FOREIGN KEY (ticket_id) REFERENCES public.box_ticket(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_accounts_customuser_id FOREIGN KEY (user_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: outfit_table_items outfit_table_items_item_id_81080f12_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table_items
    ADD CONSTRAINT outfit_table_items_item_id_81080f12_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: outfit_table_items outfit_table_items_outfit_id_3c6dcc46_fk_outfit_table_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table_items
    ADD CONSTRAINT outfit_table_items_outfit_id_3c6dcc46_fk_outfit_table_id FOREIGN KEY (outfit_id) REFERENCES public.outfit_table(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: outfit_table outfit_table_maker_id_id_48df3afd_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table
    ADD CONSTRAINT outfit_table_maker_id_id_48df3afd_fk_accounts_customuser_id FOREIGN KEY (maker_id_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: outfit_table outfit_table_ticket_id_id_d5c3777b_fk_box_ticket_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.outfit_table
    ADD CONSTRAINT outfit_table_ticket_id_id_d5c3777b_fk_box_ticket_id FOREIGN KEY (ticket_id_id) REFERENCES public.box_ticket(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item studio_item_ecommerce_store_id_db7756e1_fk_studio_ec; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item
    ADD CONSTRAINT studio_item_ecommerce_store_id_db7756e1_fk_studio_ec FOREIGN KEY (ecommerce_store_id) REFERENCES public.studio_ecommercestore(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_shoe_eu studio_item_sizes_sh_sizeshoeeucategory_i_218f546c_fk_studio_si; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_eu
    ADD CONSTRAINT studio_item_sizes_sh_sizeshoeeucategory_i_218f546c_fk_studio_si FOREIGN KEY (sizeshoeeucategory_id) REFERENCES public.studio_sizeshoeeucategory(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_shoe_uk studio_item_sizes_sh_sizeshoeukcategory_i_40bbdd4d_fk_studio_si; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_uk
    ADD CONSTRAINT studio_item_sizes_sh_sizeshoeukcategory_i_40bbdd4d_fk_studio_si FOREIGN KEY (sizeshoeukcategory_id) REFERENCES public.studio_sizeshoeukcategory(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_shoe_eu studio_item_sizes_shoe_eu_item_id_83ecbde6_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_eu
    ADD CONSTRAINT studio_item_sizes_shoe_eu_item_id_83ecbde6_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_shoe_uk studio_item_sizes_shoe_uk_item_id_896df26b_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_shoe_uk
    ADD CONSTRAINT studio_item_sizes_shoe_uk_item_id_896df26b_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_waist_inches studio_item_sizes_wa_item_id_716f2b77_fk_studio_it; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_waist_inches
    ADD CONSTRAINT studio_item_sizes_wa_item_id_716f2b77_fk_studio_it FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_waist_inches studio_item_sizes_wa_sizewaistinchcategor_1905fea0_fk_studio_si; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_waist_inches
    ADD CONSTRAINT studio_item_sizes_wa_sizewaistinchcategor_1905fea0_fk_studio_si FOREIGN KEY (sizewaistinchcategory_id) REFERENCES public.studio_sizewaistinchcategory(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_xyz studio_item_sizes_xy_sizecategory_id_9e97caf6_fk_studio_si; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_xyz
    ADD CONSTRAINT studio_item_sizes_xy_sizecategory_id_9e97caf6_fk_studio_si FOREIGN KEY (sizecategory_id) REFERENCES public.studio_sizecategory(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_sizes_xyz studio_item_sizes_xyz_item_id_5724c172_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_sizes_xyz
    ADD CONSTRAINT studio_item_sizes_xyz_item_id_5724c172_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_taglist studio_item_taglist_item_id_dd8bd9e7_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_taglist
    ADD CONSTRAINT studio_item_taglist_item_id_dd8bd9e7_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_item_taglist studio_item_taglist_tag_id_def765ac_fk_studio_tag_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_item_taglist
    ADD CONSTRAINT studio_item_taglist_tag_id_def765ac_fk_studio_tag_id FOREIGN KEY (tag_id) REFERENCES public.studio_tag(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_studiooutfittemp studio_studiooutfitt_user_id_fbd145ab_fk_accounts_; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_studiooutfittemp
    ADD CONSTRAINT studio_studiooutfitt_user_id_fbd145ab_fk_accounts_ FOREIGN KEY (user_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: studio_studiooutfittemp studio_studiooutfittemp_ticket_id_12d723fd_fk_box_ticket_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.studio_studiooutfittemp
    ADD CONSTRAINT studio_studiooutfittemp_ticket_id_12d723fd_fk_box_ticket_id FOREIGN KEY (ticket_id) REFERENCES public.box_ticket(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_useritemlikes user_item_likes_item_id_c245e38a_fk_studio_item_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemlikes
    ADD CONSTRAINT user_item_likes_item_id_c245e38a_fk_studio_item_id FOREIGN KEY (item_id) REFERENCES public.studio_item(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_useritemlikes user_item_likes_liker_id_3db3e01e_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemlikes
    ADD CONSTRAINT user_item_likes_liker_id_3db3e01e_fk_accounts_customuser_id FOREIGN KEY (liker_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: accounts_useritemlikes user_item_likes_styler_id_b7f48007_fk_accounts_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: u2m4eitidqus9h
--

ALTER TABLE ONLY public.accounts_useritemlikes
    ADD CONSTRAINT user_item_likes_styler_id_b7f48007_fk_accounts_customuser_id FOREIGN KEY (styler_id) REFERENCES public.accounts_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO u2m4eitidqus9h;


--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint); Type: ACL; Schema: public; Owner: rdsadmin
--

GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint) TO u2m4eitidqus9h;


--
-- Name: extension_before_drop; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER extension_before_drop ON ddl_command_start
   EXECUTE FUNCTION _heroku.extension_before_drop();


ALTER EVENT TRIGGER extension_before_drop OWNER TO heroku_admin;

--
-- Name: log_create_ext; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER log_create_ext ON ddl_command_end
   EXECUTE FUNCTION _heroku.create_ext();


ALTER EVENT TRIGGER log_create_ext OWNER TO heroku_admin;

--
-- Name: log_drop_ext; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER log_drop_ext ON sql_drop
   EXECUTE FUNCTION _heroku.drop_ext();


ALTER EVENT TRIGGER log_drop_ext OWNER TO heroku_admin;

--
-- Name: validate_extension; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER validate_extension ON ddl_command_end
   EXECUTE FUNCTION _heroku.validate_extension();


ALTER EVENT TRIGGER validate_extension OWNER TO heroku_admin;

--
-- PostgreSQL database dump complete
--

