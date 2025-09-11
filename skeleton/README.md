# ${{ values.name | title }} - AI Agent for Message Analysis

${{ values.description }}

This AI-powered agent monitors Kafka topics for failed message routing and provides intelligent analysis and notifications through Backstage.

## Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI and LangChain to analyze failed message routing
- 📨 **Kafka Integration**: Monitors Kafka topics for unclassified messages
- 🔔 **Backstage Notifications**: Sends intelligent alerts to Backstage when issues are detected
- 🏥 **Health Checks**: Comprehensive health monitoring
- 🐳 **Docker Ready**: Containerized for easy deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kafka Topic   │───▶│   AI Agent      │───▶│   Backstage     │
│   "unknown"     │    │   (LangChain)   │    │   Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (Analysis)    │
                       └─────────────────┘
```

## Configuration

The service is configured through environment variables:

### Service Configuration
- `SERVICE_NAME`: Name of the AI agent service
- `SERVICE_DESCRIPTION`: Description of what the agent monitors
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Kafka Configuration
- `KAFKA_BROKERS`: Comma-separated list of Kafka broker addresses
- `CONSUMER_GROUP`: Kafka consumer group ID
- `MONITORED_TOPICS`: Comma-separated list of topics to monitor (default: unknown)
- `KAFKA_AUTO_OFFSET_RESET`: Consumer offset reset strategy

### AI Configuration
- `AI_MODEL`: OpenAI model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
- `AI_TEMPERATURE`: Model temperature (0.0-1.0)
- `AI_MAX_TOKENS`: Maximum tokens for AI responses

### Backstage Configuration
- `BACKSTAGE_API_URL`: Base URL for Backstage API
- `BACKSTAGE_TOKEN`: Authentication token for Backstage
- `NOTIFICATION_TITLE`: Default title for notifications

### Monitoring Configuration
- `HEALTH_CHECK_PORT`: Port for health check endpoint (default: 8080)

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd ${{ values.name }}
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Service**:
   ```bash
   python main.py
   ```

## Docker Deployment

1. **Build the Image**:
   ```bash
   docker build -t ${{ values.name }}:latest .
   ```

2. **Run the Container**:
   ```bash
   docker run -d \
     --name ${{ values.name }} \
     --env-file .env \
     -p 8080:8080 \
     ${{ values.name }}:latest
   ```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${{ values.name }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ${{ values.name }}
  template:
    metadata:
      labels:
        app: ${{ values.name }}
    spec:
      containers:
      - name: ${{ values.name }}
        image: ${{ values.name }}:latest
        ports:
        - containerPort: 8080
        env:
        - name: KAFKA_BROKERS
          value: "${{ values.kafkaBrokers }}"
        - name: BACKSTAGE_TOKEN
          valueFrom:
            secretKeyRef:
              name: ${{ values.name }}-secrets
              key: backstage-token
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Monitoring

### Health Check
```bash
curl http://localhost:8080/health
```

The health check endpoint provides information about the service status, AI agent configuration, and Kafka connectivity.

## How It Works

1. **Message Monitoring**: The agent continuously monitors the configured Kafka topics (default: "unknown")

2. **AI Analysis**: When a message is detected, the LangChain agent:
   - Analyzes the message content using OpenAI
   - Determines the likely cause of routing failure
   - Suggests potential resolutions

3. **Notification**: The agent sends a structured notification to Backstage containing:
   - Analysis results
   - Failure cause
   - Suggested actions
   - Message metadata

4. **Error Handling**: If analysis fails, a fallback notification is sent with basic information

## Customization

### Adding New Tools

Create new tools in `src/tools/` and add them to the agent in `src/ai_agent.py`:

```python
from .tools.my_custom_tool import MyCustomTool

def _create_tools(self) -> List[Tool]:
    tools = [
        create_backstage_notification_tool(),
        MyCustomTool(),  # Add your tool here
    ]
    return tools
```

### Custom Analysis Prompts

Modify the `ANALYSIS_PROMPT_TEMPLATE` environment variable to customize how the AI analyzes messages.

## Development

### Testing
```bash
pytest tests/
```

### Code Quality
```bash
black src/
flake8 src/
mypy src/
```

### Local Development
1. Install development dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest`
3. Format code: `black .`
4. Run the service: `python main.py`

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**:
   - Verify `KAFKA_BROKERS` configuration
   - Check network connectivity to Kafka brokers
   - Ensure topics exist

2. **OpenAI API Issues**:
   - Check API rate limits
   - Monitor token usage

3. **Backstage Notification Issues**:
   - Verify `BACKSTAGE_API_URL` and `BACKSTAGE_TOKEN`
   - Check Backstage API logs
   - Ensure notification API is enabled

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run code quality checks
5. Submit a pull request


## Support

For questions and support, please contact the ${{ values.owner }} team or create an issue in the repository. 