// Sample Data for Nextier Signal Engine Core
db = db.getSiblingDB('nextier_signal');

// Clear existing data
db.articles.deleteMany({});
db.source_whitelist.deleteMany({});
db.events.deleteMany({});
db.digital_sentiment.deleteMany({});
db.risk_signals.deleteMany({});
db.economic_data.deleteMany({});
db.system_events.deleteMany({});
db.simulations.deleteMany({});
db.ui_state.deleteMany({});
db.system_configuration.deleteMany({});

// Insert source whitelist
db.source_whitelist.insertMany([
  {
    domain: 'premiumtimesng.com',
    name: 'Premium Times Nigeria',
    credibility_score: 9,
    active: true,
    last_verified: new Date().toISOString()
  },
  {
    domain: 'thecable.ng',
    name: 'The Cable',
    credibility_score: 8,
    active: true,
    last_verified: new Date().toISOString()
  },
  {
    domain: 'punchng.com',
    name: 'Punch Nigeria',
    credibility_score: 8,
    active: true,
    last_verified: new Date().toISOString()
  },
  {
    domain: 'vanguardngr.com',
    name: 'Vanguard Nigeria',
    credibility_score: 7,
    active: true,
    last_verified: new Date().toISOString()
  },
  {
    domain: 'dailytrust.com',
    name: 'Daily Trust',
    credibility_score: 7,
    active: true,
    last_verified: new Date().toISOString()
  }
]);

// Insert articles
const articleIds = [];
const articles = [
  {
    title: "Gunmen kill 5 in Borno village attack",
    content: "At least five people were killed when gunmen suspected to be members of Boko Haram attacked a village in Borno State on Monday night. The attack happened in Gwoza local government area, according to security sources. Residents fled into the mountains as the attackers burned down several houses.",
    source: "premiumtimesng.com",
    url: "https://www.premiumtimesng.com/news/headlines/123456-gunmen-kill-5-in-borno-village-attack.html",
    scraped_at: new Date().toISOString(),
    source_credibility: "verified",
    processing_status: "processed"
  },
  {
    title: "Protesters block Lagos-Ibadan expressway over fuel price hike",
    content: "Hundreds of protesters blocked the Lagos-Ibadan expressway on Tuesday morning, causing a massive traffic jam as they demonstrated against the recent increase in fuel prices. The protest, which began at around 7am, saw demonstrators carrying placards with messages condemning the government's decision to remove fuel subsidies.",
    source: "thecable.ng",
    url: "https://www.thecable.ng/protesters-block-lagos-ibadan-expressway-over-fuel-price-hike",
    scraped_at: new Date().toISOString(),
    source_credibility: "verified",
    processing_status: "processed"
  },
  {
    title: "Farmers-herders clash leaves 12 dead in Benue",
    content: "A violent clash between farmers and herders in Benue State has resulted in at least 12 deaths, according to local authorities. The incident occurred in Guma local government area, where a long-standing conflict over land use has persisted. The state governor has called for calm and promised to bring the perpetrators to justice.",
    source: "punchng.com",
    url: "https://punchng.com/farmers-herders-clash-leaves-12-dead-in-benue",
    scraped_at: new Date().toISOString(),
    source_credibility: "verified",
    processing_status: "processed"
  },
  {
    title: "Armed bandits kidnap 30 students in Kaduna school raid",
    content: "Armed bandits have kidnapped approximately 30 students from a secondary school in Kaduna State, according to police reports. The attack occurred in the early hours of Wednesday at a boarding school in Chikun local government area. Security forces have been deployed to rescue the students.",
    source: "vanguardngr.com",
    url: "https://www.vanguardngr.com/2023/armed-bandits-kidnap-30-students-in-kaduna-school-raid",
    scraped_at: new Date().toISOString(),
    source_credibility: "verified",
    processing_status: "processed"
  },
  {
    title: "Oil pipeline vandalism causes spill in Rivers community",
    content: "A major oil spill has been reported in a community in Rivers State following an act of pipeline vandalism. The incident, which occurred in Ogoni land, has contaminated farmlands and water sources, affecting thousands of residents. The oil company responsible for the pipeline has dispatched a team to contain the spill.",
    source: "dailytrust.com",
    url: "https://dailytrust.com/oil-pipeline-vandalism-causes-spill-in-rivers-community",
    scraped_at: new Date().toISOString(),
    source_credibility: "verified",
    processing_status: "processed"
  }
];

articles.forEach(article => {
  const result = db.articles.insertOne(article);
  articleIds.push(result.insertedId);
});

// Insert events
const eventIds = [];
const events = [
  {
    event_type: "attack",
    state: "Borno",
    lga: "Gwoza",
    severity: "high",
    fatalities: 5,
    conflict_actor: "Boko Haram",
    source_title: "Gunmen kill 5 in Borno village attack",
    source_url: "https://www.premiumtimesng.com/news/headlines/123456-gunmen-kill-5-in-borno-village-attack.html",
    parsed_at: new Date().toISOString(),
    article_id: articleIds[0],
    confidence_score: 85
  },
  {
    event_type: "protest",
    state: "Lagos",
    lga: "Ikeja",
    severity: "medium",
    fatalities: 0,
    conflict_actor: "Civilian protesters",
    source_title: "Protesters block Lagos-Ibadan expressway over fuel price hike",
    source_url: "https://www.thecable.ng/protesters-block-lagos-ibadan-expressway-over-fuel-price-hike",
    parsed_at: new Date().toISOString(),
    article_id: articleIds[1],
    confidence_score: 90
  },
  {
    event_type: "clash",
    state: "Benue",
    lga: "Guma",
    severity: "critical",
    fatalities: 12,
    conflict_actor: "Farmers and herders",
    source_title: "Farmers-herders clash leaves 12 dead in Benue",
    source_url: "https://punchng.com/farmers-herders-clash-leaves-12-dead-in-benue",
    parsed_at: new Date().toISOString(),
    article_id: articleIds[2],
    confidence_score: 95
  },
  {
    event_type: "kidnapping",
    state: "Kaduna",
    lga: "Chikun",
    severity: "high",
    fatalities: 0,
    conflict_actor: "Bandits",
    source_title: "Armed bandits kidnap 30 students in Kaduna school raid",
    source_url: "https://www.vanguardngr.com/2023/armed-bandits-kidnap-30-students-in-kaduna-school-raid",
    parsed_at: new Date().toISOString(),
    article_id: articleIds[3],
    confidence_score: 88
  },
  {
    event_type: "vandalism",
    state: "Rivers",
    lga: "Khana",
    severity: "medium",
    fatalities: 0,
    conflict_actor: "Unknown vandals",
    source_title: "Oil pipeline vandalism causes spill in Rivers community",
    source_url: "https://dailytrust.com/oil-pipeline-vandalism-causes-spill-in-rivers-community",
    parsed_at: new Date().toISOString(),
    article_id: articleIds[4],
    confidence_score: 80
  }
];

events.forEach(event => {
  const result = db.events.insertOne(event);
  eventIds.push(result.insertedId);
});

// Insert economic data
db.economic_data.insertMany([
  {
    state: "Borno",
    lga: "Gwoza",
    inflation_rate: 25.8,
    fuel_price: 700,
    unemployment_rate: 35.2,
    updated_at: new Date().toISOString(),
    source: "National Bureau of Statistics",
    geo_coordinates: {
      type: "Point",
      coordinates: [13.6894, 10.9758]
    }
  },
  {
    state: "Lagos",
    lga: "Ikeja",
    inflation_rate: 22.5,
    fuel_price: 650,
    unemployment_rate: 19.8,
    updated_at: new Date().toISOString(),
    source: "National Bureau of Statistics",
    geo_coordinates: {
      type: "Point",
      coordinates: [3.3792, 6.6018]
    }
  },
  {
    state: "Benue",
    lga: "Guma",
    inflation_rate: 26.2,
    fuel_price: 680,
    unemployment_rate: 32.5,
    updated_at: new Date().toISOString(),
    source: "National Bureau of Statistics",
    geo_coordinates: {
      type: "Point",
      coordinates: [8.5922, 7.8781]
    }
  },
  {
    state: "Kaduna",
    lga: "Chikun",
    inflation_rate: 24.7,
    fuel_price: 670,
    unemployment_rate: 29.3,
    updated_at: new Date().toISOString(),
    source: "National Bureau of Statistics",
    geo_coordinates: {
      type: "Point",
      coordinates: [7.4162, 10.4219]
    }
  },
  {
    state: "Rivers",
    lga: "Khana",
    inflation_rate: 23.9,
    fuel_price: 660,
    unemployment_rate: 27.1,
    updated_at: new Date().toISOString(),
    source: "National Bureau of Statistics",
    geo_coordinates: {
      type: "Point",
      coordinates: [7.3878, 4.6472]
    }
  }
]);

// Insert digital sentiment
db.digital_sentiment.insertMany([
  {
    state: "Borno",
    lga: "Gwoza",
    sentiment_score: -0.8,
    volume: 1250,
    keywords: ["attack", "Boko Haram", "insecurity", "violence"],
    period: "daily",
    date: new Date().toISOString()
  },
  {
    state: "Lagos",
    lga: "Ikeja",
    sentiment_score: -0.6,
    volume: 3500,
    keywords: ["protest", "fuel price", "subsidy removal", "hardship"],
    period: "daily",
    date: new Date().toISOString()
  },
  {
    state: "Benue",
    lga: "Guma",
    sentiment_score: -0.9,
    volume: 2100,
    keywords: ["farmers", "herders", "clash", "killings", "conflict"],
    period: "daily",
    date: new Date().toISOString()
  },
  {
    state: "Kaduna",
    lga: "Chikun",
    sentiment_score: -0.7,
    volume: 2800,
    keywords: ["kidnapping", "bandits", "students", "ransom", "security"],
    period: "daily",
    date: new Date().toISOString()
  },
  {
    state: "Rivers",
    lga: "Khana",
    sentiment_score: -0.5,
    volume: 1800,
    keywords: ["oil spill", "vandalism", "pollution", "environment"],
    period: "daily",
    date: new Date().toISOString()
  }
]);

// Insert risk signals
db.risk_signals.insertMany([
  {
    event_type: "attack",
    state: "Borno",
    lga: "Gwoza",
    severity: "high",
    fatalities: 5,
    conflict_actor: "Boko Haram",
    fuel_price: 700,
    inflation: 25.8,
    sentiment_score: -0.8,
    risk_score: 85,
    risk_level: "Critical",
    source_title: "Gunmen kill 5 in Borno village attack",
    source_url: "https://www.premiumtimesng.com/news/headlines/123456-gunmen-kill-5-in-borno-village-attack.html",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[0],
    geo_coordinates: {
      type: "Point",
      coordinates: [13.6894, 10.9758]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 25.8,
        impact_weight: 0.4
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 700,
        impact_weight: 0.3
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.8,
        impact_weight: 0.3
      }
    ],
    is_simulation: false,
    version: 1
  },
  {
    event_type: "protest",
    state: "Lagos",
    lga: "Ikeja",
    severity: "medium",
    fatalities: 0,
    conflict_actor: "Civilian protesters",
    fuel_price: 650,
    inflation: 22.5,
    sentiment_score: -0.6,
    risk_score: 65,
    risk_level: "High",
    source_title: "Protesters block Lagos-Ibadan expressway over fuel price hike",
    source_url: "https://www.thecable.ng/protesters-block-lagos-ibadan-expressway-over-fuel-price-hike",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[1],
    geo_coordinates: {
      type: "Point",
      coordinates: [3.3792, 6.6018]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 22.5,
        impact_weight: 0.3
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 650,
        impact_weight: 0.5
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.6,
        impact_weight: 0.2
      }
    ],
    is_simulation: false,
    version: 1
  },
  {
    event_type: "clash",
    state: "Benue",
    lga: "Guma",
    severity: "critical",
    fatalities: 12,
    conflict_actor: "Farmers and herders",
    fuel_price: 680,
    inflation: 26.2,
    sentiment_score: -0.9,
    risk_score: 90,
    risk_level: "Critical",
    source_title: "Farmers-herders clash leaves 12 dead in Benue",
    source_url: "https://punchng.com/farmers-herders-clash-leaves-12-dead-in-benue",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[2],
    geo_coordinates: {
      type: "Point",
      coordinates: [8.5922, 7.8781]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 26.2,
        impact_weight: 0.3
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 680,
        impact_weight: 0.2
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.9,
        impact_weight: 0.5
      }
    ],
    is_simulation: false,
    version: 1
  },
  {
    event_type: "kidnapping",
    state: "Kaduna",
    lga: "Chikun",
    severity: "high",
    fatalities: 0,
    conflict_actor: "Bandits",
    fuel_price: 670,
    inflation: 24.7,
    sentiment_score: -0.7,
    risk_score: 75,
    risk_level: "High",
    source_title: "Armed bandits kidnap 30 students in Kaduna school raid",
    source_url: "https://www.vanguardngr.com/2023/armed-bandits-kidnap-30-students-in-kaduna-school-raid",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[3],
    geo_coordinates: {
      type: "Point",
      coordinates: [7.4162, 10.4219]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 24.7,
        impact_weight: 0.3
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 670,
        impact_weight: 0.3
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.7,
        impact_weight: 0.4
      }
    ],
    is_simulation: false,
    version: 1
  },
  {
    event_type: "vandalism",
    state: "Rivers",
    lga: "Khana",
    severity: "medium",
    fatalities: 0,
    conflict_actor: "Unknown vandals",
    fuel_price: 660,
    inflation: 23.9,
    sentiment_score: -0.5,
    risk_score: 55,
    risk_level: "Medium",
    source_title: "Oil pipeline vandalism causes spill in Rivers community",
    source_url: "https://dailytrust.com/oil-pipeline-vandalism-causes-spill-in-rivers-community",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[4],
    geo_coordinates: {
      type: "Point",
      coordinates: [7.3878, 4.6472]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 23.9,
        impact_weight: 0.3
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 660,
        impact_weight: 0.3
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.5,
        impact_weight: 0.4
      }
    ],
    is_simulation: false,
    version: 1
  }
]);

// Insert a simulation
const simulationId = db.simulations.insertOne({
  name: "Fuel Price Spike Simulation",
  description: "Simulating the impact of a major fuel price increase to 1200 NGN",
  created_at: new Date().toISOString(),
  created_by: "admin",
  status: "completed",
  parameters: {
    fuel_price: 1200,
    inflation: null,
    sentiment_score: null
  },
  affected_states: ["Lagos", "Rivers", "Benue", "Kaduna", "Borno"],
  affected_lgas: [],
  baseline_risk_signals: [eventIds[0], eventIds[1], eventIds[2], eventIds[3], eventIds[4]],
  simulated_risk_signals: [],
  results_summary: {
    risk_score_changes: {
      "Lagos": 15,
      "Rivers": 10,
      "Benue": 8,
      "Kaduna": 12,
      "Borno": 5
    },
    hotspots_created: 2,
    hotspots_resolved: 0
  }
}).insertedId;

// Insert simulated risk signals
const simulatedRiskSignals = [
  {
    event_type: "protest",
    state: "Lagos",
    lga: "Ikeja",
    severity: "high", // Increased from medium
    fatalities: 0,
    conflict_actor: "Civilian protesters",
    fuel_price: 1200, // Simulated value
    inflation: 22.5,
    sentiment_score: -0.8, // Worsened
    risk_score: 80, // Increased from 65
    risk_level: "High",
    source_title: "Protesters block Lagos-Ibadan expressway over fuel price hike",
    source_url: "https://www.thecable.ng/protesters-block-lagos-ibadan-expressway-over-fuel-price-hike",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[1],
    geo_coordinates: {
      type: "Point",
      coordinates: [3.3792, 6.6018]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 22.5,
        impact_weight: 0.2
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 1200, // Simulated value
        impact_weight: 0.6
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.8, // Worsened
        impact_weight: 0.2
      }
    ],
    is_simulation: true,
    simulation_id: simulationId,
    version: 1
  },
  {
    event_type: "vandalism",
    state: "Rivers",
    lga: "Khana",
    severity: "high", // Increased from medium
    fatalities: 0,
    conflict_actor: "Unknown vandals",
    fuel_price: 1200, // Simulated value
    inflation: 23.9,
    sentiment_score: -0.7, // Worsened
    risk_score: 70, // Increased from 55
    risk_level: "High", // Increased from Medium
    source_title: "Oil pipeline vandalism causes spill in Rivers community",
    source_url: "https://dailytrust.com/oil-pipeline-vandalism-causes-spill-in-rivers-community",
    calculated_at: new Date().toISOString(),
    event_id: eventIds[4],
    geo_coordinates: {
      type: "Point",
      coordinates: [7.3878, 4.6472]
    },
    economic_triggers: [
      {
        factor: "inflation",
        threshold: 20,
        actual_value: 23.9,
        impact_weight: 0.2
      },
      {
        factor: "fuel_price",
        threshold: 650,
        actual_value: 1200, // Simulated value
        impact_weight: 0.6
      },
      {
        factor: "sentiment",
        threshold: -0.6,
        actual_value: -0.7, // Worsened
        impact_weight: 0.2
      }
    ],
    is_simulation: true,
    simulation_id: simulationId,
    version: 1
  }
];

const simulatedIds = [];
simulatedRiskSignals.forEach(signal => {
  const result = db.risk_signals.insertOne(signal);
  simulatedIds.push(result.insertedId);
});

// Update simulation with simulated risk signal IDs
db.simulations.updateOne(
  { _id: simulationId },
  { $set: { simulated_risk_signals: simulatedIds } }
);

// Insert system events
db.system_events.insertMany([
  {
    event_type: "new",
    resource_type: "risk_signal",
    resource_id: eventIds[0],
    timestamp: new Date().toISOString(),
    details: {
      risk_level: "Critical",
      state: "Borno",
      lga: "Gwoza"
    },
    notification_sent: true
  },
  {
    event_type: "new",
    resource_type: "risk_signal",
    resource_id: eventIds[1],
    timestamp: new Date().toISOString(),
    details: {
      risk_level: "High",
      state: "Lagos",
      lga: "Ikeja"
    },
    notification_sent: true
  },
  {
    event_type: "new",
    resource_type: "risk_signal",
    resource_id: eventIds[2],
    timestamp: new Date().toISOString(),
    details: {
      risk_level: "Critical",
      state: "Benue",
      lga: "Guma"
    },
    notification_sent: true
  }
]);

// Insert UI state
db.ui_state.insertOne({
  user_id: "admin",
  session_id: "session_123456",
  last_viewed_at: new Date().toISOString(),
  filters: {
    states: ["Borno", "Lagos", "Benue"],
    lgas: [],
    risk_levels: ["High", "Critical"],
    event_types: ["attack", "protest", "clash"],
    date_range: {
      start: new Date(new Date().setDate(new Date().getDate() - 7)).toISOString(),
      end: new Date().toISOString()
    }
  },
  map_view: {
    center: [8.6753, 9.0820], // Center of Nigeria
    zoom: 6
  },
  active_simulation_id: null,
  last_notification_id: null
});

// Insert system configuration
db.system_configuration.insertMany([
  {
    config_key: "risk_score_thresholds",
    config_value: {
      "Minimal": 0,
      "Low": 30,
      "Medium": 50,
      "High": 70,
      "Critical": 85
    },
    description: "Risk score thresholds for risk levels",
    updated_at: new Date().toISOString(),
    updated_by: "system"
  },
  {
    config_key: "risk_factor_weights",
    config_value: {
      "event_severity": 0.3,
      "fatalities": 0.2,
      "inflation": 0.15,
      "fuel_price": 0.15,
      "sentiment": 0.2
    },
    description: "Weights for different risk factors",
    updated_at: new Date().toISOString(),
    updated_by: "system"
  },
  {
    config_key: "economic_thresholds",
    config_value: {
      "inflation": {
        "warning": 18,
        "critical": 25
      },
      "fuel_price": {
        "warning": 650,
        "critical": 800
      }
    },
    description: "Thresholds for economic indicators",
    updated_at: new Date().toISOString(),
    updated_by: "system"
  },
  {
    config_key: "refresh_interval",
    config_value: 30,
    description: "Dashboard refresh interval in seconds",
    updated_at: new Date().toISOString(),
    updated_by: "system"
  },
  {
    config_key: "allowed_sources",
    config_value: ["premiumtimesng.com", "thecable.ng", "punchng.com", "vanguardngr.com", "dailytrust.com"],
    description: "Allowed news sources",
    updated_at: new Date().toISOString(),
    updated_by: "system"
  }
]);
