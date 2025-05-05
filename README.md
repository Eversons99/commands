# Commands (Project)

The purpose of this repository is to automate tasks related to GPON network management, command sending, and file management. Developed with a focus on preventive maintenance operations and network automation.

## 🧰 Technologies Utilized

- Python  
- Django  
- JavaScript  
- HTML  
- CSS  

## 📁 Directory Structure

```
commands/
├── assets/                     # Static resources (images, scripts, etc.)
├── attenuations_manager_app/   # App to manage attenuations
├── commands_generator_app/     # App to generate GPON migration commands 
├── conf/                       # Configuration files
├── files_manager_app/          # App to manage command files
├── gpon_health_app/            # App to monitor GPON network health
├── maintenance_core_app/       # Main app that links all routes to other apps
├── network_automation/         # Scripts and tools for network automation
├── send_sms_app/               # App to send warning SMS messages about maintenance dates
├── websocket_server/           # WebSocket server for real-time communication with the OLT CLI (Netmiko)
├── commands.json               # Config file used with pm2 (deprecated)
├── manage.py                   # Main script to start the application
├── requirements.txt            # Project dependencies
├── .env                        # File with environment variables
└── .gitignore                  # Files and folders ignored by Git
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Eversons99/commands.git
```

Create and activate a virtual environment (optional, but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Running the Project

This project uses [supervisord](https://supervisord.org/introduction.html) to run both the Commands project and the WebSocket server.

### Create the service file to manage the Commands project:

```bash
sudo nano /etc/supervisor/conf.d/commands.conf
```

```ini
[program:commands]
directory = /home/nmultifibra/commands/
stdout_logfile = /var/log/commands/stdout.log
stderr_logfile = /var/log/commands/stderr.log
command = /home/nmultifibra/commands/virtual-env/bin/gunicorn -c /home/nmultifibra/commands/conf/gunicorn_conf.py network_automation.wsgi
process_name = %(program_name)s
numprocs = 1
startsecs = 5
autorestart = true
```

### Create the service file to manage the WebSocket server:

```bash
sudo nano /etc/supervisor/conf.d/cmd_websocket_supervisord.conf
```

```ini
[program:cmd-websocket]
directory = /home/nmultifibra/commands/websocket_server
stdout_logfile = /var/log/cmd_websocket/stdout.log
stderr_logfile = /var/log/cmd_websocket/stderr.log
command = /home/nmultifibra/commands/virtual-env/bin/python3.11 /home/nmultifibra/commands/websocket_server/app.py
process_name = %(program_name)s
numprocs = 1
startsecs = 5
autorestart = true
```

### Reload Supervisor and start the services:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### Check the application status:

```bash
sudo supervisorctl status
```

You can also monitor the services in your browser:  
**http://127.0.0.1:9001**
