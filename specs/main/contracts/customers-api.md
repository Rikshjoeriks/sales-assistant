# API Contract: Customer Management

**Endpoint**: `/api/v1/customers`  
**Purpose**: Manage customer profiles and interaction history  
**Authentication**: API Key required

## POST /api/v1/customers

Create a new customer profile.

### Request
```http
POST /api/v1/customers
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "name": "John Smith",
  "demographics": {
    "age": 35,
    "profession": "Software Engineer", 
    "location": "Seattle, WA",
    "income_range": "75k_100k"
  },
  "personality_assessment": {
    "type": "D",
    "confidence": 0.78,
    "assessment_method": "conversation_analysis|survey|manual"
  },
  "communication_preferences": {
    "style": "direct",
    "preferred_channels": ["email", "phone"],
    "response_time_expectation": "same_day"
  },
  "decision_factors": {
    "primary": ["performance", "safety", "value"],
    "secondary": ["brand_reputation", "fuel_efficiency"],
    "deal_breakers": ["poor_reliability"]
  },
  "buying_context": {
    "budget_range": "40k_60k",
    "timeline": "within_3_months",
    "financing_preference": "lease|finance|cash",
    "trade_in_vehicle": "2018 Honda Civic"
  }
}
```

### Response Success (201 Created)
```json
{
  "id": "customer-uuid-123",
  "name": "John Smith", 
  "profile_completeness": 0.85,
  "personality_type": "D",
  "created_at": "2025-09-24T10:30:00Z",
  "recommendation_readiness": true,
  "profile_summary": {
    "key_traits": ["direct_communicator", "performance_focused", "value_conscious"],
    "optimal_sales_approach": "facts_and_benefits",
    "potential_objections": ["price_sensitivity", "decision_timeline"]
  }
}
```

### Response Error (400 Bad Request)
```json
{
  "error": "validation_failed",
  "message": "Invalid personality type specified",
  "details": {
    "field": "personality_assessment.type",
    "allowed_values": ["D", "I", "S", "C"],
    "received_value": "X"
  }
}
```

## GET /api/v1/customers

List customer profiles with filtering and search.

### Request
```http
GET /api/v1/customers?personality_type=D&budget_range=40k_60k&search=engineer&limit=20&offset=0
Authorization: Bearer <api_key>
```

### Response Success (200 OK)
```json
{
  "customers": [
    {
      "id": "customer-uuid-123",
      "name": "John Smith",
      "personality_type": "D",
      "budget_range": "40k_60k",
      "last_interaction": "2025-09-23T14:30:00Z",
      "interaction_count": 3,
      "current_interest": "2024 Toyota Camry Hybrid",
      "sales_stage": "presentation",
      "profile_completeness": 0.85
    }
  ],
  "total_count": 47,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

## GET /api/v1/customers/{id}

Retrieve detailed customer profile.

### Response Success (200 OK)
```json
{
  "id": "customer-uuid-123",
  "name": "John Smith",
  "demographics": {
    "age": 35,
    "profession": "Software Engineer",
    "location": "Seattle, WA"
  },
  "personality_profile": {
    "type": "D",
    "traits": {
      "dominant": 0.82,
      "influential": 0.34,
      "steady": 0.28,
      "conscientious": 0.61
    },
    "communication_style": "direct",
    "decision_making_style": "fast_analytical"
  },
  "interaction_history": [
    {
      "id": "interaction-uuid-1",
      "date": "2025-09-23T14:30:00Z",
      "type": "sales_call",
      "product_discussed": "2024 Toyota Camry Hybrid",
      "outcome": "interested",
      "next_steps": "Schedule test drive"
    }
  ],
  "recommendations_generated": 7,
  "average_recommendation_effectiveness": 4.1,
  "created_at": "2025-09-20T09:15:00Z",
  "last_updated": "2025-09-23T14:30:00Z"
}
```

## PUT /api/v1/customers/{id}

Update customer profile information.

### Request
```http
PUT /api/v1/customers/customer-uuid-123
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "demographics": {
    "age": 36,
    "profession": "Senior Software Engineer"
  },
  "decision_factors": {
    "primary": ["performance", "safety", "value", "technology"],
    "secondary": ["brand_reputation", "fuel_efficiency"]
  },
  "buying_context": {
    "budget_range": "45k_65k",
    "timeline": "within_2_months"
  }
}
```

### Response Success (200 OK)
```json
{
  "id": "customer-uuid-123",
  "updated_fields": ["demographics", "decision_factors", "buying_context"],
  "profile_completeness": 0.90,
  "last_updated": "2025-09-24T10:30:00Z",
  "changes_summary": {
    "budget_range": "40k_60k → 45k_65k",
    "timeline": "within_3_months → within_2_months",
    "new_decision_factor": "technology"
  }
}
```

## POST /api/v1/customers/{id}/interactions

Record a new customer interaction.

### Request
```http
POST /api/v1/customers/customer-uuid-123/interactions  
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "interaction_type": "sales_call|email|test_drive|showroom_visit",
  "date": "2025-09-24T10:30:00Z",
  "duration_minutes": 45,
  "products_discussed": ["2024 Toyota Camry Hybrid", "2024 Toyota Prius"],
  "customer_feedback": {
    "interest_level": "high",
    "primary_concerns": ["monthly_payment", "fuel_economy"],
    "positive_responses": ["safety_features", "hybrid_technology"]
  },
  "salesperson_notes": "Customer very interested in hybrid technology. Wants to compare monthly payment options.",
  "outcome": "scheduled_test_drive",
  "follow_up": {
    "required": true,
    "date": "2025-09-26T14:00:00Z",
    "type": "test_drive",
    "notes": "Focus on fuel economy demonstration"
  },
  "recommendation_id": "recommendation-uuid-456"
}
```

### Response Success (201 Created)
```json
{
  "interaction_id": "interaction-uuid-789",
  "customer_id": "customer-uuid-123", 
  "recorded_at": "2025-09-24T10:30:00Z",
  "profile_updates": {
    "interest_level": "increased",
    "new_concerns_identified": ["monthly_payment"],
    "sales_stage_progression": "presentation → negotiation"
  },
  "ai_insights": {
    "recommended_follow_up": "Prepare financing options comparison for test drive appointment",
    "personality_confirmation": "Direct communication style confirmed",
    "success_probability": 0.78
  }
}
```

## GET /api/v1/customers/{id}/interactions

Retrieve customer interaction history.

### Request
```http
GET /api/v1/customers/customer-uuid-123/interactions?limit=10&include_recommendations=true
Authorization: Bearer <api_key>
```

### Response Success (200 OK)
```json
{
  "customer_id": "customer-uuid-123",
  "interactions": [
    {
      "id": "interaction-uuid-789",
      "date": "2025-09-24T10:30:00Z",
      "type": "sales_call",
      "duration_minutes": 45,
      "outcome": "scheduled_test_drive",
      "effectiveness_rating": 4,
      "recommendation_used": {
        "id": "recommendation-uuid-456",
        "effectiveness": "high",
        "techniques_applied": ["social_proof", "technical_specs"]
      }
    }
  ],
  "interaction_summary": {
    "total_interactions": 4,
    "average_duration": 38,
    "progression": "prospecting → presentation → negotiation",
    "success_indicators": ["consistent_engagement", "follow_up_compliance"]
  }
}
```

## DELETE /api/v1/customers/{id}

Delete customer profile and associated data.

### Request
```http
DELETE /api/v1/customers/customer-uuid-123?data_retention_policy=anonymize
Authorization: Bearer <api_key>
```

### Response Success (204 No Content)
```http
HTTP/1.1 204 No Content
X-Data-Retention: anonymized
X-Related-Records-Updated: 12
```

---

## Error Handling

### Standard Error Response Format  
```json
{
  "error": "error_code",
  "message": "Human-readable error description",
  "details": {
    "additional_context": "value"
  },
  "timestamp": "2025-09-24T10:30:00Z",
  "request_id": "req-uuid"
}
```

### Common Error Codes
- `customer_not_found`: Customer ID doesn't exist
- `duplicate_customer`: Customer with same details already exists
- `validation_failed`: Request data validation errors
- `profile_incomplete`: Insufficient data for requested operation
- `interaction_conflict`: Interaction data conflicts with existing records
- `unauthorized_access`: API key lacks permissions for customer data

## Rate Limiting

- **Profile Operations**: 500 requests per hour per API key
- **Interaction Recording**: 1000 requests per hour per API key  
- **Bulk Operations**: 100 requests per hour per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 387
X-RateLimit-Reset: 1695556800
```