#!/bin/bash
# RabbitMQ Initialization Script for Nextier Signal Engine Core

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ to be ready..."
until rabbitmqctl status; do
  sleep 2
done

# Create queues
echo "Creating RabbitMQ queues..."
rabbitmqadmin declare queue name=scraped_articles durable=true
rabbitmqadmin declare queue name=parsed_events durable=true
rabbitmqadmin declare queue name=risk_signals durable=true

# Create exchanges
echo "Creating RabbitMQ exchanges..."
rabbitmqadmin declare exchange name=nextier_exchange type=topic durable=true

# Create bindings
echo "Creating RabbitMQ bindings..."
rabbitmqadmin declare binding source=nextier_exchange destination=scraped_articles routing_key=articles.new
rabbitmqadmin declare binding source=nextier_exchange destination=parsed_events routing_key=events.new
rabbitmqadmin declare binding source=nextier_exchange destination=risk_signals routing_key=signals.new

# Set permissions
echo "Setting RabbitMQ permissions..."
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

echo "RabbitMQ initialization completed!"
