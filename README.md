# Smart City Telemetry Dashboard (INF2003)

This repository contains the source code for Group 68's Smart City Telemetry Dashboard, featuring a hybrid database architecture (PostgreSQL & MongoDB), a Python Flask API backend, and a React Native (Expo) mobile frontend.

## Prerequisites

Before running this project, ensure you have the following installed on your machine:

* **Python 3.8+**

* **Node.js & npm**

* **PostgreSQL** (Running locally on default port 5432)

* **MongoDB** (Running locally or via MongoDB Atlas)

* **Expo Go** application installed on your physical iOS/Android device.

## Step 1: Database Initialisation

First, we need to populate both the relational and non-relational databases with the smart city sensor and maintenance data.

1. Open a terminal in the root project directory.

2. Ensure your local PostgreSQL and MongoDB servers are actively running.

3. Run the bulk ingestion script to build the schemas and populate the dummy data:

   ```
   python ingest.py
   
   ```

   *(Note: Ensure your database connection strings/URIs inside the script match your local setup).*

## Step 2: Start the Flask Backend

The Flask server acts as the API gateway between the databases and the mobile application.

1. Open a terminal in the root project directory.

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   
   ```

3. Start the Flask server:

   ```
   python app.py
   
   ```

4. **Important:** The terminal should state `* Running on all addresses (0.0.0.0)`. This allows external devices on your local network to connect.

## Step 3: Configure the Frontend IP Address

Because you are running the app on a physical mobile device, the frontend needs to know your computer's local Wi-Fi IP address to communicate with the Flask backend.

1. Find your computer's local IPv4 address (e.g., run `ipconfig` on Windows or `ifconfig` on Mac).

2. Open `smart-city-ui/src/app/index.tsx` and `smart-city-ui/src/app/logs.tsx`.

3. Locate the `API_BASE_URL` variable at the top of both files and update it with your exact IP address:

   ```
   // Example:
   const API_BASE_URL = 'http://192.168.1.15:5000/api';
   
   ```

## Step 4: Start the Expo Frontend

Now, start the React Native mobile application.

1. Open a **new** terminal window (keep the Flask terminal running) and navigate to the UI folder:

   ```
   cd smart-city-ui
   
   ```

2. Install the Node modules:

   ```
   npm install
   
   ```

3. Start the Expo server (clearing the cache is recommended to ensure IP changes are registered):

   ```
   npx expo start -c
   
   ```

## Step 5: View on Mobile Device

1. Connect your physical phone to the **same Wi-Fi network** as your computer.

2. Open the **Expo Go** app on your phone.

3. Scan the QR code generated in your Expo terminal.

4. The app will bundle and open. You can now toggle between the MongoDB live telemetry dashboard ("Home") and the PostgreSQL maintenance logs ("Logs").

### Troubleshooting Network Errors

If the app loads but shows an `[AxiosError: Network Error]`:

* Verify your computer's firewall is not blocking Port `5000`.

* Ensure your Windows Network Profile is set to **Private**, not Public.

* Ensure your phone has not automatically switched to cellular data.

* Double-check that the IP address in your `.tsx` files perfectly matches your computer's current IPv4 address.