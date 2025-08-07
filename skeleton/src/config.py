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
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Kafka Configuration
    kafka_brokers: str = Field(
        default="kafka-kafka-bootstrap.kafka.svc.cluster.local:9092", 
        description="Comma-separated Kafka broker addresses"
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
    openai_api_key: str = Field(
        default="", 
        description="OpenAI API key (set via environment variable)"
    )
    ai_model: str = Field(
        default="${{ values.aiModel }}", 
        description="AI model resource to use"
    )
    analysis_prompt_template: str = Field(
        default="""{%- if values.analysisPrompt %}{{ values.analysisPrompt | replace('\n', '\\n') }}{% else %}You are an expert system analyst reviewing a message that failed to be routed properly.

Analyze the following message and determine the most likely cause of the routing failure:

Message: {message}

Consider these common failure causes:
1. Ambiguous intent - message could fit multiple categories
2. Missing context - insufficient information to classify
3. New domain - message relates to a domain not covered by existing categories
4. Technical format issues - message format or encoding problems
5. Language barriers - non-English or unclear language

Provide a brief analysis and suggested resolution.{% endif %}""",
        description="Prompt template for AI analysis"
    )
    ai_temperature: float = Field(default=0.3, description="AI model temperature")
    ai_max_tokens: int = Field(default=500, description="Maximum tokens for AI response")
    
    # Backstage Configuration
    backstage_api_url: str = Field(
        default="http://localhost:7007/api", 
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
    
    # Health and Monitoring
    health_check_port: int = Field(default=8080, description="Health check server port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def kafka_broker_list(self) -> List[str]:
        """Parse Kafka brokers into a list."""
        return [broker.strip() for broker in self.kafka_brokers.split(",")]


# Global settings instance
settings = Settings() 