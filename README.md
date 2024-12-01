
# Notion Dashboard

The **Notion Dashboard** app integrates data from different services
into a Notion database, helping you track and manage your activities seamlessly.

## Features

- **LingQ Integration**: Sync your daily word counts into a Notion database.
- **WHOOP Integration**: Track your workouts, including metrics like heart rate, duration, and calories burned.
- **Automatic Scheduling**: Use cron jobs to automate the synchronization process.

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

### Run Manually
You can manually run the sync process:

```bash
python src/main.py
```

### Automate with Cron
To automate the process, schedule the script using cron:
1. Open the crontab editor:
   ```bash
   crontab -e
   ```
2. Add the following line to run the app daily at 23:55:
   ```bash
   55 23 * * * /path/to/your/venv/bin/python /path/to/notion-dashboard/src/main.py >> /path/to/logs/dashboard.logs 2>&1
   ```

---

## Configuration

### Notion API
Create a `notion.config.yml` file in `src/config` with the following structure:

```yaml
notion:
  key: "notion-key"
  integrations:
    whoop:
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

#### Cron Job Doesn't Run
- Check your cron logs:
  ```bash
  grep CRON /var/log/syslog
  ```

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
