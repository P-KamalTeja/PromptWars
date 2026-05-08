# API Documentation

## Base URL
```
https://api.travelplanner.com/api/v1
http://localhost:8080/api/v1
```

## Authentication
Currently no authentication required. In production, implement:
- API Key headers
- JWT tokens
- OAuth 2.0

---

## Endpoints

### 🏥 Health Check

**GET** `/health`

Returns server status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### ✈️ Plan Trip

**POST** `/trips/plan`

Create a new travel itinerary.

**Request Body:**
```json
{
  "destination": "Paris",
  "start_date": "2024-06-01",
  "end_date": "2024-06-05",
  "budget": 2000,
  "currency": "USD",
  "travelers": 2,
  "traveler_type": "couple",
  "preferences": ["cultural", "adventure"],
  "interests": ["museums", "food", "art"],
  "accessibility_needs": "wheelchair accessible",
  "constraints": {
    "no_heights": true,
    "vegetarian": true
  }
}
```

**Response:** `201 Created`
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "destination": {
    "name": "Paris",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "country": "France"
  },
  "duration_days": 5,
  "total_cost": 2000,
  "confidence_score": 0.95,
  "daily_itineraries": [
    {
      "day_number": 1,
      "date": "2024-06-01",
      "activities": [...],
      "accommodation": "Hotel Le Marais",
      "accommodation_cost": 120,
      "total_cost": 350
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

### 📋 Get Trip

**GET** `/trips/{trip_id}`

Retrieve existing trip details.

**Path Parameters:**
- `trip_id` (string, required) - Unique trip identifier

**Response:** `200 OK`
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "destination": {...},
  "daily_itineraries": [...],
  "total_cost": 2000,
  "created_at": "2024-06-01T10:30:00Z",
  "updated_at": "2024-06-01T10:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Trip not found

---

### ✏️ Update Trip

**POST** `/trips/{trip_id}/update`

Modify an existing trip based on user feedback.

**Path Parameters:**
- `trip_id` (string, required) - Unique trip identifier

**Request Body:**
```json
{
  "update_request": "Add more museums, reduce budget to $1500, make it family-friendly"
}
```

**Response:** `200 OK`
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "destination": {...},
  "daily_itineraries": [...],
  "total_cost": 1500,
  "updated_at": "2024-06-01T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request
- `404 Not Found` - Trip not found
- `500 Internal Server Error` - Update failed

---

## Data Types

### TravelerType
- `solo` - Single traveler
- `couple` - Two travelers
- `family` - Family with children
- `group` - Large group

### Preferences
- `adventure` - Active adventures
- `luxury` - Premium experiences
- `budget` - Cost-conscious
- `cultural` - Cultural experiences
- `relaxation` - Leisurely pace
- `family` - Family-friendly

### Activity
```json
{
  "name": "Louvre Museum",
  "description": "World's largest art museum",
  "location": {
    "name": "Louvre, Paris",
    "latitude": 48.8606,
    "longitude": 2.3352,
    "country": "France"
  },
  "duration_hours": 3,
  "cost": 25,
  "category": "museum",
  "time_slot": "09:00-12:00",
  "accessibility_notes": "Wheelchair accessible",
  "rating": 4.8,
  "booking_url": "https://..."
}
```

---

## Error Codes

| Code | Message | Action |
|------|---------|--------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Provide API key |
| 404 | Not Found | Verify resource ID |
| 429 | Rate Limited | Wait before retrying |
| 500 | Server Error | Try again later |
| 502 | Bad Gateway | Google Services unavailable |

---

## Rate Limiting

- **Limit:** 100 requests per hour
- **Headers:** 
  - `X-RateLimit-Limit: 100`
  - `X-RateLimit-Remaining: 95`
  - `X-RateLimit-Reset: 1623456789`

---

## Examples

### cURL
```bash
# Plan trip
curl -X POST http://localhost:8080/api/v1/trips/plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "budget": 2000,
    "travelers": 2,
    "traveler_type": "couple",
    "preferences": ["cultural"],
    "interests": ["museums", "food"]
  }'

# Get trip
curl http://localhost:8080/api/v1/trips/550e8400-e29b-41d4-a716-446655440000

# Update trip
curl -X POST http://localhost:8080/api/v1/trips/550e8400-e29b-41d4-a716-446655440000/update \
  -H "Content-Type: application/json" \
  -d '{
    "update_request": "Add more museums"
  }'
```

### Python
```python
import requests

# Plan trip
response = requests.post(
    "http://localhost:8080/api/v1/trips/plan",
    json={
        "destination": "Paris",
        "start_date": "2024-06-01",
        "end_date": "2024-06-05",
        "budget": 2000,
        "travelers": 2,
        "traveler_type": "couple",
        "preferences": ["cultural"],
        "interests": ["museums", "food"]
    }
)
trip = response.json()
print(trip["trip_id"])
```

### JavaScript
```javascript
// Plan trip
const response = await fetch("/api/v1/trips/plan", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    destination: "Paris",
    start_date: "2024-06-01",
    end_date: "2024-06-05",
    budget: 2000,
    travelers: 2,
    traveler_type: "couple",
    preferences: ["cultural"],
    interests: ["museums", "food"]
  })
});

const trip = await response.json();
console.log(trip.trip_id);
```

---

## Webhooks (Future)

Subscribe to trip events:
```json
{
  "event": "trip.created",
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-06-01T10:30:00Z"
}
```

---

**API Version:** 1.0.0  
**Last Updated:** June 2024
