#!/usr/bin/env python3
"""Main entry point for the AI Agent."""

import logging
import signal
import sys
from typing import Dict, Any

import structlog

from src.config import settings
from src.ai_agent import MessageAnalysisAgent
from src.kafka_consumer import UnknownTopicMonitor
from src.web_server import WebServer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class AIAgentService:    
    def __init__(self):
        self.ai_agent = MessageAnalysisAgent()
        self.kafka_monitor = UnknownTopicMonitor(self._handle_unknown_message)
        self.web_server = WebServer(self)
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("AI Agent service initialized", 
                   service_name=settings.service_name,
                   ai_model=settings.ai_model,
                   monitored_topic=settings.monitored_topic)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def _handle_unknown_message(self, message_content: str, metadata: Dict[str, Any]):
        try:
            logger.info("Processing unknown message", 
                       topic=metadata.get('topic'),
                       partition=metadata.get('partition'),
                       offset=metadata.get('offset'))
            
            # Use the AI agent to analyze the message
            self.ai_agent.process_unknown_message(message_content, metadata)
            
        except Exception as e:
            logger.error("Error handling unknown message", 
                       error=str(e), 
                       message_preview=message_content[:100])
            raise
    
    def start(self):
        """Start the AI Agent service."""
        try:
            self.running = True
            
            logger.info("Starting AI Agent service", 
                       kafka_broker=settings.kafka_broker,
                       security_protocol=settings.kafka_security_protocol,
                       consumer_group=settings.consumer_group)
            
            # Start the web server for health checks
            self.web_server.start()
            
            # Start monitoring Kafka topics
            self.kafka_monitor.start_monitoring()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.stop()
        except Exception as e:
            logger.error("Error starting AI Agent service", error=str(e))
            self.stop()
            sys.exit(1)
    
    def stop(self):
        """Stop the AI Agent service."""
        if self.running:
            logger.info("Stopping AI Agent service...")
            self.running = False
            
            try:
                self.kafka_monitor.stop_monitoring()
            except Exception as e:
                logger.error("Error stopping Kafka monitor", error=str(e))
            
            try:
                self.web_server.stop()
            except Exception as e:
                logger.error("Error stopping web server", error=str(e))
            
            logger.info("AI Agent service stopped")
    
    def health_check(self) -> Dict[str, Any]:
        agent_status = self.ai_agent.get_agent_status()
        
        return {
            "status": "healthy" if self.running else "stopped",
            "service_name": settings.service_name,
            "version": "1.0.0",
            "ai_agent": agent_status,
            "kafka": {
                "broker": settings.kafka_broker,
                "security_protocol": settings.kafka_security_protocol,
                "sasl_mechanism": settings.kafka_sasl_mechanism,
                "consumer_group": settings.consumer_group,
                "monitored_topic": settings.monitored_topic
            }
        }


def main():
    """Main function."""
    # Set up logging level
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
    
    logger.info("Starting ${{ values.name }} AI Agent", 
               version="1.0.0",
               description="${{ values.description }}")
    
    # Create and start the service
    service = AIAgentService()
    
    try:
        service.start()
    except Exception as e:
        logger.error("Failed to start service", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main() 