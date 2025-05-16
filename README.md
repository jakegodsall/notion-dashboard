# Notion Dashboard

The **Notion Dashboard** app integrates data from different services
into a Notion database, helping you track and manage your activities seamlessly.

## Integrations

- **LingQ Integration**: Sync your daily word counts into a Notion database.
- **WHOOP Integration**: 
  - Track your workouts, including metrics like heart rate, duration, and calories burned
  - Monitor sleep and recovery data with intelligent date handling for overnight sleep sessions

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jakegodsall/notion-dashboard.git
   cd notion-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the app:
   - Add your Notion API credentials and database configurations to the `src/config/notion.config.yml` file.

---

## Usage

### Command Line Interface

The app provides a rich command-line interface with various commands for different integrations:

#### Get Help
```bash
# Show all available commands
python main.py --help

# Show help for Whoop-specific commands
python main.py whoop --help
```

#### LingQ Commands
```bash
# Sync LingQ word counts
python main.py lingq
```

#### WHOOP Commands
```bash
# Sync workouts for today
python main.py whoop workouts

# Sync workouts for a specific date
python main.py whoop workouts --date 2024-03-20

# Sync sleep and recovery data for today
python main.py whoop sleep

# Sync sleep and recovery for a specific date
python main.py whoop sleep --date 2024-03-20

# Sync sleep data, continuing backwards until first available record
python main.py whoop sleep --date 2024-03-20 --loop-until-first
```

### Run as an AWS Lambda Function

The app includes a `lambda.py` file for running as an AWS Lambda function. This is useful for deploying the app to AWS Lambda for serverless execution.

The project is set up using AWS SAM (Serverless Application Model) for easy deployment. To deploy:

1. Install the AWS SAM CLI if not already installed:

```bash
brew install aws-sam-cli
```

2. Build the project:

```bash
sam build
```

3. Deploy the application:

```bash
sam deploy --guided
```

Follow the prompts to configure the environment variables and other configurations for deployment.

---

## Configuration

### Notion API
Create a `notion.config.yml` file in `src/config` with the following structure:

```yaml
notion:
  key: "notion-key"
  integrations:
    whoop-workout:
      database_id: "database-id"
      field_mappings:
        date:
          label: "Date"
          key: "date"
          type: "date"
        duration:
          label: "Duration"
          key: "duration"
          type: "number"
        distance:
          label: "Distance (km)"
          key: "distance"
          type: "number"
    whoop-sleep-and-recovery:
      database_id: "sleep-database-id"
      field_mappings:
        date:
          label: "Date"
          key: "date"
          type: "date"
        sleep_score:
          label: "Sleep Score"
          key: "sleep_performance_percentage"
          type: "number"
        recovery_score:
          label: "Recovery Score"
          key: "recovery_score"
          type: "number"
```
---

## Troubleshooting

### Common Errors

#### FileNotFoundError: `notion.config.yml`
- Ensure the configuration file exists at `src/config/notion.config.yml` with valid Notion API credentials.

#### ModuleNotFoundError
- Check that your `PYTHONPATH` includes the project root directory:
  ```bash
  export PYTHONPATH=/path/to/notion-dashboard
  ```

#### Sleep Data Synchronization Issues
- The sleep tracking system handles overnight sleep sessions by checking both the current and previous day for matching records
- If you see duplicate records, ensure you're not running multiple syncs for the same sleep session across different days

---

## Contributing

1. Fork the repository.
2. Create a new feature branch:
   ```bash
   git checkout -b my-new-feature
   ```
3. Commit your changes:
   ```bash
   git commit -am 'Add some feature'
   ```
4. Push to the branch:
   ```bash
   git push origin my-new-feature
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
