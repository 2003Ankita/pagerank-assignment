# HW3 – Cloud Microservices (GCP)

This repository contains the implementation for Homework 3, which consists of two microservices:

## Service 1: Cloud Function (HTTP)
- Implemented as a Google Cloud Function
- Accepts HTTP GET requests
- Reads files from a Google Cloud Storage bucket
- Returns:
  - 200 OK for existing files
  - 404 Not Found for missing files
  - 501 Not Implemented for unsupported HTTP methods
- Extracts the `X-country` header and blocks requests from forbidden countries
- Publishes forbidden requests to a Pub/Sub topic

## Service 2: Local Subscriber
- Runs locally on a laptop
- Subscribes to the Pub/Sub topic
- Logs forbidden requests to standard output
- Appends forbidden request logs to a file in Google Cloud Storage

## Repository Structure
service1_cloud_function/ # Cloud Function source code
service2_local_subscriber/ # Local Pub/Sub subscriber


## Notes
- A dedicated service account is used for both services
- No gcloud auth application-default login is used
