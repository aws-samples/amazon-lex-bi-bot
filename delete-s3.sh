#!/bin/bash

#
# Deletes the bot, intents, and custom slot types
# in reverse order of build: first the bot, then
# the intents, then the slot types.
#

#
# Environment variables to be set in the CodeBuild project
#
# $ATHENA_BUCKET		S3 bucket where data files reside
# $ATHENA_OUTPUT_LOCATION	S3 bucket for Athena output 
# $ARTIFACT_STORE		S3 bucket for CodePipeline / CodeBuild code sharing
#

echo "Deleting S3 bucket $ATHENA_BUCKET"
aws s3 rm --recursive $ATHENA_BUCKET
aws s3 rb --force $ATHENA_BUCKET

echo "Deleting S3 bucket $ATHENA_OUTPUT_LOCATION"
aws s3 rm --recursive $ATHENA_OUTPUT_LOCATION
aws s3 rb --force $ATHENA_OUTPUT_LOCATION

echo "Deleting S3 bucket $ARTIFACT_STORE"
aws s3 rm --recursive $ARTIFACT_STORE
aws s3 rb --force $ARTIFACT_STORE

