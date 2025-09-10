BEGIN;

ALTER TABLE fund_navs DROP CONSTRAINT IF EXISTS fund_navs_pkey;
ALTER TABLE fund_navs ADD COLUMN IF NOT EXISTS id BIGSERIAL;
ALTER TABLE fund_navs ADD CONSTRAINT fund_navs_pkey PRIMARY KEY (id);
ALTER TABLE fund_navs ADD CONSTRAINT fund_navs_fund_id_date_uniq UNIQUE (fund_id, "date");
COMMIT;
