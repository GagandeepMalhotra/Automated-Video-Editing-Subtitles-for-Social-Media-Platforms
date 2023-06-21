# Setting up Google Speech-to-Text API and Obtaining key.json

This guide will walk you through the steps to set up the Google Speech-to-Text API and obtain a `key.json` file in the specified format. The `key.json` file contains the necessary credentials for accessing the API.

## Prerequisites

Before you begin, make sure you have the following:

- A Google Cloud Platform (GCP) account. If you don't have one, you can create a new account at [Google Cloud](https://cloud.google.com/).
- Billing enabled for your GCP project. The Speech-to-Text API usage is not free, so you need to enable billing and ensure you understand the pricing details. You can find the pricing information at [Speech-to-Text Pricing](https://cloud.google.com/speech-to-text/pricing).

## Steps

Follow the steps below to create a Google Speech-to-Text API and obtain the `key.json` file.

### Step 1: Create a GCP Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown menu at the top of the page and select or create the project you want to use for the Speech-to-Text API.

### Step 2: Enable the Speech-to-Text API

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. In the sidebar, click on "APIs & Services" and then select "Library" from the submenu.
3. In the search bar, type "Speech-to-Text" and click on the "Google Cloud Speech-to-Text API" result.
4. Click the "Enable" button to enable the Speech-to-Text API for your project.

### Step 3: Create Service Account Credentials

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. In the sidebar, click on "APIs & Services" and then select "Credentials" from the submenu.
3. Click on the "Create Credentials" dropdown and select "Service Account".
4. Fill in the necessary details for the service account. You can provide a name and description for the account.
5. Assign the "Project > Editor" role to the service account.
6. Click the "Continue" button.
7. In the "Key Type" section, select "JSON" and click the "Create" button.
8. Save the generated JSON file. This file is your `key.json` file.

### Step 4: Configure the `key.json` File

1. Open the `key.json` file you downloaded.
2. Copy the contents of the file.
3. Create a new file named `key.json` in your project directory.
4. Paste the copied contents into the `key.json` file.
5. Modify the following fields with the appropriate values:

   - `project_id`: Your GCP project ID.
   - `private_key_id`: The private key ID from the `key.json` file.
   - `private_key`: The private key from the `key.json` file.
   - `client_email`: The client email from the `key.json` file.
   - `client_id`: The client ID from the `key.json` file.
   - `client_x509_cert_url`: The client X.509 certificate URL from the `key.json` file.

6. Ensure the `universe_domain` field is set to "googleapis.com".
