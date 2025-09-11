"""Configuration settings for the AI Agent."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service Configuration
    service_name: str = Field(default="${{ values.name }}", description="Service name")
    service_description: str = Field(
        default="${{ values.description }}", 
        description="Service description"
    )
    log_level: str = Field(default="DEBUG", description="Logging level")
    
    # Kafka Configuration
    kafka_broker: str = Field(
        default="kafka-kafka-bootstrap.kafka.svc.cluster.local:9092", 
        description="Kafka broker address"
    )
    kafka_security_protocol: str = Field(
        default="SASL_SSL",
        description="Kafka security protocol"
    )
    kafka_sasl_mechanism: str = Field(
        default="SCRAM-SHA-512",
        description="Kafka SASL mechanism"
    )
    kafka_sasl_username: str = Field(
        default="parasol",
        description="Kafka SASL username"
    )
    kafka_sasl_password: str = Field(
        default="parasol",
        description="Kafka SASL password"
    )
    consumer_group: str = Field(
        default="${{ values.consumerGroup }}", 
        description="Kafka consumer group ID"
    )
    monitored_topic: str = Field(
        default="${{ values.kafkaTopicName }}", 
        description="Kafka topic to monitor (extracted from entity annotation)"
    )
    kafka_auto_offset_reset: str = Field(
        default="latest", 
        description="Kafka consumer offset reset strategy"
    )
    
    # AI Configuration
    ai_model: str = Field(
        default="${{ values.aiModel }}", 
        description="AI model resource to use"
    )
    inference_server_url: str = Field(
        default="${{ values.inferenceServerUrl }}", 
        description="Inference server URL for the AI model"
    )

    ai_temperature: float = Field(default=0.3, description="AI model temperature")
    ai_max_tokens: int = Field(default=500, description="Maximum tokens for AI response")
    
    # Backstage Configuration
    backstage_api_url: str = Field(
        default="http://backstage-internal.backstage.svc.cluster.local/api", 
        description="Backstage API base URL"
    )
    backstage_token: str = Field(
        default="", 
        description="Backstage API authentication token"
    )
    notification_title: str = Field(
        default="Message Routing Failure Detected", 
        description="Default notification title"
    )
    notification_recipient_entity: str = Field(
        default="${{ values.owner }}", 
        description="Entity reference for notification recipients"
    )
    
    # Health and Monitoring
    health_check_port: int = Field(default=8080, description="Health check server port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def kafka_broker_list(self) -> List[str]:
        """Return Kafka broker as a list for compatibility."""
        return [self.kafka_broker]


# Global settings instance
settings = Settings() 