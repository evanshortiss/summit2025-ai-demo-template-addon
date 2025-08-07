#!/usr/bin/env python3
"""Simple web server for health checks and status endpoints."""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional

import structlog

logger = structlog.get_logger()


class HealthRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health and status endpoints."""
    
    def __init__(self, service_instance, *args, **kwargs):
        self.service_instance = service_instance
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self._handle_health()
        elif self.path == '/status':
            self._handle_status()
        else:
            self._handle_not_found()
    
    def _handle_health(self):
        """Handle health check requests."""
        try:
            health_data = self.service_instance.health_check()
            status_code = 200 if health_data.get("status") == "healthy" else 503
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = json.dumps(health_data, indent=2)
            self.wfile.write(response.encode())
            
        except Exception as e:
            logger.error("Error handling health check", error=str(e))
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            error_response = json.dumps({"status": "error", "message": str(e)})
            self.wfile.write(error_response.encode())
    
    def _handle_status(self):
        """Handle status requests (alias for health)."""
        self._handle_health()
    
    def _handle_not_found(self):
        """Handle 404 responses."""
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = json.dumps({"error": "Not found", "path": self.path})
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override to use structured logging."""
        logger.info("HTTP request", 
                   method=self.command,
                   path=self.path,
                   status=format % args)


class WebServer:
    """Simple web server for health checks."""
    
    def __init__(self, service_instance, port: int = 8080, host: str = '0.0.0.0'):
        """Initialize the web server."""
        self.service_instance = service_instance
        self.port = port
        self.host = host
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
    
    def start(self):
        """Start the web server."""
        try:
            # Create a handler class that has access to our service instance
            def handler_factory(*args, **kwargs):
                return HealthRequestHandler(self.service_instance, *args, **kwargs)
            
            self.server = HTTPServer((self.host, self.port), handler_factory)
            self.running = True
            
            logger.info("Starting web server", host=self.host, port=self.port)
            
            # Run server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info("Web server started successfully")
            
        except Exception as e:
            logger.error("Failed to start web server", error=str(e))
            raise
    
    def stop(self):
        """Stop the web server."""
        if self.running and self.server:
            logger.info("Stopping web server...")
            self.running = False
            self.server.shutdown()
            self.server.server_close()
            
            if self.server_thread:
                self.server_thread.join(timeout=5)
            
            logger.info("Web server stopped")