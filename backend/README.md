# SecuScope Backend

## Setup Instructions

1. **Create & activate virtualenv**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate synthetic logs**
   ```bash
   python -m backend.app.data.synthetic_log_generator
   ```

4. **Train the anomaly detection model**
   ```bash
   python -m backend.app.models.train_model
   ```

5. **Run the Flask server**
   ```bash
   python -m backend.app.main
   ```

Endpoints:
- GET `/api/health`
- GET `/api/logs`
- POST `/api/detect-anomalies`
