// MongoDB Initialization Script for Nextier Signal Engine Core
db = db.getSiblingDB('nextier_signal');

// Create collections with schema validation
db.createCollection('articles', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['title', 'content', 'source', 'url', 'scraped_at'],
      properties: {
        title: {
          bsonType: 'string',
          minLength: 3,
          maxLength: 200,
          description: 'Article title'
        },
        content: {
          bsonType: 'string',
          minLength: 10,
          description: 'Article content'
        },
        source: {
          bsonType: 'string',
          minLength: 3,
          maxLength: 50,
          description: 'Source name'
        },
        url: {
          bsonType: 'string',
          description: 'Source URL'
        },
        scraped_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when article was scraped'
        },
        source_credibility: {
          bsonType: 'string',
          enum: ['verified', 'unverified'],
          description: 'Source credibility status'
        },
        processing_status: {
          bsonType: 'string',
          enum: ['pending', 'processed', 'failed'],
          description: 'Processing status of the article'
        },
        error_log: {
          bsonType: 'string',
          description: 'Error log if processing failed'
        }
      }
    }
  }
});

db.createCollection('source_whitelist', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['domain', 'name', 'credibility_score', 'active'],
      properties: {
        domain: {
          bsonType: 'string',
          description: 'Domain name of the source'
        },
        name: {
          bsonType: 'string',
          description: 'Display name of the source'
        },
        credibility_score: {
          bsonType: 'number',
          minimum: 1,
          maximum: 10,
          description: 'Credibility score (1-10)'
        },
        active: {
          bsonType: 'bool',
          description: 'Whether the source is active'
        },
        last_verified: {
          bsonType: 'string',
          description: 'ISO DateTime string when source was last verified'
        }
      }
    }
  }
});

db.createCollection('events', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['event_type', 'state', 'lga', 'severity', 'source_title', 'source_url', 'parsed_at'],
      properties: {
        event_type: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 50,
          description: 'Type of event'
        },
        state: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 50,
          description: 'Nigerian state'
        },
        lga: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 50,
          description: 'Local Government Area'
        },
        severity: {
          bsonType: 'string',
          enum: ['low', 'medium', 'high', 'critical'],
          description: 'Event severity'
        },
        fatalities: {
          bsonType: 'number',
          minimum: 0,
          description: 'Number of fatalities'
        },
        conflict_actor: {
          bsonType: 'string',
          description: 'Actor involved in the conflict'
        },
        source_title: {
          bsonType: 'string',
          minLength: 3,
          maxLength: 200,
          description: 'Title of the source article'
        },
        source_url: {
          bsonType: 'string',
          minLength: 10,
          description: 'URL of the source article'
        },
        parsed_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when event was parsed'
        },
        article_id: {
          bsonType: 'objectId',
          description: 'Reference to article'
        },
        confidence_score: {
          bsonType: 'number',
          minimum: 0,
          maximum: 100,
          description: 'LLM confidence score (0-100)'
        }
      }
    }
  }
});

db.createCollection('digital_sentiment', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['state', 'sentiment_score', 'volume', 'period', 'date'],
      properties: {
        state: {
          bsonType: 'string',
          description: 'Nigerian state'
        },
        lga: {
          bsonType: 'string',
          description: 'Local Government Area (optional)'
        },
        sentiment_score: {
          bsonType: 'number',
          minimum: -1,
          maximum: 1,
          description: 'Sentiment score (-1 to 1)'
        },
        volume: {
          bsonType: 'number',
          minimum: 0,
          description: 'Volume of digital chatter'
        },
        keywords: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'Keywords found in digital chatter'
        },
        period: {
          bsonType: 'string',
          enum: ['daily', 'weekly', 'monthly'],
          description: 'Time period of the sentiment data'
        },
        date: {
          bsonType: 'string',
          description: 'ISO DateTime string for the sentiment data'
        }
      }
    }
  }
});

db.createCollection('risk_signals', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['event_type', 'state', 'lga', 'severity', 'risk_score', 'risk_level', 'source_title', 'source_url', 'calculated_at'],
      properties: {
        event_type: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 50,
          description: 'Type of event'
        },
        state: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 50,
          description: 'Nigerian state'
        },
        lga: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 50,
          description: 'Local Government Area'
        },
        severity: {
          bsonType: 'string',
          enum: ['low', 'medium', 'high', 'critical'],
          description: 'Event severity'
        },
        fatalities: {
          bsonType: 'number',
          minimum: 0,
          description: 'Number of fatalities'
        },
        conflict_actor: {
          bsonType: 'string',
          description: 'Actor involved in the conflict'
        },
        fuel_price: {
          bsonType: 'number',
          minimum: 0,
          description: 'Fuel price'
        },
        inflation: {
          bsonType: 'number',
          minimum: 0,
          description: 'Inflation rate'
        },
        sentiment_score: {
          bsonType: 'number',
          minimum: -1,
          maximum: 1,
          description: 'Digital chatter sentiment score'
        },
        risk_score: {
          bsonType: 'number',
          minimum: 0,
          maximum: 100,
          description: 'Calculated risk score (0-100)'
        },
        risk_level: {
          bsonType: 'string',
          enum: ['Minimal', 'Low', 'Medium', 'High', 'Critical'],
          description: 'Risk level category'
        },
        source_title: {
          bsonType: 'string',
          minLength: 3,
          maxLength: 200,
          description: 'Title of the source article'
        },
        source_url: {
          bsonType: 'string',
          minLength: 10,
          description: 'URL of the source article'
        },
        calculated_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when risk was calculated'
        },
        event_id: {
          bsonType: 'objectId',
          description: 'Reference to event'
        },
        geo_coordinates: {
          bsonType: 'object',
          required: ['type', 'coordinates'],
          properties: {
            type: {
              bsonType: 'string',
              enum: ['Point'],
              description: 'GeoJSON type'
            },
            coordinates: {
              bsonType: 'array',
              minItems: 2,
              maxItems: 2,
              items: {
                bsonType: 'number'
              },
              description: 'Longitude and latitude'
            }
          }
        },
        economic_triggers: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['factor', 'threshold', 'actual_value', 'impact_weight'],
            properties: {
              factor: {
                bsonType: 'string',
                enum: ['inflation', 'fuel_price', 'sentiment'],
                description: 'Economic factor'
              },
              threshold: {
                bsonType: 'number',
                description: 'Threshold value'
              },
              actual_value: {
                bsonType: 'number',
                description: 'Actual value'
              },
              impact_weight: {
                bsonType: 'number',
                minimum: 0,
                maximum: 1,
                description: 'Impact weight (0-1)'
              }
            }
          }
        },
        is_simulation: {
          bsonType: 'bool',
          description: 'Whether this is a simulated risk signal'
        },
        simulation_id: {
          bsonType: 'objectId',
          description: 'Reference to simulation'
        },
        version: {
          bsonType: 'number',
          description: 'Version for optimistic concurrency control'
        }
      }
    }
  }
});

db.createCollection('economic_data', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['state', 'inflation_rate', 'fuel_price', 'updated_at'],
      properties: {
        state: {
          bsonType: 'string',
          description: 'Nigerian state'
        },
        lga: {
          bsonType: 'string',
          description: 'Local Government Area (optional)'
        },
        inflation_rate: {
          bsonType: 'number',
          minimum: 0,
          description: 'Inflation rate'
        },
        fuel_price: {
          bsonType: 'number',
          minimum: 0,
          description: 'Fuel price'
        },
        unemployment_rate: {
          bsonType: 'number',
          minimum: 0,
          description: 'Unemployment rate'
        },
        updated_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when data was updated'
        },
        source: {
          bsonType: 'string',
          description: 'Source of the economic data'
        },
        geo_coordinates: {
          bsonType: 'object',
          required: ['type', 'coordinates'],
          properties: {
            type: {
              bsonType: 'string',
              enum: ['Point'],
              description: 'GeoJSON type'
            },
            coordinates: {
              bsonType: 'array',
              minItems: 2,
              maxItems: 2,
              items: {
                bsonType: 'number'
              },
              description: 'Longitude and latitude'
            }
          }
        }
      }
    }
  }
});

db.createCollection('system_events', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['event_type', 'resource_type', 'resource_id', 'timestamp', 'notification_sent'],
      properties: {
        event_type: {
          bsonType: 'string',
          enum: ['update', 'new', 'delete'],
          description: 'Type of system event'
        },
        resource_type: {
          bsonType: 'string',
          enum: ['risk_signal', 'event', 'article', 'economic_data'],
          description: 'Type of resource'
        },
        resource_id: {
          bsonType: 'objectId',
          description: 'ID of the resource'
        },
        timestamp: {
          bsonType: 'string',
          description: 'ISO DateTime string when event occurred'
        },
        details: {
          bsonType: 'object',
          description: 'Additional details about the event'
        },
        notification_sent: {
          bsonType: 'bool',
          description: 'Whether notification was sent'
        }
      }
    }
  }
});

db.createCollection('simulations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'created_at', 'status', 'parameters'],
      properties: {
        name: {
          bsonType: 'string',
          description: 'Simulation name'
        },
        description: {
          bsonType: 'string',
          description: 'Simulation description'
        },
        created_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when simulation was created'
        },
        created_by: {
          bsonType: 'string',
          description: 'User who created the simulation'
        },
        status: {
          bsonType: 'string',
          enum: ['active', 'completed', 'archived'],
          description: 'Simulation status'
        },
        parameters: {
          bsonType: 'object',
          properties: {
            fuel_price: {
              bsonType: 'number',
              description: 'Simulated fuel price'
            },
            inflation: {
              bsonType: 'number',
              description: 'Simulated inflation rate'
            },
            sentiment_score: {
              bsonType: 'number',
              description: 'Simulated sentiment score'
            },
            other_factors: {
              bsonType: 'object',
              description: 'Other simulation factors'
            }
          }
        },
        affected_states: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'States affected by the simulation'
        },
        affected_lgas: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          },
          description: 'LGAs affected by the simulation'
        },
        baseline_risk_signals: {
          bsonType: 'array',
          items: {
            bsonType: 'objectId'
          },
          description: 'References to original risk signals'
        },
        simulated_risk_signals: {
          bsonType: 'array',
          items: {
            bsonType: 'objectId'
          },
          description: 'References to simulated risk signals'
        },
        results_summary: {
          bsonType: 'object',
          properties: {
            risk_score_changes: {
              bsonType: 'object',
              description: 'Summary of risk score changes'
            },
            hotspots_created: {
              bsonType: 'number',
              description: 'Number of new hotspots created'
            },
            hotspots_resolved: {
              bsonType: 'number',
              description: 'Number of hotspots resolved'
            }
          }
        }
      }
    }
  }
});

db.createCollection('ui_state', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'session_id', 'last_viewed_at'],
      properties: {
        user_id: {
          bsonType: 'string',
          description: 'User ID'
        },
        session_id: {
          bsonType: 'string',
          description: 'Session ID'
        },
        last_viewed_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when user last viewed'
        },
        filters: {
          bsonType: 'object',
          properties: {
            states: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Filtered states'
            },
            lgas: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Filtered LGAs'
            },
            risk_levels: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Filtered risk levels'
            },
            event_types: {
              bsonType: 'array',
              items: {
                bsonType: 'string'
              },
              description: 'Filtered event types'
            },
            date_range: {
              bsonType: 'object',
              properties: {
                start: {
                  bsonType: 'string',
                  description: 'Start date'
                },
                end: {
                  bsonType: 'string',
                  description: 'End date'
                }
              }
            }
          }
        },
        map_view: {
          bsonType: 'object',
          properties: {
            center: {
              bsonType: 'array',
              minItems: 2,
              maxItems: 2,
              items: {
                bsonType: 'number'
              },
              description: 'Map center coordinates'
            },
            zoom: {
              bsonType: 'number',
              description: 'Map zoom level'
            }
          }
        },
        active_simulation_id: {
          bsonType: 'objectId',
          description: 'Active simulation ID'
        },
        last_notification_id: {
          bsonType: 'objectId',
          description: 'Last notification ID'
        }
      }
    }
  }
});

db.createCollection('system_configuration', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['config_key', 'config_value', 'updated_at'],
      properties: {
        config_key: {
          bsonType: 'string',
          description: 'Configuration key'
        },
        config_value: {
          description: 'Configuration value (any type)'
        },
        description: {
          bsonType: 'string',
          description: 'Configuration description'
        },
        updated_at: {
          bsonType: 'string',
          description: 'ISO DateTime string when configuration was updated'
        },
        updated_by: {
          bsonType: 'string',
          description: 'User who updated the configuration'
        }
      }
    }
  }
});

// Create indexes
db.articles.createIndex({ url: 1 }, { unique: true });
db.articles.createIndex({ scraped_at: 1 });
db.articles.createIndex({ source: 1 });
db.articles.createIndex({ processing_status: 1 });

db.source_whitelist.createIndex({ domain: 1 }, { unique: true });
db.source_whitelist.createIndex({ active: 1 });

db.events.createIndex({ state: 1, lga: 1 });
db.events.createIndex({ event_type: 1 });
db.events.createIndex({ severity: 1 });
db.events.createIndex({ parsed_at: 1 });
db.events.createIndex({ article_id: 1 });

db.digital_sentiment.createIndex({ state: 1, lga: 1, date: 1 });
db.digital_sentiment.createIndex({ period: 1, date: 1 });

db.risk_signals.createIndex({ state: 1, lga: 1 });
db.risk_signals.createIndex({ risk_level: 1 });
db.risk_signals.createIndex({ calculated_at: 1 });
db.risk_signals.createIndex({ event_id: 1 });
db.risk_signals.createIndex({ is_simulation: 1 });
db.risk_signals.createIndex({ simulation_id: 1 });
db.risk_signals.createIndex({ geo_coordinates: "2dsphere" });

db.economic_data.createIndex({ state: 1, lga: 1 }, { unique: true });
db.economic_data.createIndex({ updated_at: 1 });
db.economic_data.createIndex({ geo_coordinates: "2dsphere" });

db.system_events.createIndex({ timestamp: 1 });
db.system_events.createIndex({ resource_type: 1, resource_id: 1 });
db.system_events.createIndex({ notification_sent: 1 });

db.simulations.createIndex({ status: 1 });
db.simulations.createIndex({ created_at: 1 });

db.ui_state.createIndex({ user_id: 1, session_id: 1 }, { unique: true });
db.ui_state.createIndex({ last_viewed_at: 1 });

db.system_configuration.createIndex({ config_key: 1 }, { unique: true });
