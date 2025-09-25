# API Contract: Knowledge Management

**Endpoint**: `/api/v1/knowledge`  
**Purpose**: Manage knowledge sources and content ingestion  
**Authentication**: API Key required

## POST /api/v1/knowledge/sources

Upload and process new knowledge source (book, manual, document).

### Request
```http
POST /api/v1/knowledge/sources
Content-Type: multipart/form-data
Authorization: Bearer <api_key>

{
  "file": "<binary_file_data>",
  "title": "The Psychology of Selling",
  "author": "Brian Tracy", 
  "type": "psychology|technical|communication",
  "version": "2nd Edition",
  "metadata": {
    "publication_year": 2004,
    "page_count": 288,
    "language": "en"
  }
}
```

### Response Success (201 Created)
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "The Psychology of Selling",
  "author": "Brian Tracy",
  "type": "psychology",
  "processing_status": "queued",
  "created_at": "2025-09-24T10:30:00Z",
  "estimated_processing_time": "5-10 minutes"
}
```

### Response Error (400 Bad Request)
```json
{
  "error": "validation_failed",
  "message": "Invalid file type. Only PDF, TXT, and DOCX files are supported.",
  "details": {
    "field": "file",
    "supported_formats": ["pdf", "txt", "docx"]
  }
}
```

## GET /api/v1/knowledge/sources

List all knowledge sources with processing status.

### Request
```http
GET /api/v1/knowledge/sources?type=psychology&status=processed&limit=20&offset=0
Authorization: Bearer <api_key>
```

### Response Success (200 OK)
```json
{
  "sources": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "The Psychology of Selling",
      "author": "Brian Tracy",
      "type": "psychology",
      "processing_status": "processed",
      "concept_count": 127,
      "processed_at": "2025-09-24T10:35:00Z",
      "file_size": "2.4 MB"
    }
  ],
  "total_count": 3,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

## GET /api/v1/knowledge/sources/{id}/concepts

Retrieve extracted concepts from a specific knowledge source.

### Request
```http
GET /api/v1/knowledge/sources/123e4567-e89b-12d3-a456-426614174000/concepts?limit=50&search=social_proof
Authorization: Bearer <api_key>
```

### Response Success (200 OK)
```json
{
  "concepts": [
    {
      "id": "concept-uuid-1",
      "title": "Social Proof Principle",
      "concept_type": "persuasion_principle",
      "content": "People follow the lead of similar others. When uncertain about a decision, they look to the behavior and choices of people like themselves.",
      "keywords": ["social_proof", "conformity", "peer_influence", "testimonials"],
      "page_reference": "Chapter 4, pages 67-72",
      "confidence_score": 0.95
    }
  ],
  "total_count": 8,
  "source_info": {
    "title": "The Psychology of Selling",
    "author": "Brian Tracy"
  }
}
```

## DELETE /api/v1/knowledge/sources/{id}

Remove a knowledge source and all associated concepts.

### Request
```http
DELETE /api/v1/knowledge/sources/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <api_key>
```

### Response Success (204 No Content)
```http
HTTP/1.1 204 No Content
```

### Response Error (409 Conflict)
```json
{
  "error": "source_in_use",
  "message": "Cannot delete knowledge source that has been referenced in recommendations.",
  "details": {
    "recommendation_count": 15,
    "last_used": "2025-09-24T09:45:00Z"
  }
}
```

## POST /api/v1/knowledge/search

Semantic search across all knowledge sources.

### Request
```http
POST /api/v1/knowledge/search
Content-Type: application/json
Authorization: Bearer <api_key>

{
  "query": "handling price objections in car sales",
  "source_types": ["psychology", "communication"],
  "limit": 10,
  "similarity_threshold": 0.7
}
```

### Response Success (200 OK)
```json
{
  "results": [
    {
      "concept_id": "concept-uuid-1",
      "title": "Price Anchoring Technique",
      "content": "Present the highest-priced option first to make subsequent options appear more reasonable by comparison...",
      "source": {
        "title": "The Psychology of Selling",
        "author": "Brian Tracy",
        "type": "psychology"
      },
      "similarity_score": 0.89,
      "page_reference": "Chapter 8, p. 142"
    }
  ],
  "query_processing_time": "0.15s",
  "total_results": 7
}
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
- `validation_failed`: Request data validation errors
- `source_not_found`: Knowledge source ID doesn't exist
- `processing_failed`: Document processing encountered errors
- `unsupported_format`: File format not supported
- `quota_exceeded`: API usage limits exceeded
- `source_in_use`: Cannot delete source referenced elsewhere

## Rate Limiting

- **File Uploads**: 5 uploads per hour per API key
- **Search Requests**: 1000 requests per hour per API key
- **List/Read Operations**: 5000 requests per hour per API key

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1695556800
```