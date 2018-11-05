#!/bin/bash

#
# Creates the Athena database
#

#
# Environment variables to be set in the CodeBuild project
#
# $ATHENA_DB    		Name of the Athena database
# $ATHENA_BUCKET		Name of the S3 bucket where the data is stored
# $ATHENA_BUCKET_REGION		Region for the S3 bucket where the data is stored
# $ATHENA_DB_DESCRIPTION	Description for the Athena database
#

echo "Starting build-db.sh"
echo '$ATHENA_DB' "= $ATHENA_DB"
echo '$ATHENA_BUCKET' "= $ATHENA_BUCKET"
echo '$ATHENA_BUCKET_REGION' "= $ATHENA_BUCKET_REGION"
echo '$ATHENA_DB_DESCRIPTION' "= $ATHENA_DB_DESCRIPTION"
echo

# Create TICKIT database
echo "Creating Athena database $ATHENA_DB"
aws glue create-database --database-input "Name=$ATHENA_DB,Description=$ATHENA_DB_DESCRIPTION" >/dev/null

# Create TICKIT users table in Athena
echo "Creating users table..."
aws athena start-query-execution \
    --query-string "create external table users (user_id INT, username STRING, firstname STRING, lastname STRING, city STRING, state STRING, email STRING, phone STRING, like_sports BOOLEAN, liketheatre BOOLEAN, likeconcerts BOOLEAN, likejazz BOOLEAN, likeclassical BOOLEAN, likeopera BOOLEAN, likerock BOOLEAN, likevegas BOOLEAN, likebroadway BOOLEAN, likemusicals BOOLEAN) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/users';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create TICKIT venue table in Athena
echo "Creating venue table..."
aws athena start-query-execution \
    --query-string "create external table venue (venue_id INT, venue_name STRING, venue_city STRING, venue_state STRING, venue_seats INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/venue';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create TICKIT category table in Athena
echo "Creating category table..."
aws athena start-query-execution \
    --query-string "create external table category (cat_id INT, cat_group STRING, cat_name STRING, cat_desc STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/category';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create TICKIT date table in Athena
echo "Creating date_dim table..."
aws athena start-query-execution \
    --query-string "create external table date_dim (date_id INT, cal_date DATE, day STRING, week STRING, month STRING, quarter STRING, year INT, holiday BOOLEAN) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/date';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create TICKIT event table in Athena
echo "Creating event table..."
aws athena start-query-execution \
    --query-string "create external table event (event_id INT, venue_id INT, cat_id INT, date_id INT, event_name STRING, start_time TIMESTAMP) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/event';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create TICKIT listing table in Athena
echo "Creating listing table..."
aws athena start-query-execution \
    --query-string "create external table listing (list_id INT, seller_id INT, event_id INT, date_id INT, qty INT, price DECIMAL(8,2), total DECIMAL(8,2), listing_time TIMESTAMP) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/listing';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create TICKIT sales table in Athena
echo "Creating sales table..."
aws athena start-query-execution \
    --query-string "create external table sales (sales_id INT, list_id INT, seller_id INT, buyer_id INT, event_id INT, date_id INT, qty INT, amount DECIMAL(8,2), commission DECIMAL(8,2), sale_time TIMESTAMP) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' LOCATION '$ATHENA_BUCKET/sales';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null


