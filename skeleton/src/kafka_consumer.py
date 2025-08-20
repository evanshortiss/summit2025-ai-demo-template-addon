"""Kafka consumer for monitoring message topics."""

import json
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from .config import settings

logger = logging.getLogger(__name__)


@dataclass
class KafkaMessage:
    """Represents a Kafka message with metadata."""
    
    topic: str
    partition: int
    offset: int
    key: Optional[str]
    value: str
    timestamp: int
    headers: Dict[str, Any]


class MessageProcessor:
    """Handles processing of Kafka messages."""
    
    def __init__(self, message_handler: Callable[[KafkaMessage], None]):
        """Initialize the message processor.
        
        Args:
            message_handler: Function to call when a message is received
        """
        self.message_handler = message_handler
        self.consumer: Optional[KafkaConsumer] = None
        self.running = False
    
    def create_consumer(self) -> KafkaConsumer:
        """Create and configure the Kafka consumer."""
        consumer_config = {
            'bootstrap_servers': settings.kafka_broker_list,
            'group_id': settings.consumer_group,
            'auto_offset_reset': settings.kafka_auto_offset_reset,
            'enable_auto_commit': True,
            'auto_commit_interval_ms': 1000,
            'value_deserializer': lambda m: m.decode('utf-8') if m else None,
            'key_deserializer': lambda m: m.decode('utf-8') if m else None,
            'security_protocol': settings.kafka_security_protocol,
            'sasl_mechanism': settings.kafka_sasl_mechanism,
            'sasl_plain_username': settings.kafka_sasl_username,
            'sasl_plain_password': settings.kafka_sasl_password,
        }
        
        logger.info(f"Creating Kafka consumer with config: {consumer_config}")
        consumer = KafkaConsumer(**consumer_config)
        
        # Subscribe to topic
        logger.info(f"Subscribing to topic: {settings.monitored_topic}")
        consumer.subscribe([settings.monitored_topic])
        
        return consumer
    
    def start_consuming(self) -> None:
        try:
            self.consumer = self.create_consumer()
            self.running = True
            
            logger.info("Starting Kafka message consumption...")
            
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    # Convert Kafka message to our internal format
                    kafka_msg = KafkaMessage(
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        key=message.key,
                        value=message.value,
                        timestamp=message.timestamp,
                        headers=dict(message.headers) if message.headers else {}
                    )
                    
                    logger.info(f"Received message from {message.topic}: {message.value}...")
                    
                    # Process the message
                    self.message_handler(kafka_msg)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    continue
                    
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in consumer: {e}")
            raise
        finally:
            self.stop_consuming()
    
    def stop_consuming(self) -> None:
        """Stop consuming messages and close the consumer."""
        logger.info("Stopping Kafka consumer...")
        self.running = False
        
        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                logger.error(f"Error closing Kafka consumer: {e}")
            finally:
                self.consumer = None


class UnknownTopicMonitor:
    """Specialized monitor for the configured monitored topic."""
    
    def __init__(self, ai_agent_callback: Callable[[str, Dict[str, Any]], None]):
        """Initialize the topic monitor.
        
        Args:
            ai_agent_callback: Function to call when a message is detected on the monitored topic
        """
        self.ai_agent_callback = ai_agent_callback
        self.message_processor = MessageProcessor(self._handle_message)
    
    def _handle_message(self, message: KafkaMessage) -> None:
        """Handle messages from the monitored topic."""
        if message.topic == settings.monitored_topic:
            logger.info(f"Message detected on monitored topic '{message.topic}': {message.value[:100]}...")
            
            # Extract metadata
            metadata = {
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "timestamp": message.timestamp,
                "headers": message.headers,
                "key": message.key
            }
            
            # Call the AI agent to analyze the message
            self.ai_agent_callback(message.value, metadata)
        else:
            logger.debug(f"Ignoring message from topic: {message.topic} (not monitoring this topic)")
    
    def start_monitoring(self) -> None:
        logger.info(f"Starting topic monitor for '{settings.monitored_topic}'...")
        self.message_processor.start_consuming()
    
    def stop_monitoring(self) -> None:
        logger.info("Stopping topic monitor...")
        self.message_processor.stop_consuming() 