# Country Currency & Exchange API

A Django REST API that fetches country data from external APIs, stores it in MySQL, and provides CRUD operations with GDP calculations.

## Features

- Fetch country data from REST Countries API
- Get exchange rates from Open Exchange Rates API
- Calculate estimated GDP based on population and exchange rates
- CRUD operations for country data
- Filtering and sorting capabilities
- Summary image generation
- MySQL database integration

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL 5.7+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd country_api